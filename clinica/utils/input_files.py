"""This module contains dictionaries used in inputs.py::clinica_{file|group}_reader().

These dictionaries describe files to grab.
"""

import functools
from collections.abc import Iterable
from typing import Optional, Union

from clinica.utils.dwi import DTIBasedMeasure
from clinica.utils.pet import ReconstructionMethod, SUVRReferenceRegion, Tracer

# BIDS

T1W_NII = {"pattern": "sub-*_ses-*_t1w.nii*", "description": "T1w MRI"}
Flair_T2W_NII = {"pattern": "sub-*_ses-*_flair.nii*", "description": "FLAIR T2w MRI"}

# T1-FreeSurfer

T1_FS_WM = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/mri/wm.seg.mgz",
    "description": "segmentation of white matter (mri/wm.seg.mgz).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_BRAIN = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/mri/brain.mgz",
    "description": " extracted brain from T1w MRI (mri/brain.mgz).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_ORIG_NU = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/mri/orig_nu.mgz",
    "description": "intensity normalized volume generated after correction for"
    " non-uniformity in FreeSurfer (mri/orig_nu.mgz).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_LONG_ORIG_NU = {
    "pattern": "t1/long-*/freesurfer_longitudinal/sub-*_ses-*.long.sub-*_*/mri/orig_nu.mgz",
    "description": "intensity normalized volume generated after correction for non-uniformity in FreeSurfer (orig_nu.mgz) in longitudinal",
    "needed_pipeline": "t1-freesurfer and t1-freesurfer longitudinal",
}

T1_FS_WM_SURF_R = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/surf/rh.white",
    "description": "right white matter/gray matter border surface (rh.white).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_LONG_SURF_R = {
    "pattern": "t1/long-*/freesurfer_longitudinal/sub-*_ses-*.long.sub-*_*/surf/rh.white",
    "description": "right white matter/gray matter border surface (rh.white) generated with t1-freesurfer-longitudinal.",
    "needed_pipeline": "t1-freesurfer and t1-freesurfer longitudinal",
}

T1_FS_LONG_SURF_L = {
    "pattern": "t1/long-*/freesurfer_longitudinal/sub-*_ses-*.long.sub-*_*/surf/lh.white",
    "description": "left white matter/gray matter border surface (lh.white) generated with t1-freesurfer-longitudinal.",
    "needed_pipeline": "t1-freesurfer and t1-freesurfer longitudinal",
}

T1_FS_WM_SURF_L = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/surf/lh.white",
    "description": "left white matter/gray matter border surface (lh.white).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_DESTRIEUX = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/mri/aparc.a2009s+aseg.mgz",
    "description": "Destrieux-based segmentation (mri/aparc.a2009s+aseg.mgz).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_DESTRIEUX_PARC_L = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/label/lh.aparc.a2009s.annot",
    "description": "left hemisphere surface-based Destrieux parcellation (label/lh.aparc.a2009s.annot).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_LONG_DESTRIEUX_PARC_L = {
    "pattern": "t1/long-*/freesurfer_longitudinal/sub-*_ses-*.long.sub-*_*/label/lh.aparc.a2009s.annot",
    "description": "left hemisphere surface-based Destrieux parcellation (label/lh.aparc.a2009s.annot) generated with t1-freesurfer-longitudinal.",
    "needed_pipeline": "t1-freesurfer and t1-freesurfer longitudinal",
}

T1_FS_LONG_DESTRIEUX_PARC_R = {
    "pattern": "t1/long-*/freesurfer_longitudinal/sub-*_ses-*.long.sub-*_*/label/rh.aparc.a2009s.annot",
    "description": "right hemisphere surface-based Destrieux parcellation (label/rh.aparc.a2009s.annot) generated with t1-freesurfer-longitudinal.",
    "needed_pipeline": "t1-freesurfer and t1-freesurfer longitudinal",
}

