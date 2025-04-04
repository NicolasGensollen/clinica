from pathlib import Path
from typing import Callable, Iterator, Optional, Union

import numpy as np
import pandas as pd

from clinica.converters.study_models import StudyName, bids_id_factory

__all__ = [
    "create_participants_tsv_file",
    "create_scans_tsv_file",
    "create_sessions_tsv_file",
]


def create_participants_tsv_file(
    bids_path: Path,
    clinical_specifications_folder: Path,
    clinical_data_dir: Path,
    delete_non_bids_info: bool = True,
) -> None:
    """Create a participants TSV file for the AIBL dataset where information
    regarding the patients are reported.

    Parameters
    ----------
    bids_path : Path
        The path to the BIDS directory.

    clinical_specifications_folder : Path
        The path to the folder containing the clinical specification files.

    clinical_data_dir : Path
        The path to the directory to the clinical data files.

    delete_non_bids_info : bool, optional
        If True delete all the rows of the subjects that are not
        available in the BIDS dataset.
        Default=True.
    """
    from clinica.utils.stream import cprint

    study = StudyName.AIBL
    prev_location = ""

    specifications = _load_specifications(
        clinical_specifications_folder, "participant.tsv"
    )[[study.value, f"{study.value} location", "BIDS CLINICA"]].dropna()

    participant_df = pd.DataFrame()
    for _, row in specifications.iterrows():
        if (location := row[f"{study.value} location"]) != prev_location:
            file_to_read = _load_metadata_from_pattern(clinical_data_dir, location)
            prev_location = location
        participant_df[row["BIDS CLINICA"]] = file_to_read[row[study.value]].astype(str)

    # Compute BIDS-compatible participant ID.
    participant_df.insert(
        0,
        "participant_id",
        participant_df["alternative_id_1"].apply(
            lambda x: bids_id_factory(StudyName.AIBL).from_original_study_id(x)
        ),
    )
    participant_df.drop(labels="alternative_id_1", axis=1, inplace=True)

    # Keep year-of-birth only.
    participant_df["date_of_birth"] = participant_df["date_of_birth"].str.extract(
        r"/(\d{4}).*"
    )
    # Normalize sex value.
    participant_df["sex"] = participant_df["sex"].map({"1": "M", "2": "F"})
    # Normalize known NA values.
    participant_df.fillna("n/a", inplace=True)
    participant_df.replace("-4", "n/a", inplace=True)

    # Delete all the rows of the subjects that are not available in the BIDS dataset
    if delete_non_bids_info:
        subjects_to_keep = [d.name for d in bids_path.glob("sub-*")]
        participant_df.set_index("participant_id", inplace=True, drop=False)
        for subject in subjects_to_keep:
            if subject not in participant_df.index:
                cprint(
                    f"No clinical data was found for participant {subject}.",
                    lvl="warning",
                )
                participant_df.loc[subject] = "n/a"
                participant_df.loc[subject, "participant_id"] = subject
        participant_df = participant_df.loc[subjects_to_keep]

    participant_df.to_csv(
        bids_path / "participants.tsv",
        sep="\t",
        index=False,
        encoding="utf8",
    )


def _load_specifications(
    clinical_specifications_folder: Path, filename: str
) -> pd.DataFrame:
    specifications = clinical_specifications_folder / filename
    if not specifications.exists():
        raise FileNotFoundError(
            f"The specifications for {filename} were not found. "
            f"The should be located in {specifications}."
        )
    return pd.read_csv(specifications, sep="\t")


def _load_metadata_from_pattern(
    clinical_dir: Path,
    pattern: str,
    on_bad_lines: Optional[Union[str, Callable]] = "error",
) -> pd.DataFrame:
    try:
        return pd.read_csv(
            next(clinical_dir.glob(pattern)),
            dtype={"text": str},
            sep=",",
            engine="python",
            on_bad_lines=on_bad_lines,
        )
    except StopIteration:
        raise FileNotFoundError(
            f"Clinical data file corresponding to pattern {pattern} was not found in folder "
            f"{clinical_dir}"
        )


