from typing import List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class GeocodeResult:
    """
    A basic dataclass representing a successful geocoding response.
    Based on the field nomenclature of a FHIR address, specified at
    https://www.hl7.org/fhir/datatypes.html#Address.
    """

    line: List[str]
    city: str
    state: str
    postal_code: str
    county_fips: str
    lat: float
    lng: float
    district: Optional[str] = None
    country: Optional[str] = None
    county_name: Optional[str] = None
    precision: Optional[str] = None


class GeocodeClient(ABC):
    """
    A basic abstract class representing a vendor-agnostic geocoder client.
    Requires implementing classes to define methods to geocode from both
    strings and dictionaries. Callers should use the provided interface
    functions (e.g. geocode_from_str) to interact with the underlying
    vendor-specific client property.
    """

    @abstractmethod
    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Function that uses the implementing client to perform geocoding
        on the provided address, which is formatted as a string.
        """
        pass

    @abstractmethod
    def geocode_from_dict(self, address: dict) -> Union[GeocodeResult, None]:
        """
        Function that uses the implementing client to perform geocoding
        on the provided address, which is given as a dictionary.
        """
        pass
