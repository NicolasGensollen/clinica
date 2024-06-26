def get_substitutions_datasink_flair(bids_image_id: str) -> list:
    from clinica.pipelines.t1_linear.anat_linear_utils import (  # noqa
        _get_substitutions_datasink,
    )

    return _get_substitutions_datasink(bids_image_id, "FLAIR")


def get_substitutions_datasink_t1_linear(bids_image_id: str) -> list:
    from clinica.pipelines.t1_linear.anat_linear_utils import (  # noqa
        _get_substitutions_datasink,
    )

    return _get_substitutions_datasink(bids_image_id, "T1w")


def _get_substitutions_datasink(bids_image_id: str, suffix: str) -> list:
    """Return file name substitutions for renaming.

    Parameters
    ----------
    bids_image_id : str
        This is the original image BIDS file name without the extension.
        This will be used to get all the BIDS entities that shouldn't
        be modified (subject, session...).

    suffix : str
        The suffix to use for the new file.

    Returns
    -------
    substitutions : List of tuples of str
        List of length 3 containing the substitutions to perform.
    """
    if bids_image_id.endswith(f"_{suffix}"):
        bids_image_id_without_suffix = bids_image_id.removesuffix(f"_{suffix}")
    else:
        raise ValueError(
            f"bids image ID {bids_image_id} should end with provided {suffix}."
        )
    return [
        (
            f"{bids_image_id}Warped_cropped.nii.gz",
            f"{bids_image_id_without_suffix}_space-MNI152NLin2009cSym_desc-Crop_res-1x1x1_{suffix}.nii.gz",
        ),
        (
            f"{bids_image_id}0GenericAffine.mat",
            f"{bids_image_id_without_suffix}_space-MNI152NLin2009cSym_res-1x1x1_affine.mat",
        ),
        (
            f"{bids_image_id}Warped.nii.gz",
            f"{bids_image_id_without_suffix}_space-MNI152NLin2009cSym_res-1x1x1_{suffix}.nii.gz",
        ),
    ]


def print_end_pipeline(anat, final_file):
    """Display end message for <subject_id> when <final_file> is connected."""
    from clinica.utils.filemanip import get_subject_id
    from clinica.utils.ux import print_end_image

    print_end_image(get_subject_id(anat))