T1_FS_DESTRIEUX_PARC_R = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/label/rh.aparc.a2009s.annot",
    "description": "right hemisphere surface-based Destrieux parcellation (label/rh.aparc.a2009s.annot).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_DESIKAN = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/mri/aparc+aseg.mgz",
    "description": "Desikan-based segmentation (mri/aparc.a2009s+aseg.mgz).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_DESIKAN_PARC_L = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/label/lh.aparc.annot",
    "description": "left hemisphere surface-based Desikan parcellation (label/lh.aparc.annot).",
    "needed_pipeline": "t1-freesurfer",
}

T1_FS_DESIKAN_PARC_R = {
    "pattern": "t1/freesurfer_cross_sectional/sub-*_ses-*/label/rh.aparc.annot",
    "description": "right hemisphere surface-based Desikan parcellation (label/rh.aparc.annot).",
    "needed_pipeline": "t1-freesurfer",
}

# T1-FreeSurfer-Template
T1_FS_T_DESTRIEUX = {
    "pattern": "freesurfer_unbiased_template/sub-*_long-*/mri/aparc.a2009s+aseg.mgz",
    "description": "Destrieux-based segmentation (mri/aparc.a2009s+aseg.mgz) from unbiased template.",
    "needed_pipeline": "t1-freesurfer-longitudinal or t1-freesurfer-template",
}

# T1-FreeSurfer-Longitudinal-Correction
T1_FS_LONG_DESIKAN_PARC_L = {
    "pattern": "t1/long-*/freesurfer_longitudinal/sub-*_ses-*.long.sub-*_*/label/lh.aparc.annot",
    "description": "left hemisphere surface-based Desikan parcellation (label/lh.aparc.annot) generated with t1-freesurfer-longitudinal.",
    "needed_pipeline": "t1-freesurfer and t1-freesurfer-longitudinal",
}

T1_FS_LONG_DESIKAN_PARC_R = {
    "pattern": "t1/long-*/freesurfer_longitudinal/sub-*_ses-*.long.sub-*_*/label/rh.aparc.annot",
    "description": "right hemisphere surface-based Desikan parcellation (label/rh.aparc.annot) generated with t1-freesurfer-longitudinal.",
    "needed_pipeline": "t1-freesurfer and t1-freesurfer-longitudinal",
}

T1W_LINEAR = {
    "pattern": "*space-MNI152NLin2009cSym_res-1x1x1_T1w.nii.gz",
    "description": "T1w image registered in MNI152NLin2009cSym space using t1-linear pipeline",
    "needed_pipeline": "t1-linear",
}

T2W_LINEAR = {
    "pattern": "*space-MNI152NLin2009cSym_res-1x1x1_T2w.nii.gz",
    "description": "T2w image registered in MNI152NLin2009cSym space using t2-linear pipeline",
    "needed_pipeline": "t2-linear",
}

FLAIR_T2W_LINEAR = {
    "pattern": "*space-MNI152NLin2009cSym_res-1x1x1_flair.nii.gz",
    "description": "T2w image registered in MNI152NLin2009cSym space using t2-linear pipeline",
    "needed_pipeline": "flair-linear",
}

T1W_LINEAR_CROPPED = {
    "pattern": "*space-MNI152NLin2009cSym_desc-Crop_res-1x1x1_T1w.nii.gz",
    "description": "T1W Image registered using t1-linear and cropped "
    "(matrix size 169×208×179, 1 mm isotropic voxels)",
    "needed_pipeline": "t1-linear",
}

T2W_LINEAR_CROPPED = {
    "pattern": "*space-MNI152NLin2009cSym_desc-Crop_res-1x1x1_T2w.nii.gz",
    "description": "T2W Image registered using t2-linear and cropped "
    "(matrix size 169×208×179, 1 mm isotropic voxels)",
    "needed_pipeline": "t2-linear",
}

FLAIR_T2W_LINEAR_CROPPED = {
    "pattern": "*space-MNI152NLin2009cSym_desc-Crop_res-1x1x1_flair.nii.gz",
    "description": "T2W Image registered using t2-linear and cropped "
    "(matrix size 169×208×179, 1 mm isotropic voxels)",
    "needed_pipeline": "flair-linear",
}

T1W_EXTENSIVE = {
    "pattern": "*space-Ixi549Space_desc-SkullStripped_T1w.nii.gz",
    "description": "T1w image skull-stripped registered in Ixi549Space space using clinicaDL preprocessing pipeline",
    "needed_pipeline": "t1-extensive",
}

