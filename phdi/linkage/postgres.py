from typing import List, Dict, Union, Tuple
from phdi.linkage.core import BaseMPIConnectorClient
import psycopg2
from psycopg2.sql import Identifier, SQL
from psycopg2.extensions import connection, cursor
import json


class DIBBsConnectorClient(BaseMPIConnectorClient):
    """
    Represents a Postgres-specific Master Patient Index (MPI) connector
    client for the DIBBs implementation of the record linkage building
    block. Callers should use the provided interface functions (e.g.,
    block_vals) to interact with the underlying vendor-specific client
    property.

    When instantiating a DIBBSConnectorClient, the connection to the
    database is automatically tested using the provided parameters.
    A refused, timed-out, or otherwise error-ed connection will raise
    an immediate exception.
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
            "address": """$.address[*].line""",
            "birthdate": "$.birthDate",
            "city": """$.address[*].city""",
            "first_name": """$.name[*].given""",
            "last_name": """$.name[*].family""",
            "mrn": """$.identifier.value""",
            "sex": "$.gender",
            "state": """$.address[*].state""",
            "zip": """$.address[*].postalCode""",
        }
        db_conn = self.get_connection()
        self._close_connections(db_conn=db_conn)

    def get_connection(self) -> Union[connection, None]:
        """
        Simple method for initiating a connection to the database specified
        by the parameters given to the class' instantiation.
        """
        db_conn = None
        try:
            db_conn = psycopg2.connect(
                database=self.database,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")
        finally:
            return db_conn

    def block_data(self, block_vals: Dict) -> List[list]:
        """
        Returns a list of lists containing records from the database that match on the
        incoming record's block values. If blocking on 'ZIP' and the incoming record's
        zip code is '90210', the resulting block of data would contain records that all
        have the same zip code of 90210.

        :param block_vals: Dictionary containing key value pairs for the column name for
          blocking and the data for the incoming record as well as any transformations,
          e.g., {"ZIP": {"value": "90210"}} or
          {"ZIP": {"value": "90210",}, "transformation":"first4"}.
        :return: A list of records that are within the block, e.g., records that all
          have 90210 as their ZIP.
        """
        if len(block_vals) == 0:
            raise ValueError("`block_vals` cannot be empty.")

        db_cursor = None
        db_conn = None
        try:
            # Use context manager to handle commits and transactions
            with self.get_connection() as db_conn:
                with db_conn.cursor() as db_cursor:
                    # Generate raw SQL query

                    query, data = self._generate_block_query(block_vals)
                    # Execute query
                    db_cursor.execute(query, data)
                    blocked_data = [list(row) for row in db_cursor.fetchall()]

        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")

        finally:
            self._close_connections(db_conn=db_conn, db_cursor=db_cursor)

        # Set up blocked data by adding column headers as 1st row of LoL
        # TODO: Replace indices with column names for reability
        blocked_data_cols = ["patient_id", "person_id"]
        for key in sorted(list(self.fields_to_jsonpaths.keys())):
            blocked_data_cols.append(key)
        blocked_data.insert(0, blocked_data_cols)

        return blocked_data

    def insert_match_patient(
        self,
        patient_resource: Dict,
        person_id=None,
    ) -> Union[None, str]:
        """
        If a matching person ID has been found in the MPI, inserts a new patient into
        the patient table and updates the person table to link to the new patient; else
        inserts a new patient into the patient table and inserts a new person into the
        person table with a new personID, linking the new personID to the new patient.

        :param patient_resource: A FHIR patient resource.
        :param person_id: The personID matching the patient record if a match has been
          found in the MPI, defaults to None.
        """
        db_cursor = None
        db_conn = None
        try:
            # Use context manager to handle commits and transactions
            with self.get_connection() as db_conn:
                with db_conn.cursor() as db_cursor:
                    # Match has not been found
                    if person_id is None:
                        # Insert a new record into person table to generate new
                        # person_id
                        insert_new_person = SQL(
                            "INSERT INTO {person_table} (external_person_id) VALUES "
                            "('NULL') RETURNING person_id;"
                        ).format(person_table=Identifier(self.person_table))

                        db_cursor.execute(insert_new_person)

                        # Retrieve newly generated person_id
                        person_id = db_cursor.fetchall()[0][0]

                    # Insert into patient table
                    insert_new_patient = SQL(
                        "INSERT INTO {patient_table} "
                        "(patient_id, person_id, patient_resource) VALUES (%s, %s, %s);"
                    ).format(patient_table=Identifier(self.patient_table))
                    data = [
                        patient_resource.get("id"),
                        person_id,
                        json.dumps(patient_resource),
                    ]
                    db_cursor.execute(insert_new_patient, data)

        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")

        finally:
            self._close_connections(db_conn=db_conn, db_cursor=db_cursor)

        return person_id

    def _generate_block_query(self, block_vals: dict) -> Tuple[SQL, list[str]]:
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
        :return: A tuple containing a psycopg2.sql.SQL object representing the query as
            well as list of all data to be inserted into it.

        """
        # Check whether `block_vals` contains supported keys
        for key in block_vals:
            if key not in self.fields_to_jsonpaths:
                raise ValueError(
                    f"""`{key}` not supported for blocking at this time. Supported
                    columns include first_name, last_name, birthdate, address, city,
                    state, zip, mrn, and sex."""
                )

        # Generate select query to extract fields_to_jsonpaths keys
        select_query_stubs = []
        select_query_stubs_data = []
        for key in self.fields_to_jsonpaths:
            query = f"jsonb_path_query_array(patient_resource,%s) as {key}"
            select_query_stubs.append(query)
            select_query_stubs_data.append(self.fields_to_jsonpaths[key])
        select_query = "SELECT patient_id, person_id, " + ", ".join(
            stub for stub in select_query_stubs
        )

        # Generate blocking query based on blocking criteria
        block_query_stubs = []
        block_query_stubs_data = []
        for col_name, param in block_vals.items():
            query = (
                "CAST(jsonb_path_query_array(patient_resource, %s) as VARCHAR)= "
                "'[true]'"
            )
            block_query_stubs.append(query)
            # Add appropriate transformations
            if "transformation" in param:
                # first4 transformations
                if block_vals[col_name]["transformation"] == "first4":
                    block_query_stubs_data.append(
                        f"{self.fields_to_jsonpaths[col_name]} starts with "
                        f'"{block_vals[col_name]["value"]}"'
                    )
                # last4 transformations
                else:
                    block_query_stubs_data.append(
                        f"{self.fields_to_jsonpaths[col_name]} like_regex "
                        f'"{block_vals[col_name]["value"]}$$"'
                    )
            # Build query for columns without transformations
            else:
                block_query_stubs_data.append(
                    f"{self.fields_to_jsonpaths[col_name]} like_regex "
                    f'"{block_vals[col_name]["value"]}"'
                )

        block_query = " WHERE " + " AND ".join(stub for stub in block_query_stubs)

        query = select_query + " FROM {patient_table}" + block_query + ";"
        query = SQL(query).format(patient_table=Identifier(self.patient_table))
        data = select_query_stubs_data + block_query_stubs_data

        return query, data

    def _close_connections(
        self,
        db_conn: Union[connection, None] = None,
        db_cursor: Union[cursor, None] = None,
    ) -> None:
        """
        Simple helper method to close passed connections. If a context manager's
        `with` block successfully executes, the connection will already be
        committed and closed, so the resource will already be released. However,
        if the `with` block terminates before safe execution, this function
        allows a `finally` clause to succinctly clean up all open connections.
        """
        if db_cursor is not None:
            db_cursor.close()
        if db_conn is not None:
            db_conn.close()
