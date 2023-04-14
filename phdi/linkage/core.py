from typing import List, Union
from abc import ABC, abstractmethod


class BaseMPIConnectorClient(ABC):
    """
    Represents a vendor-agnostic Master Patient Index (MPI) connector client. Requires
    implementing classes to define methods to retrive blocks of data from the MPI.
    Callers should use the provided interface functions (e.g., block_data)
    to interact with the underlying vendor-specific client property.
    """

    @abstractmethod
    def block_data() -> List[list]:
        """
        Returns a list of lists containing records from the database that match on the
        incoming record's block values. If blocking on 'ZIP' and the incoming record's
        zip code is '90210', the resulting block of data would contain records that all
        have the same zip code of 90210.

        """
        pass  # pragma: no cover

    @abstractmethod
    def get_connection() -> Union[any, None]:
        """
        Creates a connection to the database associated with the connector class.
        The connection is returned for use in other class methods as a context
        manager, and should generally not be called externally to the client.
        Also used for testing the validity of a connection when the client
        connector is instantiated. The return type is set to any here since the
        exact "class" of the client's connection is unknown in the abstract.
        """
        pass  # pragma: no cover

    @abstractmethod
    def insert_match_patient() -> None:
        """
        If a matching person ID has been found in the MPI, inserts a new patient into
        the patient table and updates the person table to link to the new patient; else
        inserts a new patient into the patient table and inserts a new person into the
        person table with a new personID, linking the new personID to the new patient.

        """
        pass  # pragma: no cover

    @abstractmethod
    def _generate_block_query(self, block_vals: dict) -> str:
        """
        Generates a query for selecting a block of data from the patient table per the
        block_vals parameters. Accepted blocking fields include: first_name, last_name,
        birthdate, addess, city, state, zip, mrn, and sex.
        """
        pass  # pragma: no cover
