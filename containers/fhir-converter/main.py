from pathlib import Path
import subprocess
import json

from enum import Enum
from fastapi import FastAPI, Response, status
from pydantic import BaseModel


api = FastAPI()


class InputType(str, Enum):
    hl7v2 = "hl7v2"
    ccda = "ccda"


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

    input_data: str
    input_type: InputType
    root_template: RootTemplate


@api.get("/")
async def health_check():
    return {"status": "OK"}


@api.post("/convert-to-fhir", status_code=200)
async def convert(input: FhirConverterInput, response: Response):
    result = convert_to_fhir(**dict(input))
    if "original_request" in result.get("response"):
        response.status_code = status.HTTP_400_BAD_REQUEST

    return result


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
    :param input_type: The type of message to be converted. Valid values are "hl7v2"
        and "c-cda".
    :param root_template: Name of the liquid template within to be used for conversion.
        Options are listed in the FHIR-Converter README.md.
    """

    # Setup path variables
    converter_project_path = (
        "/build/FHIR-Converter/output/Microsoft.Health.Fhir.Liquid.Converter.Tool.dll"
    )
    if input_type == "hl7v2":
        template_directory_path = "/build/FHIR-Converter/data/Templates/Hl7v2"
    elif input_type == "ccda":
        template_directory_path = "/build/FHIR-Converter/data/Templates/Ccda"
    else:
        raise ValueError(
            f"Invalid input_type {input_type}. Valid values are 'hl7v2' and 'ccda'."
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
    else:
        result = vars(converter_response)
        # Include original input data in the result.
        result["original_request"] = {
            "input_data": input_data,
            "input_type": input_type,
            "root_template": root_template,
        }

    return {"response": result}