T1W_TO_MNI_TRANSFORM = {
    "pattern": "*space-MNI152NLin2009cSym_res-1x1x1_affine.mat",
    "description": "Transformation matrix from T1W image to MNI space using t1-linear pipeline",
    "needed_pipeline": "t1-linear",
}

T2W_TO_MNI_TRANSFROM = {
    "pattern": "*space-MNI152NLin2009cSym_res-1x1x1_affine.mat",
    "description": "Transformation matrix from T2W image to MNI space using t2-linear pipeline",
    "needed_pipeline": "t2-linear",
}

FLAIR_T2W_TO_MNI_TRANSFROM = {
    "pattern": "*space-MNI152NLin2009cSym_res-1x1x1_affine.mat",
    "description": "Transformation matrix from T2W image to MNI space using t2-linear pipeline",
    "needed_pipeline": "flair-linear",
}


def aggregator(func):
    """If the decorated function receives iterable arguments,
    this decorator will call the decorated function for each
    value in the iterable and aggregate the results in a list.
    This works only if the iterables provided have the same length.
    Arguments lefts as non-iterable will be repeated.

    Examples
    --------
    The function `t1_volume_native_tpm` expects an integer defining the
    mask tissue and returns a dictionary describing the files to read:

    >>> import json
    >>> from clinica.utils.input_files import t1_volume_native_tpm
    >>> print(json.dumps(t1_volume_native_tpm(1), indent=3))
    {
        "pattern": "t1/spm/segmentation/native_space/*_*_T1w_segm-graymatter_probability.nii*",
        "description": "Tissue probability map graymatter in native space",
        "needed_pipeline": "t1-volume-tissue-segmentation"
    }

    Without the `aggregator` decorator, querying files for multiple
    tissues would have to be implemented in a loop:

    >>> print(json.dumps([t1_volume_native_tpm(tissue) for tissue in (1, 2)], indent=3))
    [
        {
            "pattern": "t1/spm/segmentation/native_space/*_*_T1w_segm-graymatter_probability.nii*",
            "description": "Tissue probability map graymatter in native space",
            "needed_pipeline": "t1-volume-tissue-segmentation"
        },
        {
            "pattern": "t1/spm/segmentation/native_space/*_*_T1w_segm-whitematter_probability.nii*",
            "description": "Tissue probability map whitematter in native space",
            "needed_pipeline": "t1-volume-tissue-segmentation"
        }
    ]

    Although this is fine, you might not know in a pipeline what was provided (scalar or iterable).
    With the `aggregator` decorator, you can pass both:

    >>> t1_volume_native_tpm((1, 2))
    [
        {
            "pattern": "t1/spm/segmentation/native_space/*_*_T1w_segm-graymatter_probability.nii*",
            "description": "Tissue probability map graymatter in native space",
            "needed_pipeline": "t1-volume-tissue-segmentation"
        },
        {
            "pattern": "t1/spm/segmentation/native_space/*_*_T1w_segm-whitematter_probability.nii*",
            "description": "Tissue probability map whitematter in native space",
            "needed_pipeline": "t1-volume-tissue-segmentation"
        }
    ]

    This works also with multiple args and kwargs:

    >>> from clinica.utils.input_files import t1_volume_native_tpm_in_mni
    >>> print(json.dumps(t1_volume_native_tpm_in_mni(1, False), indent=3))
    {
        "pattern": "t1/spm/segmentation/normalized_space/*_*_T1w_segm-graymatter_space-Ixi549Space_modulated-off_probability.nii*",
        "description": "Tissue probability map graymatter based on native MRI in MNI space (Ixi549) without modulation.",
        "needed_pipeline": "t1-volume-tissue-segmentation"
    }
    >>> print(json.dumps(t1_volume_native_tpm_in_mni(1, (True, False)), indent=3))
    [
        {
            "pattern": "t1/spm/segmentation/normalized_space/*_*_T1w_segm-graymatter_space-Ixi549Space_modulated-on_probability.nii*",
            "description": "Tissue probability map graymatter based on native MRI in MNI space (Ixi549) with modulation.",
            "needed_pipeline": "t1-volume-tissue-segmentation"
        },
        {
            "pattern": "t1/spm/segmentation/normalized_space/*_*_T1w_segm-graymatter_space-Ixi549Space_modulated-off_probability.nii*",
            "description": "Tissue probability map graymatter based on native MRI in MNI space (Ixi549) without modulation.",
            "needed_pipeline": "t1-volume-tissue-segmentation"
        }
    ]
    >>> print(json.dumps(t1_volume_native_tpm_in_mni((1, 2), (True, False)), indent=3))
    [
        {
            "pattern": "t1/spm/segmentation/normalized_space/*_*_T1w_segm-graymatter_space-Ixi549Space_modulated-on_probability.nii*",
            "description": "Tissue probability map graymatter based on native MRI in MNI space (Ixi549) with modulation.",
            "needed_pipeline": "t1-volume-tissue-segmentation"
        },
        {
            "pattern": "t1/spm/segmentation/normalized_space/*_*_T1w_segm-whitematter_space-Ixi549Space_modulated-off_probability.nii*",
            "description": "Tissue probability map whitematter based on native MRI in MNI space (Ixi549) without modulation.",
            "needed_pipeline": "t1-volume-tissue-segmentation"
        }
    ]
    """

    @functools.wraps(func)
    def wrapper_aggregator(*args, **kwargs):
        # Get the lengths of iterable args and kwargs
        arg_sizes = [
            len(arg)
            for arg in args
            if (isinstance(arg, Iterable) and not isinstance(arg, str))
        ]
        arg_sizes += [
            len(arg)
            for k, arg in kwargs.items()
            if (isinstance(arg, Iterable) and not isinstance(arg, str))
        ]

        # If iterable args/kwargs have different lengths, raise
        if len(set(arg_sizes)) > 1:
            raise ValueError(f"Arguments must have the same length.")

        # No iterable case, just call the function
        if len(arg_sizes) == 0:
            return func(*args, **kwargs)

        # Handle args first by repeating non-iterable values
        arg_size = arg_sizes[0]
        new_args = []
        for arg in args:
            if not (isinstance(arg, Iterable) and not isinstance(arg, str)):
                new_args.append((arg,) * arg_size)
            else:
                new_args.append(arg)

        # Same thing for kwargs
        new_kwargs = [{} for _ in range(arg_size)]
        for k, arg in kwargs.items():
            for i in range(len(new_kwargs)):
                if not (isinstance(arg, Iterable) and not isinstance(arg, str)):
                    new_kwargs[i][k] = arg
                else:
                    new_kwargs[i][k] = arg[i]

        # Properly encapsulate in a for loop
        if len(new_args) == 0:
            return [func(**x) for x in new_kwargs]
        elif len(new_kwargs) == 0:
            return [func(*x) for x in zip(*new_args)]
        return [func(*x, **y) for x, y in zip(zip(*new_args), new_kwargs)]

    return wrapper_aggregator


