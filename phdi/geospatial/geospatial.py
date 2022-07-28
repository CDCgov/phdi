from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class GeocodeResult:
    """
    A basic dataclass representing a successful geocoding response.
    """

    street: List[str]
    city: str
    state: str
    zipcode: str
    county_fips: str
    county_name: str
    lat: float
    lng: float
    precision: str


class GeocodeClient(ABC):
    """
    A basic abstract class representing a vendor-agnostic geocoder client.
    Requires implementing classes to define methods to geocode from both
    strings and dictionaries. Treats the underlying client in vendor-
    specific implementations as a special internal property which can
    be accessed using .client().
    """

    @property
    @abstractmethod
    def client(self):
        pass

    @abstractmethod
    def geocode_from_str(self):
        pass

    @abstractmethod
    def geocode_from_dict(self):
        pass
