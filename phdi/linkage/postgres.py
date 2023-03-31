from typing import List, Dict
from phdi.linkage.core import BaseMPIConnectorClient
import psycopg2
import json


class PostgresConnectorClient(BaseMPIConnectorClient):
    """
    Represents a Postgres-specific Master Patient Index (MPI) connector client.
    Callers should use the provided interface functions (e.g., block_vals)
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
        self.fields_to_jsonpaths = {
            "address": """$.address[*] ?(@.use=="home").line""",
            "birthdate": "$.birthDate",
            "city": """$.address[*] ?(@.use=="home").city""",
            "first_name": """$.name[*] ?(@.use=="official").given""",
            "last_name": """$.name[*] ?(@.use=="official").family""",
            "mrn": """$.identifier ?(@.type.coding[0].code=="MR").value""",
            "sex": "$.gender",
            "state": """$.address[*] ?(@.use=="home").state""",
            "zip": """$.address[*] ?(@.use=="home").postalCode""",
        }

    def block_data(self, block_vals: Dict) -> List[list]:
        """
        Returns a list of lists containing records from the database that match on the
        incoming record's block values. If blocking on 'ZIP' and the incoming record's
        zip code is '90210', the resulting block of data would contain records that all
        have the same zip code of 90210.

        :param block_vals: Dictionary containing key value pairs for the column name for
          blocking and the data for the incoming record as well as any transformations,
          e.g., {["ZIP"]: {"value": "90210"}} or
          {["ZIP"]: {"value": "90210",}, "transformation":"first4"}.
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

        if len(block_vals) == 0:
            raise ValueError("`block_vals` cannot be empty.")

        # Generate raw SQL query
        query = self._generate_block_query(block_vals)

        # Execute query
        self.cursor.execute(query)
        blocked_data = [list(row) for row in self.cursor.fetchall()]

        # Close cursor and connection
        self.cursor.close()
        self.connection.close()

        # Set up blocked data by adding column headers as 1st row of LoL
        # TODO: Replace indices with column names for reability
        blocked_data_cols = ["patient_id", "person_id"]
        for key in sorted(list(self.fields_to_jsonpaths.keys())):
            blocked_data_cols.append(key)
        blocked_data.insert(0, blocked_data_cols)

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

            return person_id[0][0]

    def _generate_block_query(self, block_vals: dict) -> str:
        """
        Generates a query for selecting a block of data from the patient table per the
        block_vals parameters. Accepted blocking fields include: first_name, last_name,
        birthdate, addess, city, state, zip, mrn, and sex.

        :param table_name: Table name.
        :param block_vals: Dictionary containing key value pairs for the column name for
          blocking and the data for the incoming record as well as any transformations,
          e.g., {["ZIP"]: {"value": "90210"}} or
          {["ZIP"]: {"value": "90210",}, "transformation":"first4"}.
        :raises ValueError: If column key in `block_vals` is not supported.
        :return: Query to select block of data base on `block_vals` parameters.

        """
        # Check whether `block_vals` contains supported keys
        for key in block_vals.keys():
            if key not in self.fields_to_jsonpaths.keys():
                raise ValueError(
                    f"""`{key}` not supported for blocking at this time. Supported
                    columns include first_name, last_name, birthdate, address, city,
                    state, zip, mrn, and sex."""
                )

        # Generate select query to extract fields_to_jsonpaths keys
        select_query_stubs = []
        for col_name in self.fields_to_jsonpaths.keys():
            query = f"""jsonb_path_query_array(patient_resource,
                '{self.fields_to_jsonpaths[col_name]}') as {col_name}"""
            select_query_stubs.append(query)
        select_query = "SELECT patient_id, person_id, " + ", ".join(
            stub for stub in select_query_stubs
        )

        # Generate blocking query based on blocking criteria
        block_query_stubs = []
        for col_name, param in block_vals.items():
            # Add appropriate transformations
            if "transformation" in param.keys():
                # first4 transformations
                if block_vals[col_name]["transformation"] == "first4":
                    query = f"""
                        CAST(jsonb_path_query_array(patient_resource,
                        '{self.fields_to_jsonpaths[col_name]} starts with
                        "{block_vals[col_name]["value"]}"') as VARCHAR)
                        = '[true]'"""
                # last4 transformations
                else:
                    query = f"""
                        CAST(jsonb_path_query_array(patient_resource,
                        '{self.fields_to_jsonpaths[col_name]} like_regex
                        "{block_vals[col_name]["value"]}$$"') as VARCHAR)
                        = '[true]'"""

            # Build query for columns without transformations
            else:
                query = f"""CAST(jsonb_path_query_array(patient_resource,
                        '{self.fields_to_jsonpaths[col_name]} like_regex
                        "{block_vals[col_name]["value"]}"') as VARCHAR)
                        = '[true]'"""
            block_query_stubs.append(query)

        block_query = " WHERE " + " AND ".join(stub for stub in block_query_stubs)

        query = select_query + f" FROM {self.patient_table}" + block_query + ";"
        return query