@aggregator
def t1_volume_native_tpm(tissue_number: int) -> dict:
    from pathlib import Path

    from .spm import get_spm_tissue_from_index

    tissue = get_spm_tissue_from_index(tissue_number)
    return {
        "pattern": Path("t1")
        / "spm"
        / "segmentation"
        / "native_space"
        / f"*_*_T1w_segm-{tissue.value}_probability.nii*",
        "description": f"Tissue probability map {tissue.value} in native space",
        "needed_pipeline": "t1-volume-tissue-segmentation",
    }


@aggregator
def t1_volume_dartel_input_tissue(tissue_number: int) -> dict:
    from pathlib import Path

    from .spm import get_spm_tissue_from_index

    tissue = get_spm_tissue_from_index(tissue_number)
    return {
        "pattern": Path("t1")
        / "spm"
        / "segmentation"
        / "dartel_input"
        / f"*_*_T1w_segm-{tissue.value}_dartelinput.nii*",
        "description": f"Dartel input for tissue probability map {tissue.value} from T1w MRI",
        "needed_pipeline": "t1-volume-tissue-segmentation",
    }


@aggregator
def t1_volume_native_tpm_in_mni(tissue_number: int, modulation: bool) -> dict:
    from pathlib import Path

    from .spm import get_spm_tissue_from_index

    tissue = get_spm_tissue_from_index(tissue_number)
    pattern_modulation = "on" if modulation else "off"
    description_modulation = "with" if modulation else "without"

    return {
        "pattern": Path("t1")
        / "spm"
        / "segmentation"
        / "normalized_space"
        / f"*_*_T1w_segm-{tissue.value}_space-Ixi549Space_modulated-{pattern_modulation}_probability.nii*",
        "description": (
            f"Tissue probability map {tissue.value} based on "
            f"native MRI in MNI space (Ixi549) {description_modulation} modulation."
        ),
        "needed_pipeline": "t1-volume-tissue-segmentation",
    }