def _map_diagnosis(diagnosis: int) -> str:
    if diagnosis == 1:
        return "CN"
    elif diagnosis == 2:
        return "MCI"
    elif diagnosis == 3:
        return "AD"
    else:
        return "n/a"


def _format_metadata_for_rid(
    input_df: pd.DataFrame, source_id: int, bids_metadata: str, source_metadata: str
) -> pd.DataFrame:
    from ..._utils import viscode_to_session

    extract = input_df.loc[(input_df["RID"] == source_id), ["VISCODE", source_metadata]]
    extract.rename(columns={source_metadata: bids_metadata}, inplace=True)
    extract = extract.assign(
        session_id=extract.VISCODE.apply(lambda x: viscode_to_session(x))
    )
    extract.drop(labels="VISCODE", inplace=True, axis=1)
    extract.set_index("session_id", inplace=True, drop=True)

    return extract


def _compute_age_at_exam(
    birth_date: Optional[str], exam_date: Optional[str]
) -> Optional[int]:
    from datetime import datetime

    if birth_date and exam_date:
        date_of_birth = datetime.strptime(birth_date, "/%Y")
        exam_date = datetime.strptime(exam_date, "%m/%d/%Y")
        return exam_date.year - date_of_birth.year
    return None


def _set_age_from_birth(df: pd.DataFrame) -> pd.DataFrame:
    if "date_of_birth" not in df.columns or "examination_date" not in df.columns:
        raise ValueError(
            "Columns date_of_birth or/and examination_date were not found in the sessions metadata dataframe."
            "Please check your study metadata."
        )
    if len(df["date_of_birth"].dropna().unique()) <= 1:
        df["date_of_birth"] = df["date_of_birth"].ffill()
        df["age"] = df.apply(
            lambda x: _compute_age_at_exam(x.date_of_birth, x.examination_date), axis=1
        )
    else:
        df["age"] = None
    return df.drop(labels="date_of_birth", axis=1)


def create_sessions_tsv_file(
    bids_dir: Path,
    clinical_data_dir: Path,
    clinical_specifications_folder: Path,
) -> None:
    """Extract the information regarding a subject sessions and save them in a tsv file.

    Parameters
    ----------
    bids_dir : Path
        The path to the BIDS directory.

    clinical_data_dir : Path
        The path to the directory to the clinical data files.

    clinical_specifications_folder : Path
        The path to the folder containing the clinical specification files.
    """
    from clinica.dataset import (
        get_sessions_for_subject_in_bids_dataset,
        get_subjects_from_bids_dataset,
    )

    study = StudyName.AIBL.value
    specifications = _load_specifications(
        clinical_specifications_folder, "sessions.tsv"
    )[["BIDS CLINICA", f"{study} location", study]].dropna()

    for bids_id in get_subjects_from_bids_dataset(bids_dir):
        rid = int(bids_id_factory(study)(bids_id).to_original_study_id())
        sessions = pd.DataFrame(
            {"session_id": get_sessions_for_subject_in_bids_dataset(bids_dir, bids_id)}
        ).set_index("session_id", drop=False)

        for _, row in specifications.iterrows():
            df = _load_metadata_from_pattern(
                clinical_data_dir, row[f"{study} location"]
            )
            data = _format_metadata_for_rid(
                input_df=df,
                source_id=rid,
                bids_metadata=row["BIDS CLINICA"],
                source_metadata=row[study],
            )
            sessions = pd.concat([sessions, data], axis=1)

        sessions.sort_index(inplace=True)

        # -4 are considered missing values in AIBL
        sessions.replace([-4, "-4", np.nan], None, inplace=True)
        sessions["diagnosis"] = sessions.diagnosis.apply(lambda x: _map_diagnosis(x))
        sessions["examination_date"] = sessions.apply(
            lambda x: _complete_examination_dates(
                rid, clinical_data_dir, x.session_id, x.examination_date
            ),
            axis=1,
        )
        sessions = _set_age_from_birth(sessions)

        # in case there is a session in clinical data that was not actually converted
        sessions.dropna(subset=["session_id"], inplace=True)
        sessions.fillna("n/a", inplace=True)

        bids_id = bids_id_factory(StudyName.AIBL).from_original_study_id(str(rid))
        sessions.to_csv(
            bids_dir / bids_id / f"{bids_id}_sessions.tsv",
            sep="\t",
            index=False,
            encoding="utf8",
        )


