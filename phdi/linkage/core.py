from typing import List
from abc import ABC, abstractmethod

from sqlalchemy import Select


class BaseMPIConnectorClient(ABC):
    """
    Represents a vendor-agnostic Master Patient Index (MPI) connector client. Requires
    implementing classes to define methods to retrive blocks of data from the MPI.
    Callers should use the provided interface functions (e.g., block_data)
    to interact with the underlying vendor-specific client property.
    """

    @abstractmethod
    def get_block_data() -> List[list]:
        """
        Returns a list of lists containing records from the MPI database that
        match on the incoming record's block criteria and values. If blocking
        on 'ZIP' and the incoming record's zip code is '90210', the resulting
        block of data would contain records that all
        have the same zip code of 90210.

        """
        pass  # pragma: no cover

    @abstractmethod
    def insert_matched_patient() -> None:
        """
        If a matching person ID has been found in the MPI, inserts a new patient into
        the patient table and all other subsequent MPI tables, including the
        matched person id, to link the new patient and matched person ID;
        else inserts a new patient into the patient table, as well as all other
        subsequent MPI tables, and inserts a new person into the person table
        linking the new person to the new patient.
        """
        pass  # pragma: no cover

    @abstractmethod
    def _generate_block_query(self, block_critieria: dict) -> Select:
        """
         Generates a query for selecting a block of data from the MPI tables per the
        block field criteria.  The block field criteria should be a dictionary
        organized by MPI table name, with the ORM table object, and the blocking
        criteria.
        """
        pass  # pragma: no cover

    @abstractmethod
    def _get_person_id() -> str:
        """
        If person id is not supplied then generate a new person record
        with a new person id.
        If an external person id is not supplied then just return the new
        person id.
        If an external person id is supplied then check if there is an
        external person record created for this external person id.
        If the external person record exists then verify that the person id,
        either supplied or newly created, is linked to the external person record.
        If the person id supplied, or newly created, is not linked in the found
        external person record then create a new external person record using
        the supplied external person id and the person id (either supplied
        or newly created).
        If the external person record does exist and is linked to the person id,
        either supplied or newly created, then just return the person id.
        If an external person record does not exist with the supplied external
        person id then create a new external person record and link it to the
        the person id, either supplied or newly created.  Then return the person id.
        """
        pass  # pragma: no cover
