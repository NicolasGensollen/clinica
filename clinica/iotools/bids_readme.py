from typing import IO

from attrs import define

from .bids_utils import StudyName


@define
class BIDSReadme:
    """Model representing the content for a BIDS Readme."""

    name: StudyName
    link: str
    description: str

    def write(self, to: IO[str]):
        from importlib.metadata import version

        to.write(
            f"This BIDS directory was generated with Clinica v{version('clinica')}.\n"
            f"More information on https://www.clinica.run\n"
            f"\n"
            f"Study: {self.name.value}\n"
            f"\n"
            f"{self.description}\n\n"
            f"Find more about it and about the data user agreement: {self.link}"
        )
