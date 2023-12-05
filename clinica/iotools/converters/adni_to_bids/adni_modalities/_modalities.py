from enum import Enum


class ADNIModality(str, Enum):
    """Modalities supported by the converter."""

    T1 = "T1"
    DWI = "DWI"
    FLAIR = "FLAIR"
    FMRI = "fMRI"
    PET_FDG = "PET_FDG"
    PET_FDG_UNIFORM = "PET_FDG_UNIFORM"
    PET_PIB = "PET_PIB"
    PET_AV45 = "PET_AV45"
    PET_FBB = "PET_FBB"
    PET_TAU = "PET_TAU"
