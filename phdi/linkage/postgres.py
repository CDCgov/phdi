from typing import List, Dict
from phdi.linkage.core import BaseMPIConnectorClient
import psycopg2
import json


class PostgresConnectorClient(BaseMPIConnectorClient):
    """
    Represents a Postgres-specific Master Patient Index (MPI) connector client.
    Callers should use the provided interface functions (e.g., block_data)
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

    def block_data(self, block_data: Dict) -> List[list]:
        """
        Returns a list of lists containing records from the database that match on the
        incoming record's block values. If blocking on 'ZIP' and the incoming record's
        zip code is '90210', the resulting block of data would contain records that all
        have the same zip code of 90210.

        :param block_data: Dictionary containing key value pairs for the column name for
          blocking and the data for the incoming record, e.g., ["ZIP"]: "90210".
        :return: A list of records that are within the block, e.g., records that all
          have 90210 as their ZIP.
        """
        # TODO: Update with context manager
        # Connect to MPI
        try:
            self.connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            self.cursor = self.connection.cursor()
        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")

        if len(block_data) == 0:
            raise ValueError("`block_data` cannot be empty.")

        # Generate raw SQL query
        query = self._generate_block_query(self.patient_table, block_data)

        # Execute query
        self.cursor.execute(query)
        extracted_data = self.cursor.fetchall()

        # Close cursor and connection
        self.cursor.close()
        self.connection.close()

        # Set up blocked data by adding column headers as 1st row of LoL
        # TODO: Replace indices with column names for reability
        blocked_data = [["patient_id", "person_id"]]
        for key in sorted(list(extracted_data[0][-1].keys())):
            blocked_data[0].append(key)

        # Unnest patient_resource data
        for row in extracted_data:
            row_data = [row[0], row[1]]
            for value in sorted(list(row[-1].keys())):
                row_data.append(row[-1][value])
            blocked_data.append(row_data)

        return blocked_data

    def upsert_match_patient(
        self,
        patient_resource: Dict,
        person_id=None,
    ) -> None:
        """
        If a matching person ID has been found in the MPI, inserts a new patient into
        the patient table and updates the person table to link to the new patient; else
        inserts a new patient into the patient table and inserts a new person into the
        person table with a new personID, linking the new personID to the new patient.

        :param patient_record: A FHIR patient resource.
        :param person_id: The personID matching the patient record if a match has been
          found in the MPI, defaults to None.
        """
        # Connect to MPI
        try:
            self.connection = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            self.cursor = self.connection.cursor()
        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")

        # Match has been found
        if person_id is not None:
            # Insert into patient table
            insert_patient_table = (
                f"INSERT INTO {self.patient_table} "
                + "(patient_id, person_id, patient_resource) "
                + f"""VALUES ('{patient_resource.get("id")}', '{person_id}', """
                + f"""'{json.dumps(patient_resource)}');"""
            )
            self.cursor.execute(insert_patient_table)
            self.connection.commit()
            self.cursor.close()
            self.connection.close()

        # Match has not been found
        else:
            # Insert a new record into person table to generate new person_id
            self.cursor.execute(
                f"""INSERT INTO {self.person_table} """
                + """ (external_person_id) VALUES ('NULL') """
                + """ RETURNING person_id;"""
            )

            # Retrieve newly generated person_id
            person_id = self.cursor.fetchall()

            # Insert into patient table
            insert_patient_table = (
                f"INSERT INTO {self.patient_table} "
                + "(patient_id, person_id, patient_resource) "
                + f"VALUES ('{patient_resource.get('id')}','{person_id[0][0]}', "
                + f"'{json.dumps(patient_resource)}');"
            )
            self.cursor.execute(insert_patient_table)
            self.connection.commit()

            self.cursor.close()
            self.connection.close()

    def _generate_block_query(self, table_name: str, block_data: Dict) -> str:
        """
        Generates a query for selecting a block of data from `table_name` per the
        block_data parameters.

        :param table_name: Table name.
        :param block_data: Dictionary containing key value pairs for the column name
          for blocking and the data for the incoming record, e.g., ["ZIP"]: "90210".
        :return: Query to select block of data base on `block_data` parameters.

        """
        # TODO: Update queries for nested values, e.g., zip within address
        query_stub = f"SELECT * FROM {table_name} WHERE "
        block_query = " AND ".join(
            [
                f"patient_resource->>'{key}' = '{value}'"
                if type(value) == str
                else (f"'{key}' = {value}")
                for key, value in block_data.items()
            ]
        )
        query = query_stub + block_query + ";"
        return query
