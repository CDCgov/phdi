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

        fields_to_jsonpaths = {
            "first_name": """'$.name[*] ?(@.use=="official").given'""",
            "last_name": """'$.name ?(@.use=="official").family'""",
            "birthdate": "'$.birthDate'",
            "address": """'$.address[*] ?(@.use=="home").line'""",
            "city": """'$.address[*] ?(@.use=="home").city'""",
            "state": """'$.address[*] ?(@.use=="home").state'""",
            "zip": """'$.address[*] ?(@.use=="home").postalCode'""",
            "sex": "'$.gender'",
            "mrn": """'$.identifier ?(@.type.coding[0].code=="MR").value'""",
        }

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
            raise ValueError("`block_data` cannot be empty.")

        # Generate raw SQL query
        query = self._generate_block_query(self.patient_table, block_vals)

        # Execute query
        self.cursor.execute(query)
        extracted_data = self.cursor.fetchall()

        # Close cursor and connection
        self.cursor.close()
        self.connection.close()

        # Set up blocked data by adding column headers as 1st row of LoL
        # TODO: Replace indices with column names for reability
        blocked_data = [["patient_id", "person_id"]]
        for key in sorted(list(fields_to_dictpaths.keys())):
            blocked_data[0].append(key)

        # Unnest patient_resource data
        for row in extracted_data:
            row_data = [row[0], row[1]]
            for value in sorted(list(fields_to_dictpaths.keys())):
                row_data.append(fields_to_dictpaths[value])
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

            return person_id[0][0]

    def _generate_block_query(self, table_name: str, block_vals: Dict) -> str:
        """
        Generates a query for selecting a block of data from `table_name` per the
        block_data parameters. Accepted blocking fields include: first_name, last_name,
        birthdate, addess, city, state, zip, and sex

        :param table_name: Table name.
        :param block_vals: Dictionary containing key value pairs for the column name for
          blocking and the data for the incoming record as well as any transformations,
          e.g., {["ZIP"]: {"value": "90210"}} or
          {["ZIP"]: {"value": "90210",}, "transformation":"first4"}.
        :raises ValueError: If column key in `block_vals` is not supported.
        :return: Query to select block of data base on `block_vals` parameters.

        """
        # TODO: Add MRN to fields_to_jsonpaths
        fields_to_jsonpaths = {
            "address": """'$.address[*] ?(@.use=="home").line'""",
            "birthdate": "'$.birthDate'",
            "city": """'$.address[*] ?(@.use=="home").city'""",
            "first_name": """'$.name[*] ?(@.use=="official").given'""",
            "last_name": """'$.name ?(@.use=="official").family'""",
            "mrn": """'$.identifier ?(@.type.coding[0].code=="MR").value'""",
            "sex": "'$.gender'",
            "state": """'$.address[*] ?(@.use=="home").state'""",
            "zip": """'$.address[*] ?(@.use=="home").postalCode'""",
        }

        # Check whether `block_vals` contains supported keys
        for key in block_vals.keys():
            if key not in fields_to_jsonpaths.keys():
                raise ValueError(
                    f"""`{key}` not supported for blocking at this time. Supported
                    columns include first_name, last_name, birthdate, address, city,
                    state, zip, and sex."""
                )

        query_stub = "SELECT "
        select_query = ", ".join(
            f"jsonb_path_query(patient_resource,{fields_to_jsonpaths[field]} as {field}"
            if field != "mrn"
            else (
                f"""jsonb_path_query_array(patient_resource,
                {fields_to_jsonpaths[field]} as {field}"""
            )
            for field in fields_to_jsonpaths.keys()
        )
        block_query = " AND ".join(
            [
                f"patient_resource#>>{fields_to_jsonpaths[key]} ? '{value}'"
                if type(value) == str
                else (f"{fields_to_jsonpaths[key]} = {value}")
                for key, value in block_vals.items()
            ]
        )
        query = query_stub + block_query + ";"
        return query
