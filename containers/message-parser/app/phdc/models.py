from dataclasses import dataclass
from typing import List, Optional


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
class PHDCInputData:
    type: str = "case report"
    patient: Patient = None