def t1_volume_template_tpm_in_mni(
    group_label: str, tissue_number: int, modulation: bool, fwhm: Optional[int] = None
) -> dict:
    """Build the dictionary required by clinica_file_reader to get the tissue
    probability maps based on group template in MNI space.

    Parameters
    ----------
    group_label : str
        Label used for the group of interest.

    tissue_number : int
        An integer defining the tissue of interest.

    modulation : {"on", "off"}
        Whether modulation is on or off.

    fwhm : int, optional
        The smoothing kernel in millimeters.

    Returns
    -------
    dict :
        Information dict to be passed to clinica_file_reader.
    """
    from pathlib import Path

    from .spm import get_spm_tissue_from_index

    tissue = get_spm_tissue_from_index(tissue_number)
    pattern_modulation = "on" if modulation else "off"
    description_modulation = "with" if modulation else "without"
    fwhm_key_value = f"_fwhm-{fwhm}mm" if fwhm else ""
    fwhm_description = f"with {fwhm}mm smoothing" if fwhm else "with no smoothing"

    return {
        "pattern": Path("t1")
        / "spm"
        / "dartel"
        / f"group-{group_label}"
        / f"*_T1w_segm-{tissue.value}_space-Ixi549Space_modulated-{pattern_modulation}{fwhm_key_value}_probability.nii*",
        "description": (
            f"Tissue probability map {tissue.value} based on {group_label} template in MNI space "
            f"(Ixi549) {description_modulation} modulation and {fwhm_description}."
        ),
        "needed_pipeline": "t1-volume",
    }


def t1_volume_deformation_to_template(group_label):
    from pathlib import Path

    information = {
        "pattern": Path("t1")
        / "spm"
        / "dartel"
        / f"group-{group_label}"
        / f"sub-*_ses-*_T1w_target-{group_label}_transformation-forward_deformation.nii*",
        "description": f"Deformation from native space to group template {group_label} space.",
        "needed_pipeline": "t1-volume-create-dartel",
    }
    return information


@aggregator
def t1_volume_i_th_iteration_group_template(group_label, i):
    from pathlib import Path

    information = {
        "pattern": Path(f"group-{group_label}")
        / "t1"
        / f"group-{group_label}_iteration-{i}_template.nii*",
        "description": f"Iteration #{i} of Dartel template {group_label}",
        "needed_pipeline": "t1-volume or t1-volume-create-dartel",
    }
    return information


def t1_volume_final_group_template(group_label):
    from pathlib import Path

    information = {
        "pattern": Path(f"group-{group_label}")
        / "t1"
        / f"group-{group_label}_template.nii*",
        "description": f"T1w template file of group {group_label}",
        "needed_pipeline": "t1-volume or t1-volume-create-dartel",
    }
    return information


def custom_group(pattern, description):
    information = {"pattern": pattern, "description": description}
    return information


""" DWI """

# BIDS

DWI_NII = {"pattern": "dwi/sub-*_ses-*_dwi.nii*", "description": "DWI NIfTI"}

DWI_JSON = {"pattern": "dwi/sub-*_ses-*_dwi.json", "description": "DWI JSON file"}

DWI_BVAL = {"pattern": "dwi/sub-*_ses-*_dwi.bval", "description": "bval files"}

DWI_BVEC = {"pattern": "dwi/*_dwi.bvec", "description": "bvec files"}

