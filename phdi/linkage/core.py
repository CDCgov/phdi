from typing import List, Dict
from abc import ABC, abstractmethod


class BaseMPIConnectorClient(ABC):
    """
    Represents a vendor-agnostic Master Patient Index (MPI) connector client. Requires
    implementing classes to define methods to retrive blocks of data from the MPI.
    Callers should use the provided interface functions (e.g., block_data)
    to interact with the underlying vendor-specific client property.
    """

    @abstractmethod
    def block_data(db_name: str, table_name: str, block_data: Dict) -> List[list]:
        """
        Returns a list of lists containing records from the database that match on the
        incoming record's block values. If blocking on 'ZIP' and the incoming record's
        zip code is '90210', the resulting block of data would contain records that all
        have the same zip code of 90210.

        :param db_name: Database name.
        :param table_name: Table name.
        :param block_data: Dictionary containing key value pairs for the column name for
        blocking and the data for the incoming record, e.g., ["ZIP"]: "90210".
        :return: A list of records that are within the block, e.g., records that all
        have 90210 as their ZIP.
        """
        pass  # pragma: no cover

    @abstractmethod
    def upsert_match_patient(
        patient_record: Dict,
        patient_table_name: str,
        person_table_name: str,
        person_id=None,
    ) -> None:
        """
        If a matching person ID has been found in the MPI, inserts a new patient into
        the patient table and updates the person table to link to the new patient; else
        inserts a new patient into the patient table and inserts a new person into the
        person table with a new personID, linking the new personID to the new patient.

        :param patient_record: A FHIR patient resource.
        :param patient_table_name: Name of patient table to update or insert into.
        :param person_table_name: Name of person table to update or insert into.
        :param person_id: The personID matching the patient record if a match has been
        found in the MPI, defaults to None.
        """
        pass  # pragma: no cover
