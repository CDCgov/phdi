from typing import List, Dict
from phdi.linkage.core import BaseMPIConnectorClient
import psycopg2


class PostgresConnectorClient(BaseMPIConnectorClient):
    """
    Represents a Postgres-specific Master Patient Index (MPI) connector client. Requires
    implementing classes to define methods to retrive blocks of data from the MPI.
    Callers should use the provided interface functions (e.g., geocode_from_str)
    to interact with the underlying vendor-specific client property.
    """

    def __init__(
        self,
        database: str,
        user: str,
        password: str,
        host: str,
        port: str,
        patient_table: str,
        person_table: str,
    ) -> None:
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.patient_table = patient_table
        self.person_table = person_table

        try:
            self.connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
        except Exception as error:
            print(f"{error}")
        self.cursor = self.connection.cursor()

    def block_data(self, table_name, block_data: Dict) -> List[list]:
        """
        Returns a list of lists containing records from the database that match on the
        incoming record's block values. If blocking on 'ZIP' and the incoming record's
        zip code is '90210', the resulting block of data would contain records that all
        have the same zip code of 90210.

        :param table_name: Table to return blocked data from, e.g., Patient MPI.
        :param block_data: Dictionary containing key value pairs for the column name for
        blocking and the data for the incoming record, e.g., ["ZIP"]: "90210".
        :return: A list of records that are within the block, e.g., records that all
        have 90210 as their ZIP.
        """
        if len(block_data) == 0:
            raise ValueError("`block_data` cannot be empty.")

        # Generate raw SQL query
        query = self._generate_block_query(table_name, block_data)

        # Execute query
        self.cursor.execute(query)
        blocked_data = [list(row) for row in self.cursor.fetchall()]

        return blocked_data

    def upsert_match_patient(
        self,
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

        print("temp workaround!")

    def _generate_block_query(self, table_name: str, block_data: Dict) -> str:
        """
        Generates a query for selecting a block of data from `table_name` per the
        block_data parameters.

        :param table_name: Table name.
        :param block_data: Dictionary containing key value pairs for the column name
        for blocking and the data for the incoming record, e.g., ["ZIP"]: "90210".
        :return: Query to select block of data base on `block_data` parameters.

        """
        query_stub = f"SELECT * FROM {table_name} WHERE "
        block_query = " AND ".join(
            [
                key + f" = '{value}'" if type(value) == str else (key + f" = {value}")
                for key, value in block_data.items()
            ]
        )
        query = query_stub + block_query + ";"
        return query