FMAP_PHASEDIFF_JSON = {
    "pattern": "fmap/sub-*_ses-*_phasediff.json",
    "description": "phasediff JSON file",
}

FMAP_PHASEDIFF_NII = {
    "pattern": "fmap/sub-*_ses-*_phasediff.nii*",
    "description": "phasediff NIfTI volume",
}

FMAP_MAGNITUDE1_NII = {
    "pattern": "fmap/sub-*_ses-*_magnitude1.nii*",
    "description": "magnitude1 file",
}

# CAPS

DWI_PREPROC_NII = {
    "pattern": "dwi/preprocessing/sub-*_ses-*_space-*_desc-preproc_dwi.nii*",
    "description": "preprocessed DWI",
    "needed_pipeline": "dwi-preprocessing-using-t1 or dwi-preprocessing-using-fieldmap",
}

DWI_PREPROC_BRAINMASK = {
    "pattern": "dwi/preprocessing/sub-*_ses-*_space-*_brainmask.nii*",
    "description": "b0 brainmask",
    "needed_pipeline": "dwi-preprocessing-using-t1 or dwi-preprocessing-using-fieldmap",
}

DWI_PREPROC_BVEC = {
    "pattern": "dwi/preprocessing/sub-*_ses-*_space-*_desc-preproc_dwi.bvec",
    "description": "preprocessed bvec",
    "needed_pipeline": "dwi-preprocessing-using-t1 or dwi-preprocessing-using-fieldmap",
}

DWI_PREPROC_BVAL = {
    "pattern": "dwi/preprocessing/*_space-*_desc-preproc_dwi.bval",
    "description": "preprocessed bval",
    "needed_pipeline": "dwi-preprocessing-using-t1 or dwi-preprocessing-using-fieldmap",
}


def dwi_dti(measure: Union[str, DTIBasedMeasure], space: Optional[str] = None) -> dict:
    """Return the query dict required to capture DWI DTI images.

    Parameters
    ----------
    measure : DTIBasedMeasure or str
        The DTI based measure to consider.

    space : str, optional
        The space to consider.
        By default, all spaces are considered (i.e. '*' is used in regexp).

    Returns
    -------
    dict :
        The query dictionary to get DWI DTI images.
    """
    measure = DTIBasedMeasure(measure)
    space = space or "*"

    return {
        "pattern": f"dwi/dti_based_processing/*/*_space-{space}_{measure.value}.nii.gz",
        "description": f"DTI-based {measure.value} in space {space}.",
        "needed_pipeline": "dwi_dti",
    }


""" PET """

# BIDS


def bids_pet_nii(
    tracer: Optional[Union[str, Tracer]] = None,
    reconstruction: Optional[Union[str, ReconstructionMethod]] = None,
) -> dict:
    """Return the query dict required to capture PET scans.

    Parameters
    ----------
    tracer : Tracer, optional
        If specified, the query will only match PET scans acquired
        with the requested tracer.
        If None, the query will match all PET sans independently of
        the tracer used.

    reconstruction : ReconstructionMethod, optional
        If specified, the query will only match PET scans reconstructed
        with the specified method.
        If None, the query will match all PET scans independently of the
        reconstruction method used.

    Returns
    -------
    dict :
        The query dictionary to get PET scans.
    """
    from pathlib import Path

    description = f"PET data"
    trc = ""
    rec = ""

    if tracer is not None:
        tracer = Tracer(tracer)
        trc = f"_trc-{tracer.value}"
        description += f" with {tracer.value} tracer"
        rec = "*"
    if reconstruction is not None:
        reconstruction = ReconstructionMethod(reconstruction)
        rec = f"_rec-{reconstruction.value}"
        description += f" with reconstruction method {reconstruction.value}"

    return {
        "pattern": Path("pet") / f"*{trc}{rec}_pet.nii*",
        "description": description,
    }


# PET-Volume


