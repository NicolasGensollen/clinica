from typing import Callable, Tuple, Union

from ..adni_to_bids import ADNIUserFacingModality


class ADNIModalityConverter:
    """Class acting as a factory for ADNI modality converters.

    It provides a uniform interface for the different modality converters.

    Example
    -------
    >>> converter = ADNIModalityConverter("dwi")
    >>> converter.convert()
    """

    def __init__(self, modality: Union[str, ADNIUserFacingModality]):
        if isinstance(modality, str):
            modality = ADNIUserFacingModality(modality)
        self.modality = modality

    @property
    def converters(self) -> Tuple[Callable, ...]:
        """Return a tuple of available converters for the modality."""
        if self.modality == ADNIUserFacingModality.T1:
            from ._t1 import convert_adni_t1

            return (convert_adni_t1,)

        if self.modality == ADNIUserFacingModality.PET_FDG:
            from ._fdg_pet import convert_adni_fdg_pet, convert_adni_fdg_pet_uniform

            return convert_adni_fdg_pet, convert_adni_fdg_pet_uniform

        if self.modality == ADNIUserFacingModality.PET_AMYLOID:
            from ._av45_fbb_pet import convert_adni_av45_fbb_pet
            from ._pib_pet import convert_adni_pib_pet

            return convert_adni_pib_pet, convert_adni_av45_fbb_pet

        if self.modality == ADNIUserFacingModality.PET_TAU:
            from ._tau_pet import convert_adni_tau_pet

            return (convert_adni_tau_pet,)

        if self.modality == ADNIUserFacingModality.DWI:
            from ._dwi import convert_adni_dwi

            return (convert_adni_dwi,)

        if self.modality == ADNIUserFacingModality.FLAIR:
            from ._flair import convert_adni_flair

            return (convert_adni_flair,)

        if self.modality == ADNIUserFacingModality.FMRI:
            from ._fmri import convert_adni_fmri

            return (convert_adni_fmri,)

    def convert(self, **kwargs):
        """Call every converter available iteratively with the user inputs."""
        for converter in self.converters:
            converter(**kwargs)
