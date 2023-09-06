from pathlib import Path
from fastapi import FastAPI, Response, status

from phdi.fhir.conversion import add_rr_data_to_eicr
from app.constants import (
    sample_response,
    FhirConverterInput,
)
from app.service import convert_to_fhir

description = (Path(__file__).parent.parent / "description.md").read_text(
    encoding="utf-8"
)

app = FastAPI(
    title="PHDI FHIR Converter Service",
    version="0.0.1",
    contact={
        "name": "CDC Public Health Data Infrastructure",
        "url": "https://cdcgov.github.io/phdi-site/",
        "email": "dmibuildingblocks@cdc.gov",
    },
    license_info={
        "name": "Creative Commons Zero v1.0 Universal",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
    },
    description=description,
)


@app.get("/")
async def health_check():
    """
    Check service status. If an HTTP 200 status code is returned along with
    '{"status": "OK"}' then the FHIR conversion service is available and running
    properly.
    """
    return {"status": "OK"}


@app.post(
    "/convert-to-fhir",
    status_code=200,
    responses=sample_response,
)
async def convert(input: FhirConverterInput, response: Response):
    """
    Converts an HL7v2 or C-CDA message to FHIR format using the Microsoft FHIR
    Converter CLI tool. When conversion is successful, a dictionary containing the
    response from the FHIR Converter is returned.

    In order to successfully call this function, the Microsoft FHIR Converter tool
    must be installed. For information on how to do this, please refer to the
    description.md file. The source code for the converter can be found at
    https://github.com/microsoft/FHIR-Converter.
    """
    fhir_converter_input = dict(input)
    fhir_converter_input.pop("rr_data")

    # If RR is present, also need input data and conversion type eICR
    if input.rr_data is not None:
        if input.root_template != "EICR" or input.input_type != "ecr":
            response.status_code = status.HTTP_400_BAD_REQUEST
            result = {
                "message": "Reportability Response (RR) data is only accepted "
                "for eCR conversion requests."
            }
            return result

        merged_ecr = add_rr_data_to_eicr(input.rr_data, input.input_data)
        fhir_converter_input.update({"input_data": merged_ecr})

    result = convert_to_fhir(**fhir_converter_input)
    if "fhir_conversion_failed" in result.get("response"):
        response.status_code = status.HTTP_400_BAD_REQUEST

    return result
