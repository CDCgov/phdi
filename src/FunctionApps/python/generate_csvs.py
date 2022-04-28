import csv
import sys

from GenerateCSVs import RECORD_TYPES
from GenerateCSVs.fhir import (
    RECORD_TYPE_VXU,
    RECORD_TYPE_ELR,
    RECORD_TYPE_ECR,
    read_bundles_by_type,
)

import typer
from enum import Enum


class RecordType(str, Enum):
    vxu = RECORD_TYPE_VXU
    elr = RECORD_TYPE_ELR
    ecr = RECORD_TYPE_ECR


def main(container_url: str, prefix: str, record_type: RecordType):
    cols, fn = RECORD_TYPES[record_type]

    writer = csv.writer(sys.stdout)
    writer.writerow(cols)

    for _, bundle in read_bundles_by_type(container_url, prefix, [record_type]):
        writer.writerows(fn(bundle))


if __name__ == "__main__":
    typer.run(main)
