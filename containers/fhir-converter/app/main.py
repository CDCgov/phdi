from pathlib import Path
import subprocess
import json
import uuid
from enum import Enum
from fastapi import FastAPI, Response, status
from pydantic import BaseModel, Field

# Reading sample request & response files for docs
raw_sample_response = json.load(
    open(
        Path(__file__).parent.parent
        / "assets"
        / "sample_vxu_fhir_conversion_response.json"
    )
)
sample_response = {200: raw_sample_response}

sample_request = open(
    Path(__file__).parent.parent / "assets" / "sample_request.hl7"
).read()

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


class InputType(str, Enum):
    elr = "elr"
    vxu = "vxu"
    ecr = "ecr"


class RootTemplate(str, Enum):
    ADT_A01 = "ADT_A01"
    ADT_A02 = "ADT_A02"
    ADT_A03 = "ADT_A03"
    ADT_A04 = "ADT_A04"
    ADT_A05 = "ADT_A05"
    ADT_A06 = "ADT_A06"
    ADT_A07 = "ADT_A07"
    ADT_A08 = "ADT_A08"
    ADT_A09 = "ADT_A09"
    ADT_A10 = "ADT_A10"
    ADT_A11 = "ADT_A11"
    ADT_A13 = "ADT_A13"
    ADT_A14 = "ADT_A14"
    ADT_A15 = "ADT_A15"
    ADT_A16 = "ADT_A16"
    ADT_A25 = "ADT_A25"
    ADT_A26 = "ADT_A26"
    ADT_A27 = "ADT_A27"
    ADT_A28 = "ADT_A28"
    ADT_A29 = "ADT_A29"
    ADT_A31 = "ADT_A31"
    ADT_A40 = "ADT_A40"
    ADT_A41 = "ADT_A41"
    ADT_A45 = "ADT_A45"
    ADT_A47 = "ADT_A47"
    ADT_A60 = "ADT_A60"
    BAR_P01 = "BAR_P01"
    BAR_P02 = "BAR_P02"
    BAR_P12 = "BAR_P12"
    DFT_P03 = "DFT_P03"
    DFT_P11 = "DFT_P11"
    MDM_T01 = "MDM_T01"
    MDM_T02 = "MDM_T02"
    MDM_T05 = "MDM_T05"
    MDM_T06 = "MDM_T06"
    MDM_T09 = "MDM_T09"
    MDM_T10 = "MDM_T10"
    OMG_O19 = "OMG_O19"
    OML_O21 = "OML_O21"
    ORM_O01 = "ORM_O01"
    ORU_R01 = "ORU_R01"
    OUL_R22 = "OUL_R22"
    OUL_R23 = "OUL_R23"
    OUL_R24 = "OUL_R24"
    RDE_O11 = "RDE_O11"
    RDE_O25 = "RDE_O25"
    RDS_O13 = "RDS_O13"
    REF_I12 = "REF_I12"
    REF_I14 = "REF_I14"
    SIU_S12 = "SIU_S12"
    SIU_S13 = "SIU_S13"
    SIU_S14 = "SIU_S14"
    SIU_S15 = "SIU_S15"
    SIU_S16 = "SIU_S16"
    SIU_S17 = "SIU_S17"
    SIU_S26 = "SIU_S26"
    VXU_V04 = "VXU_V04"
    CCD = "CCD"
    EICR = "EICR"
    ConsultationNote = "ConsultationNote"
    DischargeSummary = "DischargeSummary"
    Header = "Header"
    HistoryandPhysical = "HistoryandPhysical"
    OperativeNote = "OperativeNote"
    ProcedureNote = "ProcedureNote"
    ProgressNote = "ProgressNote"
    ReferralNote = "ReferralNote"
    TransferSummary = "TransferSummary"