def _complete_examination_dates(
    rid: int,
    clinical_data_dir: Path,
    session_id: Optional[str] = None,
    examination_date: Optional[str] = None,
) -> Optional[str]:
    if examination_date:
        return examination_date
    if session_id:
        return _find_exam_date_in_other_csv_files(rid, session_id, clinical_data_dir)
    return None


def _find_exam_date_in_other_csv_files(
    rid: int, session_id: str, clinical_data_dir: Path
) -> Optional[str]:
    """Try to find an alternative exam date by searching in other CSV files."""
    from ..._utils import viscode_to_session

    for csv in _get_csv_files_for_alternative_exam_date(clinical_data_dir):
        csv_data = pd.read_csv(csv, low_memory=False)
        csv_data["SESSION"] = csv_data.VISCODE.apply(lambda x: viscode_to_session(x))
        exam_date = csv_data[(csv_data.RID == rid) & (csv_data.SESSION == session_id)]
        if not exam_date.empty and exam_date.iloc[0].EXAMDATE != "-4":
            return exam_date.iloc[0].EXAMDATE
    return None


def _get_csv_files_for_alternative_exam_date(
    clinical_data_dir: Path,
) -> Iterator[Path]:
    """Return a list of paths to CSV files in which an alternative exam date could be found."""

    for pattern in (
        "aibl_mri3meta_*.csv",
        "aibl_mrimeta_*.csv",
        "aibl_cdr_*.csv",
        "aibl_flutemeta_*.csv",
        "aibl_mmse_*.csv",
        "aibl_pibmeta_*.csv",
    ):
        try:
            yield next(clinical_data_dir.glob(pattern))
        except StopIteration:
            continue


def create_scans_tsv_file(
    bids_path: Path,
    clinical_data_dir: Path,
    clinical_specifications_folder: Path,
) -> None:
    """Create scans.tsv files for AIBL.

    Parameters
    ----------
    bids_path : Path
        The path to the BIDS folder.

    clinical_data_dir : Path
        The path to the directory to the clinical data files.

    clinical_specifications_folder : Path
        The path to the folder containing the clinical specification files.
    """

    scans_dict = _create_scans_dict(
        clinical_data_dir,
        clinical_specifications_folder,
        bids_path,
    )
    _write_scans_tsv(bids_path, scans_dict)


def _handle_flutemeta_badline(line: list[str]) -> Optional[list[str]]:
    """
    Fix for malformed flutemeta file in AIBL (see #796).
    Some flutemeta lines contain a non-coded string value at the second-to-last position. This value
    contains a comma which adds an extra column and shifts the remaining values to the right. In this
    case, we just remove the erroneous content and replace it with -4 which AIBL uses as n/a value.

    Example : bad_line = ['618', '1', 'm18', ... , '1', 'measured', 'AUSTIN AC CT Brain  H19s', '0']
    """

    if line[-3] == "measured" and line[-2] == "AUSTIN AC CT Brain  H19s":
        return line[:-3] + ["-4", line[-1]]


def _init_scans_dict(bids_path: Path) -> dict:
    from clinica.utils.pet import Tracer

    bids_ids = (
        sub_path.name
        for sub_path in bids_path.rglob("./sub-AIBL*")
        if sub_path.is_dir()
    )

    scans_dict = {}
    for bids_id in bids_ids:
        scans_dict[bids_id] = dict()
        ses_list = (
            ses_path.name
            for ses_path in (bids_path / bids_id).rglob("ses-M*")
            if ses_path.is_dir()
        )
        for session in ses_list:
            scans_dict[bids_id][session] = {
                "T1/DWI/fMRI/FMAP": {},
                Tracer.PIB: {},
                Tracer.AV45: {},
                Tracer.FMM: {},
            }
    return scans_dict


