from typing import List, Dict, Union, Tuple
from phdi.linkage.core import BaseMPIConnectorClient
import psycopg2
from psycopg2.sql import Identifier, SQL
from psycopg2.extensions import connection, cursor
import json
import logging


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
            "mrn": """$.identifier ?(@.type.coding[0].code=="MR").value""",
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
        external_person_id=None,
    ) -> Union[None, tuple]:
        """
        If a matching person ID has been found in the MPI, inserts a new patient into
        the patient table, including the matched person id, to link the new patient
        and matched person ID; else inserts a new patient into the patient table and
        inserts a new person into the person table with a new person ID, linking the
        new person ID to the new patient.

        :param patient_resource: A FHIR patient resource.
        :param person_id: The person ID matching the patient record if a match has been
          found in the MPI, defaults to None.
        :param external_person_id: The external person id for the person that matches
          the patient record if a match has been found in the MPI, defaults to None.
        :return: the person id
        """
        matched = False
        db_cursor = None
        db_conn = None
        try:
            # Use context manager to handle commits and transactions
            with self.get_connection() as db_conn:
                with db_conn.cursor() as db_cursor:
                    # handle all logic whether to insert, update
                    # or query to get an existing person record
                    # then use the returned person_id to link
                    #  to the newly create patient
                    matched, person_id = self._insert_person(
                        db_cursor=db_cursor,
                        person_id=person_id,
                        external_person_id=external_person_id,
                    )

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
                    try:
                        db_cursor.execute(insert_new_patient, data)
                    except psycopg2.errors.UniqueViolation:
                        logging.warning(
                            f"Patient with ID {patient_resource.get('id')} already "
                            "exists in the MPI. The patient table was not updated."
                        )

        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")

        finally:
            self._close_connections(db_conn=db_conn, db_cursor=db_cursor)

        return (matched, person_id)

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

    def _insert_person(
        self,
        db_cursor: Union[cursor, None] = None,
        person_id: str = None,
        external_person_id: str = None,
    ) -> tuple:
        """
        If person id is not supplied and external person id is not supplied
        then insert a new person record with an auto-generated person id (UUID)
        with a Null external person id and return that new person id. If the
        person id is not supplied but an external person id is supplied try
        to find an existing person record with the external person id and
        return that person id; otherwise add a new person record with an
        auto-generated person id (UUID) with the supplied external person id
        and return the new person id.  If person id and external person id are
        both supplied then update the person records external person id if it
        is Null and return the person id.

        :param person_id: The person id for the person record to be inserted
          or updated, defaults to None.
        :param external_person_id: The external person id for the person record
          to be inserted or updated, defaults to None.
        :return: A tuple of two values; the person id either supplied or
          auto-generated and a boolean that indicates if there was a match
          found within the person table or not based upon the external person id
        """
        matched = False
        try:
            if external_person_id is None:
                external_person_id = "'NULL'"
            else:
                # if external person id is supplied then find if there is already
                #  a person with that external person id already within the MPI
                #  - if so, return that person id
                person_query = SQL(
                    "SELECT person_id FROM {person_table} WHERE external_person_id = %s"
                ).format(person_table=Identifier(self.person_table))
                query_data = [external_person_id]
                db_cursor.execute(person_query, query_data)
                # Retrieve person_id that has the supplied external_person_id
                returned_data = db_cursor.fetchall()

                if returned_data is not None and len(returned_data) > 0:
                    found_person_id = returned_data[0][0]
                    matched = True
                    return matched, found_person_id

            if person_id is None:
                # Insert a new record into person table to generate new
                # person_id with either the supplied external person id
                #  or a null external person id
                insert_new_person = SQL(
                    "INSERT INTO {person_table} (external_person_id) VALUES "
                    "(%s) RETURNING person_id;"
                ).format(person_table=Identifier(self.person_table))
                person_data = [external_person_id]

                db_cursor.execute(insert_new_person, person_data)

                # Retrieve newly generated person_id
                person_id = db_cursor.fetchall()[0][0]
            # otherwise if person id is supplied and the external person id is supplied
            # and not none and a record with the external person id was not found
            #  then update the person record with the supplied external person id
            elif person_id is not None and external_person_id != "'NULL'":
                matched = True
                update_person_query = SQL(
                    "UPDATE {person_table} SET external_person_id = %s "
                    "WHERE person_id = %s AND external_person_id = 'NULL' "
                ).format(person_table=Identifier(self.person_table))
                update_data = [external_person_id, person_id]
                db_cursor.execute(update_person_query, update_data)

        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")
        return matched, person_id