class FhirConverterInput(BaseModel):
    """
    Input parameters for the FHIR Converter.
    """

    input_data: str = Field(
        description="The message to be converted as a string.",
        example=sample_request,
    )
    input_type: InputType = Field(
        description="The type of message to be converted.", example="vxu"
    )
    root_template: RootTemplate = Field(
        description="Name of the liquid template within to be used for conversion.",
        example="VXU_V04",
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
    result = convert_to_fhir(**dict(input))
    if "fhir_conversion_failed" in result.get("response"):
        response.status_code = status.HTTP_400_BAD_REQUEST

    return result


def add_data_source_to_bundle(bundle: dict, data_source: str) -> dict:
    """
    Given a FHIR bundle and a a data source parameter the function
    will loop through the bundle and add a Meta.source entry for
    every resource in the bundle.

    :param bundle: The FHIR bundle to add minimum provenance to.
    :param data_source: The data source of the FHIR bundle.
    :return: The FHIR bundle with the a Meta.source entry for each
      FHIR resource in the bunle
    """
    if data_source == "":
        raise ValueError(
            "The data_source parameter must be a defined, non-empty string."
        )

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if "meta" in resource:
            meta = resource["meta"]
        else:
            meta = {}
            resource["meta"] = meta

        if "source" in meta:
            meta["source"].append(data_source)
        else:
            meta["source"] = [data_source]

    return bundle


def convert_to_fhir(
    input_data: str,
    input_type: str,
    root_template: str,
) -> dict:
    """
    Call the Microsoft FHIR Converter CLI tool to convert an Hl7v2, or C-CDA message
    to FHIR R4. The message to be converted can be provided either as a string via the
    input_data_content argument, or by specifying a path to a file containing the
    message with input_data_file_path. One, but not both of these parameters is
    required. When conversion is successfull a dictionary containing the resulting FHIR
    bundle is returned. When conversion fails a dictionary containing the response from
    the FHIR Converter is returned. In order to successfully call this function,
    the conversion tool must be installed. For information on how to do this please
    refer to FHIR-Converter-Installation-And-Usage-Guide. The source code for the
    converter can be found at https://github.com/microsoft/FHIR-Converter.

    :param input_data: The message to be converted as a string.
    :param input_type: The type of message to be converted. Valid values are
        "elr", "vxu", and "ecr".
    :param root_template: Name of the liquid template within to be used for conversion.
        Options are listed in the FHIR-Converter README.md.
    """

    # Setup path variables
    converter_project_path = (
        "/build/FHIR-Converter/output/Microsoft.Health.Fhir.Liquid.Converter.Tool.dll"
    )
    if input_type == "elr" or input_type == "vxu":
        template_directory_path = "/build/FHIR-Converter/data/Templates/Hl7v2"
    elif input_type == "ecr":
        template_directory_path = "/build/FHIR-Converter/data/Templates/eCR"
    else:
        raise ValueError(
            f"Invalid input_type {input_type}. Valid values are 'hl7v2' and 'ecr'."
        )
    output_data_file_path = "/tmp/output.json"

    # Write input data to file
    input_data_file_path = Path(f"/tmp/{input_type}-input.txt")
    input_data_file_path.write_text(input_data)

    # Formulate command for the FHIR Converter.
    fhir_conversion_command = [
        f"dotnet {converter_project_path} ",
        "convert -- ",
        f"--TemplateDirectory {template_directory_path} ",
        f"--RootTemplate {root_template} ",
        f"--InputDataFile {str(input_data_file_path)} "
        f"--OutputDataFile {str(output_data_file_path)} ",
    ]

    fhir_conversion_command = "".join(fhir_conversion_command)

    # Call the FHIR Converter.
    converter_response = subprocess.run(
        fhir_conversion_command, shell=True, capture_output=True
    )

    # Process the response from FHIR Converter.
    if converter_response.returncode == 0:
        result = json.load(open(output_data_file_path))
        # Generate a new UUID for the patient resource.
        for entry in result["FhirResource"]["entry"]:
            if entry["resource"]["resourceType"] == "Patient":
                old_id = entry["resource"]["id"]
                break
        new_id = str(uuid.uuid4())
        result = json.dumps(result)
        result = result.replace(old_id, new_id)
        result = json.loads(result)
        result = add_data_source_to_bundle(result, input_type)

    else:
        result = vars(converter_response)
        result["fhir_conversion_failed"] = "true"

    return {"response": result}
