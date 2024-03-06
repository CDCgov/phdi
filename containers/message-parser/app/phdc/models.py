from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Union


@dataclass
class Telecom:
    """
    A class containing all of the data elements for a telecom element.
    """

    value: Optional[str] = None
    type: Optional[str] = None
    useable_period_low: Optional[str] = None
    useable_period_high: Optional[str] = None


@dataclass
class Address:
    """
    A class containing all of the data elements for an address element.
    """

    street_address_line_1: Optional[str] = None
    street_address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    county: Optional[str] = None
    country: Optional[str] = None
    type: Optional[str] = None
    useable_period_low: Optional[str] = None
    useable_period_high: Optional[str] = None


@dataclass
class Name:
    """
    A class containing all of the data elements for a name element.
    """

    prefix: Optional[str] = None
    first: Optional[str] = None
    middle: Optional[str] = None
    family: Optional[str] = None
    suffix: Optional[str] = None
    type: Optional[str] = None
    valid_time_low: Optional[str] = None
    valid_time_high: Optional[str] = None


@dataclass
class Patient:
    """
    A class containing all of the data elements for a patient element.
    """

    name: List[Name] = None
    address: List[Address] = None
    telecom: List[Telecom] = None
    administrative_gender_code: Optional[str] = None
    race_code: Optional[str] = None
    ethnic_group_code: Optional[str] = None
    birth_time: Optional[str] = None


@dataclass
class Organization:
    """
    A class containing all of the data elements for an organization element.
    """

    id: str = None
    name: str = None
    telecom: Telecom = None
    address: Address = None


@dataclass
class CodedElement:
    """
    A class containing all of the data elements for a coded element.
    """

    xsi_type: Optional[str] = None
    code: Optional[str] = None
    code_system: Optional[str] = None
    code_system_name: Optional[str] = None
    display_name: Optional[str] = None
    value: Optional[str] = None
    text: Optional[Union[str, int]] = None

    def to_attributes(self) -> Dict[str, str]:
        """
        Given a standard CodedElements return a dictionary that can be iterated over to
        produce the corresponding XML element.

        :return: A dictionary of the CodedElement's attributes
        """
        # Create a dictionary with XML attribute names
        attributes = {
            "{http://www.w3.org/2001/XMLSchema-instance}type": self.xsi_type,
            "code": self.code,
            "codeSystem": self.code_system,
            "codeSystemName": self.code_system_name,
            "displayName": self.display_name,
            "value": self.value,
            "text": self.text,
        }
        return {k: v for k, v in attributes.items() if v is not None}


@dataclass
class Observation:
    """
    A class containing all of the data elements for an observation element.
    """

    obs_type: str = "laboratory"
    type_code: Optional[str] = None
    class_code: Optional[str] = None
    code_display: Optional[str] = None
    code_system: Optional[str] = None
    code_system_name: Optional[str] = None
    quantitative_value: Optional[float] = None
    quantitative_system: Optional[str] = None
    quantitative_code: Optional[str] = None
    qualitative_value: Optional[str] = None
    qualitative_system: Optional[str] = None
    qualitative_code: Optional[str] = None
    mood_code: Optional[str] = None
    code_code: Optional[str] = None
    code_code_system: Optional[str] = None
    code_code_system_name: Optional[str] = None
    code_code_display: Optional[str] = None
    value_quantitative_code: Optional[str] = None
    value_quant_code_system: Optional[str] = None
    value_quant_code_system_name: Optional[str] = None
    value_quantitative_value: Optional[float] = None
    value_qualitative_code: Optional[str] = None
    value_qualitative_code_system: Optional[str] = None
    value_qualitative_code_system_name: Optional[str] = None
    value_qualitative_value: Optional[str] = None
    components: Optional[list] = None
    code: Optional[CodedElement] = None
    value: Optional[CodedElement] = None
    translation: Optional[CodedElement] = None
    text: Optional[str] = None


@dataclass
class PHDCInputData:
    """
    A class containing all of the data to construct a PHDC document when passed to the
    PHDCBuilder.
    """

    type: Literal["case_report", "contact_record", "lab_report", "morbidity_report"] = (
        "case_report"
    )
    patient: Patient = None
    organization: List[Organization] = None
    clinical_info: List[List[Observation]] = field(default_factory=list)
    social_history_info: List[List[Observation]] = field(default_factory=list)
    repeating_questions: List[List[Observation]] = field(default_factory=list)