def pet_volume_normalized_suvr_pet(
    acq_label: Union[str, Tracer],
    group_label: str,
    suvr_reference_region: Union[str, SUVRReferenceRegion],
    use_brainmasked_image: bool,
    use_pvc_data: bool,
    fwhm: int = 0,
) -> dict:
    from pathlib import Path

    acq_label = Tracer(acq_label)
    region = SUVRReferenceRegion(suvr_reference_region)

    if use_brainmasked_image:
        mask_key_value = "_mask-brain"
        mask_description = "brain-masked"
    else:
        mask_key_value = ""
        mask_description = "full"

    if use_pvc_data:
        pvc_key_value = "_pvc-rbv"
        pvc_description = "using RBV method for PVC"
    else:
        pvc_key_value = ""
        pvc_description = "without PVC"

    if fwhm:
        fwhm_key_value = f"_fwhm-{fwhm}mm"
        fwhm_description = f"with {fwhm}mm smoothing"
    else:
        fwhm_key_value = ""
        fwhm_description = "with no smoothing"

    suvr_key_value = f"_suvr-{region.value}"

    information = {
        "pattern": Path("pet")
        / "preprocessing"
        / f"group-{group_label}"
        / f"*_trc-{acq_label.value}_pet_space-Ixi549Space{pvc_key_value}{suvr_key_value}{mask_key_value}{fwhm_key_value}_pet.nii*",
        "description": (
            f"{mask_description} SUVR map (using {region.value} region) of {acq_label.value}-PET "
            f"{pvc_description} and {fwhm_description} in Ixi549Space space based on {group_label} DARTEL template"
        ),
        "needed_pipeline": "pet-volume",
    }
    return information


def _clean_pattern(pattern: str, character: str = "*") -> str:
    """Removes multiple '*' wildcards in provided pattern."""
    cleaned = []
    for c in pattern:
        if not cleaned or not cleaned[-1] == c == character:
            cleaned.append(c)
    return "".join(cleaned)


def pet_linear_nii(
    acq_label: Optional[Union[str, Tracer]] = None,
    suvr_reference_region: Optional[Union[str, SUVRReferenceRegion]] = None,
    uncropped_image: bool = False,
    space: str = "mni",
    resolution: Optional[int] = None,
) -> dict:
    from pathlib import Path

    tracer_filter = "*"
    tracer_description = ""
    if acq_label:
        acq_label = Tracer(acq_label)
        tracer_filter = f"_trc-{acq_label.value}"
        tracer_description = f" obtained with tracer {acq_label.value}"
    region_filter = "*"
    region_description = ""
    if suvr_reference_region:
        region = SUVRReferenceRegion(suvr_reference_region)
        region_filter = f"_suvr-{region.value}"
        region_description = f" for SUVR region {region.value}"
    space_filer = f"_space-{'MNI152NLin2009cSym' if space == 'mni' else 'T1w'}"
    space_description = f" affinely registered to the {'MNI152NLin2009cSym template' if space == 'mni' else 'associated T1w image'}"
    description = "*"
    if space == "mni" and not uncropped_image:
        description = "_desc-Crop"
    resolution_filter = "*"
    resolution_description = ""
    if resolution:
        resolution_explicit = f"{resolution}x{resolution}x{resolution}"
        resolution_filter = f"_res-{resolution_explicit}"
        resolution_description = f" of resolution {resolution_explicit}"
    information = {
        "pattern": Path("pet_linear")
        / _clean_pattern(
            f"*{tracer_filter}{space_filer}{description}{resolution_filter}{region_filter}_pet.nii.gz"
        ),
        "description": (
            f"{'Cropped ' if space == 'mni' and not uncropped_image else ''}PET nifti image{resolution_description}"
            f"{tracer_description}{region_description}{space_description} resulting from the pet-linear pipeline"
        ),
        "needed_pipeline": "pet-linear",
    }
    return information


def pet_linear_transformation_matrix(tracer: Union[str, Tracer]) -> dict:
    from pathlib import Path

    tracer = Tracer(tracer)

    return {
        "pattern": Path("pet_linear") / f"*_trc-{tracer.value}_space-T1w_rigid.mat",
        "description": "Rigid transformation matrix between the PET and T1w images estimated with ANTs.",
        "needed_pipeline": "pet-linear",
    }


# CUSTOM
def custom_pipeline(pattern, description):
    information = {"pattern": pattern, "description": description}
    return information
