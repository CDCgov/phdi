from typing import List, Union
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
    strings and dictionaries. Callers should use the provided interface
    functions (e.g. geocode_from_str) to interact with the underlying
    vendor-specific client property.
    """

    @property
    @abstractmethod
    def client(self):
        """
        Since abstract base classes in python don't conventionally define
        instance variables (because they lack constructors), this abstract
        property does the following for implementing classes:
          1. defines a private instance variable __client that's accessible
             in implementing functions
          2. makes it accessible through the use of .client()
        This instance variable will hold whatever vendor-specific client
        is instantiated by implementing classes so that they can perform
        geocoding without referencing the underlying client that connects
        to the vendor service.
        """
        pass

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
