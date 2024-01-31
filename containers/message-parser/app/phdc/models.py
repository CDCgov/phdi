from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional


@dataclass
class Telecom:
    value: Optional[str] = None
    type: Optional[str] = None
    useable_period_low: Optional[str] = None
    useable_period_high: Optional[str] = None


@dataclass
class Address:
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
    name: List[Name] = None
    address: List[Address] = None
    telecom: List[Telecom] = None
    administrative_gender_code: Optional[str] = None
    race_code: Optional[str] = None
    ethnic_group_code: Optional[str] = None
    birth_time: Optional[str] = None


@dataclass
class CodedElement:
    xsi_type: Optional[str] = None
    code: Optional[str] = None
    code_system: Optional[str] = None
    code_system_name: Optional[str] = None
    display_name: Optional[str] = None

    def to_attributes(self) -> Dict[str, str]:
        """
        to_attributes is intended to take a standard CodedElements
          and simplify them to a dictionary that can be looped through for
          multiple types of simple elements. Right now, primarily Observation.

          It will create a small dictionary that can then be assigned to an ET.Element.
        """
        # Create a dictionary with XML attribute names
        attributes = {
            "{http://www.w3.org/2001/XMLSchema-instance}type": self.xsi_type,
            "code": self.code,
            "codeSystem": self.code_system,
            "codeSystemName": self.code_system_name,
            "displayName": self.display_name,
        }
        return {k: v for k, v in attributes.items() if v is not None}


@dataclass
class Observation:
    type_code: Optional[str] = None
    class_code: Optional[str] = None
    mood_code: Optional[str] = None
    code: Optional[CodedElement] = None
    value: Optional[CodedElement] = None
    translation: Optional[CodedElement] = None


@dataclass
class PHDCInputData:
    type: Literal[
        "case_report", "contact_record", "lab_report", "morbidity_report"
    ] = "case_report"
    patient: Patient = None
    clinical_info: List[Observation] = None
