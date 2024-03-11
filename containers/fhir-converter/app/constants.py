import json
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from pydantic import Field

# Requests and responses for the service are defined in this file.
# Examples of both are also stored here.

# Defining example requests/responses
raw_sample_response = json.load(
    open(
        Path(__file__).parent.parent
        / "assets"
        / "sample_vxu_fhir_conversion_response.json"
    )
)
sample_response = {200: raw_sample_response}

sample_request = json.load(
    open(Path(__file__).parent.parent / "assets" / "sample_fhir_converter_request.json")
)


# Request input types
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
    ELR = "ELR"
    ConsultationNote = "ConsultationNote"
    DischargeSummary = "DischargeSummary"
    Header = "Header"
    HistoryandPhysical = "HistoryandPhysical"
    OperativeNote = "OperativeNote"
    ProcedureNote = "ProcedureNote"
    ProgressNote = "ProgressNote"
    ReferralNote = "ReferralNote"
    TransferSummary = "TransferSummary"


# Request types
class FhirConverterInput(BaseModel):
    """
    Input parameters for the FHIR Converter.
    """

    input_data: str = Field(
        description="The message to be converted as a string.",
    )
    input_type: InputType = Field(
        description="The type of message to be converted.", example="vxu"
    )
    root_template: RootTemplate = Field(
        description="Name of the liquid template within to be used for conversion.",
    )
    rr_data: Optional[str] = Field(
        description="If an eICR message, the accompanying Reportability Response data.",
        default=None,
    )
