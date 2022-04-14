import csv
import io

import azure.functions as func

from GenerateCSVs.fhir import (
    read_bundles_by_type,
    write_csvs,
    RECORD_TYPE_VXU,
    RECORD_TYPE_ELR,
    RECORD_TYPE_ECR,
)

from GenerateCSVs.vxu import VXU_COLUMNS, vxu_to_csv
from GenerateCSVs.elr import ELR_COLUMNS, elr_to_csv
from GenerateCSVs.ecr import ECR_COLUMNS, ecr_to_csv

from config import get_required_config


RECORD_TYPES = {
    RECORD_TYPE_VXU: (VXU_COLUMNS, vxu_to_csv),
    RECORD_TYPE_ELR: (ELR_COLUMNS, elr_to_csv),
    RECORD_TYPE_ECR: (ECR_COLUMNS, ecr_to_csv),
}


def generate_csvs(container_url: str, container_prefix: str) -> dict[str, io.StringIO]:
    """Generate a csv for each record type"""

    # Initialize the output, then a set of csv writers
    results = {k: io.StringIO() for k in RECORD_TYPES.keys()}
    writers = {k: csv.writer(results[k]) for k in RECORD_TYPES.keys()}

    # Write column headers for each record
    for k, spec in RECORD_TYPES.items():
        writers[k].writerow(spec[0])

    # For each record, run the associated function and write the appropriate csv
    for rtype, bundle in read_bundles_by_type(
        container_url, container_prefix, RECORD_TYPES.keys()
    ):
        cols, fn = RECORD_TYPES[rtype]
        writers[rtype].writerow(fn(bundle))

    return results


def main(req: func.HttpRequest) -> func.HttpResponse:
    write_csvs(
        get_required_config("CONTAINER_URL"),
        get_required_config("CSV_OUTPUT_PREFIX"),
        generate_csvs(
            get_required_config("CONTAINER_URL"),
            get_required_config("CSV_INPUT_PREFIX"),
        ),
    )

    return func.HttpResponse("ok")