def _format_time(time: str) -> str:
    import datetime

    date_obj = datetime.datetime.strptime(time, "%m/%d/%Y")
    return date_obj.strftime("%Y-%m-%dT%H:%M:%S")


def _create_scans_dict(
    clinical_data_dir: Path,
    clinical_specifications_folder: Path,
    bids_path: Path,
) -> dict:
    """Create a dictionary containing metadata per subject/session to write in scans.tsv.

    Parameters
    ----------
    clinical_data_dir : Path
        The path to the directory where the clinical data are stored.

    clinical_specifications_folder : Path
        The path to the folder containing the clinical specification files.

    bids_path: Path
        The path to the BIDS directory.

    Returns
    -------
    pd.DataFrame :
        A pandas DataFrame that contains the scans information for all sessions of all participants.
    """
    from ..._utils import viscode_to_session

    scans_dict = _init_scans_dict(bids_path)

    study = StudyName.AIBL.value

    scans_specs = _load_specifications(clinical_specifications_folder, "scans.tsv")[
        [study, f"{study} location", "BIDS CLINICA", "Modalities related"]
    ].dropna()

    for _, row in scans_specs.iterrows():
        on_bad_lines = (
            _handle_flutemeta_badline
            if "flutemeta" in row[f"{study} location"]
            else "error"
        )
        file = _load_metadata_from_pattern(
            clinical_data_dir, row[f"{study} location"], on_bad_lines
        )
        file["session_id"] = file["VISCODE"].apply(lambda x: viscode_to_session(x))

        for bids_id in scans_dict.keys():
            original_id = bids_id_factory(StudyName.AIBL)(
                bids_id
            ).to_original_study_id()
            for session in scans_dict[bids_id].keys():
                try:
                    value = file[
                        (file["RID"] == int(original_id))
                        & (file["session_id"] == session)
                    ][row[study]].item()
                    if value == "-4":
                        value = "n/a"
                    elif row["BIDS CLINICA"] == "acq_time":
                        value = _format_time(value)
                except ValueError:
                    value = "n/a"

                modality = scans_dict[bids_id][session][row["Modalities related"]]

                # Avoid writing over in case of modality "T1/..." because it is used twice
                if (row["BIDS CLINICA"] not in modality) or (
                    modality[row["BIDS CLINICA"]] == "n/a"
                ):
                    modality[row["BIDS CLINICA"]] = value
    return scans_dict


def _write_scans_tsv(bids_dir: Path, scans_dict: dict) -> None:
    """Write the scans dict into TSV files.

    Parameters
    ----------
    bids_dir : Path
        The path to the BIDS directory.

    scans_dict : dict
        Dictionary containing scans metadata.

        .. note::
            This is the output of the function
            `clinica.iotools.bids_utils.create_scans_dict`.

    See also
    --------
    write_sessions_tsv
    """
    from clinica.utils.pet import get_pet_tracer_from_filename

    supported_modalities = ("anat", "dwi", "func", "pet")

    for subject in scans_dict:
        for session in scans_dict[subject]:
            scans_df = pd.DataFrame()
            tsv_file = bids_dir / subject / session / f"{subject}_{session}_scans.tsv"
            tsv_file.unlink(missing_ok=True)
            for modality in [
                mod
                for mod in (bids_dir / subject / session).glob("*")
                if mod.name in supported_modalities
            ]:
                for file in [
                    file for file in modality.iterdir() if modality.suffix != ".json"
                ]:
                    f_type = (
                        "T1/DWI/fMRI/FMAP"
                        if modality.name in ("anat", "dwi", "func")
                        else get_pet_tracer_from_filename(file.name).value
                    )
                    row_to_append = pd.DataFrame(
                        scans_dict[subject][session][f_type], index=[0]
                    )
                    row_to_append.insert(
                        0, "filename", f"{modality.name} / {file.name}"
                    )
                    scans_df = pd.concat([scans_df, row_to_append])
                scans_df = scans_df.fillna("n/a")
                scans_df.to_csv(tsv_file, sep="\t", encoding="utf8", index=False)
