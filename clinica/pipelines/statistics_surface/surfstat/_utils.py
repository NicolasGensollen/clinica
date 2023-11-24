"""This file contains functions for loading data from disk
and performing some checks on them.
"""
from os import PathLike
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from nilearn.surface import Mesh

TSV_FIRST_COLUMN = "participant_id"
TSV_SECOND_COLUMN = "session_id"


__all__ = [
    "read_and_check_tsv_file",
    "get_t1_freesurfer_custom_file_template",
    "build_thickness_array",
    "get_average_surface",
]


def read_and_check_tsv_file(tsv_file: PathLike) -> pd.DataFrame:
    """This function reads the TSV file provided and performs some basic checks.

    Parameters
    ----------
    tsv_file : PathLike
        Path to the TSV file to open.

    Returns
    -------
    tsv_data : pd.DataFrame
        DataFrame obtained from the file.
    """
    try:
        return pd.read_csv(tsv_file, sep="\t").set_index(
            [TSV_FIRST_COLUMN, TSV_SECOND_COLUMN]
        )
    except FileNotFoundError:
        raise FileNotFoundError(f"File {tsv_file} does not exist.")
    except KeyError:
        raise ValueError(
            f"The TSV data should have at least two columns: {TSV_FIRST_COLUMN} and {TSV_SECOND_COLUMN}"
        )


T1_FREESURFER_TEMPLATE_PATH_FROM_CAPS_ROOT = (
    "/%(subject)s/%(session)s/t1/freesurfer_cross_sectional/%(subject)s_%(session)s"
    "/surf/%(hemi)s.thickness.fwhm%(fwhm)s.fsaverage.mgh"
)


def get_t1_freesurfer_custom_file_template(base_dir: PathLike) -> str:
    """Returns a Template for the path to the desired surface file.

    Parameters
    ----------
    base_dir : PathLike
        Base directory to search for the template.

    Returns
    -------
    template_path : str
        Path to the t1 freesurfer template.
    """
    return str(base_dir) + T1_FREESURFER_TEMPLATE_PATH_FROM_CAPS_ROOT


def build_thickness_array(
    input_dir: Path,
    surface_file: str,
    df: pd.DataFrame,
    fwhm: float,
) -> np.ndarray:
    """This function builds the cortical thickness array.

    Parameters
    ----------
    input_dir : PathLike
        Input directory.

    surface_file : str
        Template for the path to the surface file of interest.

    df : pd.DataFrame
        Subjects DataFrame, indexed by participant_id, and session_id..

    fwhm : float
        Smoothing parameter only used to retrieve the right surface file.

    Returns
    -------
    thickness : np.ndarray
        Cortical thickness. Hemispheres and subjects are stacked.
    """
    from nibabel.freesurfer.mghformat import load

    thickness = []
    for idx, row in df.iterrows():
        subject, session = idx
        parts = []
        for hemi in ("lh", "rh"):
            query = {"subject": subject, "session": session, "fwhm": fwhm, "hemi": hemi}
            surface_file_path = str(input_dir / (surface_file % query))
            parts.append(load(surface_file_path).get_fdata())
        combined = np.vstack(parts)
        thickness.append(combined.flatten())
    thickness = np.vstack(thickness)
    if thickness.shape[0] != len(df):
        raise ValueError(
            f"Unexpected shape for thickness array : {thickness.shape}. "
            f"Expected {len(df)} rows."
        )
    return thickness


def get_average_surface(fsaverage_path: Path) -> Tuple[Dict, Mesh]:
    """This function extracts the average surface and the average mesh
    from the path to the fsaverage templates.

    .. note::

        Note that the average surface is returned as a dictionary
        with 'coord' and 'tri' as keys, while the average mesh is
        returned as a Nilearn Mesh object (basically a NamedTuple
        with 'coordinates' and 'faces' attributes). The surface
        isn't returned as a Nilearn Surface object for compatibility
        with BrainStats.

    .. warning::

        There is an issue with faces having  a value of 0 as index.
        This is most likely a bug in BrainStat as MATLAB indexing
        starts at 1 while Python starts at zero.

    Parameters
    ----------
    fsaverage_path : PathLike
        Path to the fsaverage templates.

    Returns
    -------
    average_surface : dict
        Average surface as a dictionary for BrainStat compatibility.

    average_mesh : nilearn.surface.Mesh
        Average mesh as a Nilearn Mesh object.
    """
    import copy

    from nilearn.surface import Mesh, load_surf_mesh

    meshes = [
        load_surf_mesh(str(fsaverage_path / f"{hemi}.pial")) for hemi in ("lh", "rh")
    ]
    coordinates = np.vstack([mesh.coordinates for mesh in meshes])
    _verify_finite(coordinates, "mesh coordinates")
    faces = np.vstack(
        [meshes[0].faces, meshes[1].faces + meshes[0].coordinates.shape[0]]
    )
    _verify_finite(faces, "faces")
    average_mesh = Mesh(
        coordinates=coordinates,
        faces=copy.deepcopy(faces),
    )
    ##################
    # UGLY HACK !!! Need investigation
    ##################
    # Uncomment the following line if getting an error
    # with negative values in bincount in Brainstat.
    # Not sure, but might be a bug in BrainStat...
    #
    faces += 1
    #################
    average_surface = {
        "coord": coordinates,
        "tri": faces,
    }
    return average_surface, average_mesh


def _verify_finite(array: np.ndarray, name: str) -> None:
    from clinica.utils.stream import cprint

    if not np.isfinite(array).all():
        raise ValueError(f"The {name} array contains non finite values: {array}")
    cprint(f"The {name} array has shape {array.shape}.", lvl="info")
