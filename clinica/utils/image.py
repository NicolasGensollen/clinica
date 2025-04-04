from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from os import PathLike
from pathlib import Path
from typing import Callable, Optional, Tuple, Union

import nibabel as nib
import numpy as np
from nibabel.nifti1 import Nifti1Image

__all__ = [
    "HemiSphere",
    "NiftiImage",
    "NiftiImage3D",
    "compute_aggregated_volume",
    "get_new_image_like",
    "merge_nifti_images_in_time_dimension",
    "remove_dummy_dimension_from_image",
    "crop_nifti",
    "clip_nifti",
    "crop_nifti_using_t1_mni_template",
    "get_mni_template",
    "get_mni_cropped_template",
]


class HemiSphere(str, Enum):
    """Possible values for hemispheres."""

    LEFT = "lh"
    RIGHT = "rh"


def compute_aggregated_volume(
    image_filename: PathLike,
    aggregator: Optional[Callable] = None,
    volumes_to_keep: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Computes the aggregated 3D volumes from a 4D image and an aggregator function.

    The aggregation is computed on the last (fourth) dimension.
    It is possible to compute the aggregation on a subset of the volumes through the
    parameter 'volumes_to_keep'.

    Parameters
    ----------
    image_filename : str
        The path to the input image.

    aggregator : Callable, optional
        The aggregator function. Example: np.average, np.median.
        If None, no aggregation will be performed.

    volumes_to_keep : np.array, optional
        The volumes to be kept during aggregation. This is a 1D index array.
        If None, all volumes of the input image will be kept during aggregation.
        Default = None.

    Returns
    -------
    np.ndarray:
        The 3D volume data array obtained from the aggregation.
    """
    volumes = np.array(nib.four_to_three(nib.load(image_filename)))
    if volumes_to_keep is None:
        volumes_to_keep = volumes
    else:
        volumes_to_keep = volumes[volumes_to_keep]
    data = [
        volume.get_fdata(dtype="float32").astype(np.float32)
        for volume in volumes_to_keep
    ]
    if aggregator is None:
        return np.stack(data, axis=-1)
    return aggregator(data, axis=0)


def get_new_image_like(old_image: PathLike, new_image_data: np.ndarray) -> Nifti1Image:
    """Builds a new Nifti1Image from the provided image and new data.

    Parameters
    ----------
    old_image : PathLike
        The path to the old image file from which to get the header and affine.

    new_image_data : np.ndarray
        The data for the new image to build.

    Returns
    -------
    Nifti1Image :
        The new image.
    """
    old_img = nib.load(old_image)
    hdr = old_img.header.copy()
    hdr.set_data_shape(new_image_data.shape)
    hdr.set_xyzt_units("mm")
    hdr.set_data_dtype(np.float32)

    return nib.Nifti1Image(new_image_data, old_img.affine, hdr)


def clip_nifti(
    input_image: Path,
    new_image_suffix: str = "_clipped",
    low: Optional[float] = None,
    high: Optional[float] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """Build a new nifti image from the clipped values of the provided image.

    Parameters
    ----------
    input_image : Path
        The path to the nifti image to be clipped.

    new_image_suffix : str, optional
        The suffix for building the new image file name.
        By default, it is '_clipped' such that the output image file name
        of an image named 'image.nii.gz' will be 'image_clipped.nii.gz'.

    low : float, optional
        The low threshold for clipping.
        If None, no thresholding will be applied.

    high : float, optional
        The high threshold for clipping.
        If None, no thresholding will be applied.

    output_dir : Path, optional
        The path to the folder in which the output image should be written.
        If None, the image will be written in the current directory.

    Returns
    -------
    output_image : Path
        The path to the output clipped image.
    """
    from .filemanip import get_filename_no_ext

    clipped = get_new_image_like(
        input_image,
        np.clip(
            nib.load(input_image).get_fdata(dtype="float32"),
            a_min=low,
            a_max=high,
        ),
    )
    output_image = (
        output_dir or Path.cwd()
    ) / f"{get_filename_no_ext(input_image)}{new_image_suffix}.nii.gz"
    clipped.to_filename(output_image)
    return output_image


def merge_nifti_images_in_time_dimension(
    images: Tuple[Union[str, PathLike], ...], out_file: Optional[PathLike] = None
) -> PathLike:
    """Concatenates the provided images in the 4th dimension.

    The provided images must all be 3D or 4D. For 3D images, a dummy
    4th dimension will be added before concatenation.

    Parameters
    ----------
    images : tuple of str or tuple of Pathlike
        The paths to the images that should get merged.

    out_file : PathLike, optional
        The path to the file in which to write the merged
        volumes. If None, the volumes will be written to a
        file named 'merged_files.nii.gz' in the current folder.

    Returns
    -------
    out_file : PathLike
        Path to merged volumes.
    """
    import os

    images = _check_existence(images)
    out_file = out_file or os.path.abspath("merged_files.nii.gz")
    volumes = _check_volumes_from_images(images)
    merged_volume = np.concatenate(volumes, axis=-1)
    merged_image = get_new_image_like(images[0], merged_volume)
    nib.save(merged_image, out_file)

    return out_file


def _check_existence(filenames: Tuple[PathLike, ...]) -> Tuple[Path, ...]:
    """Converts all element in provided tuple to Path objects and check for existence."""
    from pathlib import Path

    if len(filenames) < 2:
        raise ValueError("At least 2 files are required.")
    filenames = tuple(Path(f) for f in filenames)
    missing_files = tuple(f for f in filenames if not f.exists())
    if missing_files:
        raise FileNotFoundError(f"the following file(s) are missing: {missing_files}")
    return filenames


def _check_volumes_from_images(images: Tuple[Path, ...]) -> Tuple[np.ndarray, ...]:
    """Loads the images and check the dimensions."""
    images = tuple(nib.load(i) for i in images)
    volumes = tuple(i.get_fdata() for i in images)
    four_dimensional_volumes = []
    for volume in volumes:
        if volume.ndim == 3:
            four_dimensional_volumes.append(volume[..., np.newaxis])
        elif volume.ndim == 4:
            four_dimensional_volumes.append(volume)
        else:
            raise ValueError(
                f"Only 3D or 4D images can be concatenated. A {volume.ndim}D image was found."
            )

    return tuple(four_dimensional_volumes)


def remove_dummy_dimension_from_image(image: str, output: str) -> str:
    """Remove all dummy dimensions (i.e. equal to 1) from an image.

    Parameters
    ----------
    image : str
        Path to the input image.

    output : str
        Path to the desired output image.

    Returns
    -------
    str :
        The path to the output image.
    """
    import nibabel as nib
    from nilearn.image import new_img_like

    img = new_img_like(image, nib.load(image).get_fdata().squeeze())
    nib.save(img, output)

    return output


@dataclass
class Slice:
    """Interval composed of a starting point and ending point."""

    start: int
    end: int

    def __post_init__(self):
        if self.end < self.start:
            raise ValueError(
                f"Slice instance has a start value ({self.start}) larger than the end value ({self.end})."
            )

    def get_slice(self) -> slice:
        return slice(self.start, self.end)

    def __repr__(self) -> str:
        return f"( {self.start}, {self.end} )"


BboxTuple = tuple[tuple[int, int], tuple[int, int], tuple[int, int]]


@dataclass
class Bbox3D:
    """3D Bounding Box."""

    x_slice: Slice
    y_slice: Slice
    z_slice: Slice

    @classmethod
    def from_coordinates(
        cls,
        start_x: int,
        end_x: int,
        start_y: int,
        end_y: int,
        start_z: int,
        end_z: int,
    ):
        return cls(
            Slice(start_x, end_x),
            Slice(start_y, end_y),
            Slice(start_z, end_z),
        )

    @classmethod
    def from_tuple(cls, box: BboxTuple):
        return cls.from_coordinates(*box[0], *box[1], *box[2])

    def get_slices(self) -> tuple[slice, slice, slice]:
        return (
            self.x_slice.get_slice(),
            self.y_slice.get_slice(),
            self.z_slice.get_slice(),
        )

    def __repr__(self):
        return f"( {self.x_slice}, {self.y_slice}, {self.z_slice} )"


# This bounding box has been pre-computed by clinica developers
MNI_CROP_BBOX = Bbox3D.from_coordinates(12, 181, 13, 221, 0, 179)


def _is_bbox_within_array(array: np.ndarray, bbox: Bbox3D) -> bool:
    if not (0 <= bbox.x_slice.start and bbox.x_slice.end <= array.shape[0]):
        return False
    if not (0 <= bbox.y_slice.start and bbox.y_slice.end <= array.shape[1]):
        return False
    if not (0 <= bbox.z_slice.start and bbox.z_slice.end <= array.shape[2]):
        return False
    return True


def _crop_array(array: np.ndarray, bbox: Bbox3D) -> np.ndarray:
    # TODO: When Python 3.10 is dropped, replace with 'return array[*bbox.get_slices()]'
    from clinica.utils.exceptions import ClinicaImageDimensionError

    if _is_bbox_within_array(array, bbox):
        x, y, z = bbox.get_slices()
        return array[x, y, z]
    raise ClinicaImageDimensionError(
        f"Cannot use the bounding box {bbox} to crop the provided array of shape {array.shape}."
    )


def _get_file_locally_or_download(
    filename: str, url: Optional[str] = None, expected_checksum: Optional[str] = None
) -> Path:
    from clinica.utils.inputs import RemoteFileStructure, fetch_file

    resource_folder = Path(__file__).parent.parent / "resources" / "masks"
    local_file = resource_folder / filename
    if not local_file.exists():
        if url is None or expected_checksum is None:
            raise ValueError(
                f"Downloading file {filename} requires both the URL and the expected checksum "
                "such that it can be ensured that no data corruption occurred."
            )
        fetch_file(
            RemoteFileStructure(
                filename=filename,
                url=url,
                checksum=expected_checksum,
            ),
            resource_folder,
        )
    if local_file.exists():
        return local_file
    raise FileNotFoundError(f"Unable to get file {filename} locally or remotely.")


def get_mni_cropped_template() -> Path:
    return _get_file_locally_or_download(
        filename="ref_cropped_template.nii.gz",
        url="https://aramislab.paris.inria.fr/files/data/img_t1_linear/",
        expected_checksum="67e1e7861805a8fd35f7fcf2bdf9d2a39d7bcb2fd5a201016c4d2acdd715f5b3",
    )


def get_mni_template(modality: str) -> Path:
    """Get the path to the MNI template for the given modality.

    If the file can be found locally in the resources folder, it is
    returned directly, otherwise it is downloaded from the aramislab
    server.

    Parameters
    ----------
    modality : str
        t1 or flair depending on which template is desired.

    Returns
    -------
    Path :
        The path to the required MNI template.

    Raises
    ------
    ValueError:
        If the modality is not t1 or flair.
    FileNotFoundError:
        If the template could not be retrieved locally or remotely.
    """
    if modality.lower() == "t1":
        return _get_mni_template_t1()
    if modality.lower() == "flair":
        return _get_mni_template_flair()
    raise ValueError(f"No MNI template available for modality {modality}.")


def _get_mni_template_t1() -> Path:
    return _get_file_locally_or_download(
        filename="mni_icbm152_t1_tal_nlin_sym_09c.nii",
        url="https://aramislab.paris.inria.fr/files/data/img_t1_linear/",
        expected_checksum="93359ab97c1c027376397612a9b6c30e95406c15bf8695bd4a8efcb2064eaa34",
    )


def _get_mni_template_flair() -> Path:
    return _get_file_locally_or_download(
        filename="GG-853-FLAIR-1.0mm.nii.gz",
        url="https://aramislab.paris.inria.fr/files/data/img_flair_linear/",
        expected_checksum="b1d2d359a4c3671685227bb14014ce50ac232012b628335a4c049e2911c64ce1",
    )


class NiftiImage:
    """Wrapper around the nib.Nifti1Image."""

    def __init__(self, image_path: Union[str, Path]):
        from nibabel.filebasedimages import ImageFileError

        image_path = Path(image_path)
        if not image_path.is_file():
            raise FileNotFoundError(f"File {image_path} does not exist.")
        try:
            nib.load(image_path)
        except ImageFileError:
            raise IOError(f"File {image_path} is not a nifti image or is corrupted.")
        self.path = Path(image_path)

    @cached_property
    def image(self) -> nib.Nifti1Image:
        return nib.load(self.path)

    @property
    def shape(self) -> tuple[int, ...]:
        return self.image.shape

    @cached_property
    def data(self) -> np.ndarray:
        return self.image.get_fdata()

    @property
    def affine(self) -> np.ndarray:
        return self.image.affine

    def get_filename(self, with_extension: bool = True) -> str:
        from clinica.utils.filemanip import get_filename_no_ext

        if with_extension:
            return self.path.name
        return get_filename_no_ext(self.path.name)


class NiftiImage3D(NiftiImage):
    def __init__(self, image_path: Union[str, Path]):
        from clinica.utils.exceptions import ClinicaImageDimensionError

        super().__init__(image_path)
        if len(self.shape) != 3:
            raise ClinicaImageDimensionError(f"The image in {self.path} is not 3D.")

    @property
    def bbox(self) -> Bbox3D:
        return Bbox3D.from_coordinates(
            0, self.shape[0], 0, self.shape[1], 0, self.shape[2]
        )


def crop_nifti(
    input_image: Union[str, Path, NiftiImage3D],
    bounding_box: Optional[Union[Bbox3D, BboxTuple]] = None,
    reference_image: Optional[Union[str, Path, NiftiImage3D]] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """Crop the input image using the provided bounding box.

    If no bounding box is provided, the function performs no cropping.

    The function expects a 3D anatomical image.

    If the bounding box falls outside the image limits, the function will perform
    resampling of the input image onto the reference cropped template.

    Parameters
    ----------
    input_image : str, Path, or NiftiImage3D
        The input image to be cropped. It can be a path to a nifti file,
        provided as a plain string or a Path object, or it can be an
        instance of NiftiImage3D. If the image is not 3D, an error will
        be raised.

    bounding_box : Bbox3D or BboxTuple, optional
        The bounding box to be used for cropping.
        It can be either an instance of Bbox3D or provided as tuples:
        ((start_x, end_x), (start_y, end_y), (start_z, end_z))
        If no bounding box is provided, the function performs no cropping.

    reference_image : str, Path, or NiftiImage3D, optional
        The reference image used to get the header of the cropped image.
        If nothing is provided, the header of the input image will be used.
        This can be provided as a plain string or a Path object. It can also
        be an instance of NiftiImage3D.

    output_dir : str or Path, optional
        The folder in which to write the output cropped image.
        If not provided, the image will be written in current folder.

    Returns
    -------
    output_img : Path
        The path to the cropped image.

    Raises
    ------
    ClinicaImageDimensionError:
        If the input image is not 3D or if the output image has unexpected dimension.
    """
    from nilearn.image import new_img_like, resample_to_img

    from clinica.utils.exceptions import ClinicaImageDimensionError
    from clinica.utils.stream import log_and_warn

    if not isinstance(input_image, NiftiImage3D):
        input_image = NiftiImage3D(input_image)
    if bounding_box is None:
        bounding_box = input_image.bbox
    if not isinstance(bounding_box, Bbox3D):
        bounding_box = Bbox3D.from_tuple(bounding_box)
    if reference_image:
        if not isinstance(reference_image, NiftiImage3D):
            reference_image = NiftiImage3D(reference_image)
    else:
        reference_image = input_image
    try:
        cropped_array = _crop_array(input_image.data, bounding_box)
        crop_img = new_img_like(reference_image.image, cropped_array)
    except ClinicaImageDimensionError:
        log_and_warn(
            (
                f"The image {input_image.path} has dimensions {input_image.shape} and cannot be "
                f"cropped using the bounding box {bounding_box}. The `crop_nifti` function will try to resample the "
                f"input image to the reference template {reference_image.path} instead of cropping."
            ),
            UserWarning,
        )
        crop_img = resample_to_img(
            input_image.image, reference_image.image, force_resample=True
        )
    if crop_img.shape != reference_image.shape:
        raise ClinicaImageDimensionError(
            f"The cropped image has shape {crop_img.shape} different from the expected shape "
            f"{reference_image.shape} of the reference template {reference_image.path}."
        )
    output_img = (
        output_dir or Path.cwd()
    ) / f"{input_image.get_filename(with_extension=False)}_cropped.nii.gz"
    crop_img.to_filename(output_img)

    return output_img


def crop_nifti_using_t1_mni_template(
    input_image: Union[str, Path, NiftiImage3D],
    output_dir: Optional[Path] = None,
) -> Path:
    """The function expects a 3D anatomical image and will crop it using a pre-computed bounding box.

    This bounding box has been used to crop the MNI template (located in clinica/resources/masks/mni_icbm152_t1_tal_nlin_sym_09c.nii)
    into the cropped template (located in clinica/resources/masks/ref_cropped_template.nii.gz).

    Parameters
    ----------
    input_image : str, Path, or NiftiImage3D
        The input image to be cropped. It can be a path to a nifti file,
        provided as a plain string or a Path object, or it can be an
        instance of NiftiImage3D. If the image is not 3D, an error will
        be raised.

    output_dir : str or Path, optional
        The folder in which to write the output cropped image.
        If not provided, the image will be written in current folder.

    Returns
    -------
    output_img : Path
        The path to the cropped image.

    Raises
    ------
    ClinicaImageDimensionError:
        If the input image is not 3D or if the output image has unexpected dimension.
    """
    return crop_nifti(
        input_image,
        bounding_box=MNI_CROP_BBOX,
        reference_image=get_mni_cropped_template(),
        output_dir=output_dir,
    )
