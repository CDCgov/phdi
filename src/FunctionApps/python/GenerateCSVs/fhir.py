import io

from typing import Iterator, Tuple


RECORD_TYPE_VXU = "VXU"
RECORD_TYPE_ELR = "ELR"
RECORD_TYPE_ECR = "ECR"


def read_bundles_by_type() -> Iterator[Tuple[str, dict]]:
    """
    Read FHIR bundles from blob storage and return an iterator
    along with the source of the record (one of the RECORD_TYPE_ constants)
    """

    return


def write_csvs(csvs: dict[str, io.StringIO]) -> None:
    """Write the csvs to the final blob storage location"""
    pass
