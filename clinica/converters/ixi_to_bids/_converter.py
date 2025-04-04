"""Convert IXI dataset (https://brain-development.org/ixi-dataset/) to BIDS."""

from typing import Optional

from clinica.converters._utils import write_modality_agnostic_files
from clinica.utils.filemanip import UserProvidedPath

from ._utils import (
    check_modalities,
    define_participants,
    read_clinical_data,
    write_dwi_b_values,
    write_participants,
    write_scans,
    write_sessions,
    write_subject_data,
)

__all__ = ["convert"]


def convert(
    path_to_dataset: UserProvidedPath,
    bids_dir: UserProvidedPath,
    path_to_clinical: UserProvidedPath,
    subjects: Optional[UserProvidedPath] = None,
    n_procs: Optional[int] = 1,
    **kwargs,
):
    from clinica.converters.factory import get_converter_name
    from clinica.converters.study_models import StudyName
    from clinica.utils.stream import cprint

    from .._utils import validate_input_path

    path_to_dataset = validate_input_path(path_to_dataset)
    bids_dir = validate_input_path(bids_dir, check_exist=False)
    path_to_clinical = validate_input_path(path_to_clinical)
    if subjects:
        subjects = validate_input_path(subjects)

    if n_procs != 1:
        cprint(
            f"{get_converter_name(StudyName.IXI)} converter does not support multiprocessing yet. n_procs set to 1.",
            lvl="warning",
        )

    clinical_data = read_clinical_data(path_to_clinical)
    participants = define_participants(path_to_dataset, subjects)
    check_modalities(data_directory=path_to_dataset, participants=participants)

    write_participants(
        bids_dir=bids_dir, clinical_data=clinical_data, participants=participants
    )

    for participant in participants:
        cprint(f"Converting IXI subject {participant} to BIDS", lvl="debug")
        write_subject_data(
            bids_dir=bids_dir, participant=participant, path_to_dataset=path_to_dataset
        )
        write_sessions(
            bids_dir=bids_dir, participant=participant, clinical_data=clinical_data
        )
        write_scans(bids_dir=bids_dir, participant=participant)

    if list(bids_dir.rglob("dwi")):
        write_dwi_b_values(bids_dir=bids_dir)

    readme_data = {
        "link": "https://brain-development.org/ixi-dataset/",
        "desc": (
            "IXI is the nickname for the Information eXtraction from Images project, "
            "which issued a dataset of nearly 600 images from healthy subjects. The MR"
            "acquisition protocol includes T1,T2, PD weighted, MRA and diffusion-weighted"
            "images. Three hospitals in London were involved in data collection."
        ),
    }

    write_modality_agnostic_files(
        study_name=StudyName.IXI, readme_data=readme_data, bids_dir=bids_dir
    )

    cprint("Conversion to BIDS finished.", lvl="info")
