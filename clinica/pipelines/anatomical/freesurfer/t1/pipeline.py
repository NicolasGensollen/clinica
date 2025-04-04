from pathlib import Path
from typing import List

from nipype import config

from clinica.pipelines.engine import Pipeline

cfg = dict(execution={"parameterize_dirs": False})
config.update_config(cfg)


class T1FreeSurfer(Pipeline):
    """FreeSurfer-based processing of T1-weighted MR images.

    Returns:
        A clinica pipeline object containing the T1FreeSurfer pipeline.
    """

    @staticmethod
    def get_processed_images(
        caps_directory: Path, subjects: List[str], sessions: List[str]
    ) -> List[str]:
        from clinica.utils.filemanip import extract_image_ids
        from clinica.utils.input_files import T1_FS_DESTRIEUX
        from clinica.utils.inputs import clinica_file_reader

        image_ids: List[str] = []
        if caps_directory.is_dir():
            t1_freesurfer_files, _ = clinica_file_reader(
                subjects, sessions, caps_directory, T1_FS_DESTRIEUX
            )
            image_ids = extract_image_ids(t1_freesurfer_files)
        return image_ids

    def _check_pipeline_parameters(self) -> None:
        """Check pipeline parameters."""
        from clinica.utils.stream import cprint

        if "-dontrun" in self.parameters["recon_all_args"].split(" "):
            cprint(
                msg=(
                    "Found -dontrun flag for FreeSurfer recon-all. "
                    "Please note that this will not run the segmentation."
                ),
                lvl="warning",
            )

    def _check_custom_dependencies(self) -> None:
        """Check dependencies that can not be listed in the `info.json` file."""
        pass

    def get_input_fields(self) -> List[str]:
        """Specify the list of possible inputs of this pipeline.

        Notes
        -----
        The list of inputs of the T1FreeSurfer pipeline is:
            * t1w (str): Path of the T1 weighted image in BIDS format

        Returns
        -------
        list of str :
            A list of (string) input fields name.
        """
        return ["t1w"]

    def get_output_fields(self) -> List[str]:
        """Specify the list of possible outputs of this pipeline.

        Notes
        -----
        The list of outputs of the T1FreeSurfer pipeline is:
            * image_id (str): Image ID (e.g. sub-CLNC01_ses-M000)

        Returns
        -------
        list of str :
            A list of (string) output fields name.
        """
        return ["image_id"]

    def _build_input_node(self):
        """Build and connect an input node to the pipeline.

        Raise:
            ClinicaBIDSError: If there are duplicated files or missing files for any subject
        """
        import nipype.interfaces.utility as nutil
        import nipype.pipeline.engine as npe

        from clinica.iotools.data_handling import (
            are_images_centered_around_origin_of_world_coordinate_system,
        )
        from clinica.utils.exceptions import ClinicaException
        from clinica.utils.filemanip import (
            extract_subjects_sessions_from_filename,
            save_participants_sessions,
        )
        from clinica.utils.input_files import T1W_NII
        from clinica.utils.inputs import clinica_file_filter
        from clinica.utils.stream import cprint
        from clinica.utils.ux import print_images_to_process

        processed_ids = self.get_processed_images(
            self.caps_directory, self.subjects, self.sessions
        )
        if len(processed_ids) > 0:
            cprint(
                msg=(
                    f"Clinica found {len(processed_ids)} image(s) "
                    "already processed in CAPS directory:"
                ),
                lvl="warning",
            )
            for image_id in processed_ids:
                cprint(msg=f"{image_id.replace('_', ' | ')}", lvl="warning")
            if self.overwrite_caps:
                output_folder = "<CAPS>/subjects/<participant_id>/<session_id>/t1/freesurfer_cross_sectional"
                cprint(
                    msg=f"Output folders in {output_folder} will be recreated.",
                    lvl="warning",
                )
            else:
                cprint(msg="Image(s) will be ignored by Clinica.", lvl="warning")
                input_ids = [
                    f"{p_id}_{s_id}" for p_id, s_id in zip(self.subjects, self.sessions)
                ]
                to_process_ids = list(set(input_ids) - set(processed_ids))
                self.subjects, self.sessions = extract_subjects_sessions_from_filename(
                    to_process_ids
                )

        t1w_files, self.subjects, self.sessions = clinica_file_filter(
            self.subjects, self.sessions, self.bids_directory, T1W_NII
        )

        if not t1w_files:
            raise ClinicaException("Empty dataset or already processed")

        save_participants_sessions(
            self.subjects, self.sessions, self.base_dir / self.name
        )
        if len(self.subjects):
            print_images_to_process(self.subjects, self.sessions)
            cprint(
                f"List available in {self.base_dir / self.name / 'participants.tsv'}"
            )
            cprint("The pipeline will last approximately 10 hours per image.")

        read_node = npe.Node(
            name="ReadingFiles",
            iterables=[
                ("t1w", t1w_files),
            ],
            synchronize=True,
            interface=nutil.IdentityInterface(fields=self.get_input_fields()),
        )
        are_images_centered_around_origin_of_world_coordinate_system(
            [Path(f) for f in t1w_files],
            self.bids_directory,
        )

        self.connect(
            [
                (read_node, self.input_node, [("t1w", "t1w")]),
            ]
        )

    def _build_output_node(self):
        """Build and connect an output node to the pipeline."""
        import nipype.interfaces.utility as nutil
        import nipype.pipeline.engine as npe

        from .tasks import save_to_caps_task

        save_to_caps = npe.Node(
            interface=nutil.Function(
                input_names=["source_dir", "image_id", "caps_dir", "overwrite_caps"],
                output_names=["image_id"],
                function=save_to_caps_task,
            ),
            name="SaveToCaps",
        )
        save_to_caps.inputs.source_dir = str(self.base_dir / self.name / "ReconAll")
        save_to_caps.inputs.caps_dir = str(self.caps_directory)
        save_to_caps.inputs.overwrite_caps = self.overwrite_caps

        self.connect(
            [
                (self.output_node, save_to_caps, [("image_id", "image_id")]),
            ]
        )

    def _build_core_nodes(self):
        """Build and connect the core nodes of the pipeline."""
        import nipype.interfaces.utility as nutil
        import nipype.pipeline.engine as npe
        from nipype.interfaces.freesurfer.preprocess import ReconAll

        from .tasks import init_input_node_task, write_tsv_files_task

        # Nodes declaration
        # =================
        # Initialize the pipeline
        #   - Extract <image_id> (e.g. sub-CLNC01_ses-M000) T1w filename;
        #   - Check FOV of T1w;
        #   - Create <subjects_dir> folder in <WD>/<Pipeline.name>/ReconAll/<image_id>/;
        #   - Print begin execution message.
        init_input = npe.Node(
            interface=nutil.Function(
                input_names=["t1w", "recon_all_args", "output_dir"],
                output_names=["image_id", "t1w", "flags", "subjects_dir"],
                function=init_input_node_task,
            ),
            name="0-InitPipeline",
        )
        init_input.inputs.recon_all_args = self.parameters["recon_all_args"]
        init_input.inputs.output_dir = str(self.base_dir / self.name / "ReconAll")

        # Run recon-all command
        # FreeSurfer segmentation will be in <subjects_dir>/<image_id>/
        recon_all = npe.Node(interface=ReconAll(), name="1-SegmentationReconAll")
        recon_all.inputs.directive = "all"

        # Generate TSV files containing a summary of the regional statistics
        # in <subjects_dir>/regional_measures
        create_tsv = npe.Node(
            interface=nutil.Function(
                input_names=["subjects_dir", "image_id"],
                output_names=["image_id"],
                function=write_tsv_files_task,
            ),
            name="2-CreateTsvFiles",
        )
        connections = [
            (self.input_node, init_input, [("t1w", "t1w")]),
            (
                init_input,
                recon_all,
                [
                    ("subjects_dir", "subjects_dir"),
                    ("t1w", "T1_files"),
                    ("image_id", "subject_id"),
                    ("flags", "flags"),
                ],
            ),
            (init_input, create_tsv, [("subjects_dir", "subjects_dir")]),
            (recon_all, create_tsv, [("subject_id", "image_id")]),
            (create_tsv, self.output_node, [("image_id", "image_id")]),
        ]
        self.connect(connections)
