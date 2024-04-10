from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Union


@dataclass
class GeocodeResult:
    """
    Represents a successful geocoding response.
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
    geoid: Optional[str] = None
    census_tract: Optional[str] = None
    census_block: Optional[str] = None


class BaseGeocodeClient(ABC):
    """
    Represents a vendor-agnostic geocoder client. Requires implementing
    classes to define methods to geocode from both strings and dictionaries.
    Callers should use the provided interface functions (e.g., geocode_from_str)
    to interact with the underlying vendor-specific client property.
    """

    @abstractmethod
    def geocode_from_str(self, address: str) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a string.

        :param address: The address to geocode, given as a string.
        :param overwrite: If true, `resource` is modified in-place;
          if false, a copy of `resource` modified and returned.  Default: `True`
        :return: A geocoded address (if valid result) or None (if no valid result).
        """
        pass  # pragma: no cover

    @abstractmethod
    def geocode_from_dict(self, address: dict) -> Union[GeocodeResult, None]:
        """
        Geocodes the provided address, which is formatted as a dictionary.

        The given dictionary should conform to standard nomenclature around address
        fields, including:

        * `street`: the number and street address
        * `street2`: additional street level information (if needed)
        * `apartment`: apartment or suite number (if needed)
        * `city`: city to geocode
        * `state`: state to geocode
        * `postal_code`: the postal code to use
        * `urbanization`: urbanization code for area, sector, or regional
        * `development`: (only used for Puerto Rican addresses)

        There is no minimum number of fields that must be specified to use this
        function; however, a minimum of street, city, and state are suggested
        for the best matches.

        :param address: A dictionary with fields outlined above.
        :return: A geocoded address (if valid result) or None (if no valid result).
        """
        pass  # pragma: no cover
