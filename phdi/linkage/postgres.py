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
        external_person_id_table: str,
        external_source_table: str,
    ) -> None:
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.patient_table = patient_table
        self.person_table = person_table
        self.external_person_id_table = external_person_id_table
        self.external_source_table = external_source_table
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
        external_source_name=None,
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
        :param external_source_name: An optional string indicating the name of the
          external system that generated the external ID supplied with the incoming
          record. Defaults to None.
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
                        external_source_name=external_source_name,
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
        external_source_name: str = None,
    ) -> tuple:
        """
        Manages person insertions into the MPI, taking account of supplied
        external information (IDs and sources). This function is called when
        deciding how to link a new, incoming patient to previously created
        person clusters.

        First, if a call is made in which external_person_id and external_source_name
        are both provided, the function queries the MPI to see if there exists
        a person we've already seen that possess this unique combination of
        ID and source. If yes, the incoming patient is assumed to link directly
        to this previously-seen person (due to external linkage or identifiers),
        so the person_id from this combination is automatically assigned.

        Second, if the supplied combination of external_person_id and
        source_name didn't match to a known combination--or if none were
        provided--the function moves to manual person_id handling. If a person_id
        is supplied by the caller (meaning the incoming record matched against
        a person cluster in the `link_against_mpi` function), this function
        uses that person_id. If an ID is not supplied, the function creates a
        new person in the MPI and uses its newly-generated person_id.

        Finally, if external information was provided but didn't match a known
        signature, a new external_source is created (if needed) to accomodate
        the passed-in external_source_name. Then, the function creates a new
        row in the external_person_ids table that combines the newly-created
        external_source, the passed-in or determined person_id, and the passed-in
        external_person_id.

        :param person_id: The person id for the person record to be inserted
          or updated, defaults to None.
        :param external_person_id: The external person id for the person record
          to be inserted or updated, defaults to None.
        :param external_source_name: An optional string indicating the name of
          the external system that generated the external ID supplied with the
          incoming record. Defaults to None.
        :return: A tuple of two values; the person id either supplied or
          auto-generated and a boolean that indicates if there was a match
          found within the person table or not based upon the external person id
        """
        matched = False
        try:
            # Require both pieces of information to process an external identifier
            if external_person_id is None or external_source_name is None:
                external_person_id = "'NULL'"
                external_source_name = "'NULL'"

            # Step 1: check whether an incoming patient maps to a person we've
            # processed that has the same external ID and source of that ID--if yes,
            # use that mapped person ID and we're done
            else:
                person_query = SQL(
                    "SELECT person_id, external_source_key FROM {external_person_id_table} WHERE external_person_id = %s"  # noqa
                ).format(
                    external_person_id_table=Identifier(self.external_person_id_table)
                )
                query_data = [external_person_id]

                # First query gets the person_id and key of this external ID's source
                db_cursor.execute(person_query, query_data)
                returned_data = db_cursor.fetchall()

                # Second query verifies that source of external ID in the MPI
                # matches source of external ID passed with incoming patient
                if returned_data is not None and len(returned_data) > 0:
                    found_person_id = returned_data[0][0]
                    found_external_source_key = returned_data[0][1]

                    # Build the query using the previously found primary key of the external
                    # source to look up its name in the MPI
                    source_query = SQL(
                        "SELECT external_source_name FROM {external_source_table} WHERE external_source_key = %s"  # noqa
                    ).format(
                        external_source_table=Identifier(self.external_source_table)
                    )
                    query_data = [found_external_source_key]
                    db_cursor.execute(source_query, query_data)
                    returned_data = db_cursor.fetchall()

                    # Now compare this found name to the name we were passed
                    # If they agree, this is a case 1 match and we use the person
                    if returned_data is not None and len(returned_data) > 0:
                        found_source_name = returned_data[0][0]
                        if found_source_name == external_source_name:
                            matched = True
                            return matched, found_person_id

            # Step 2: we couldn't match the incoming patient to a processed person
            # with matching external info, so we'll need to use a different
            # person_id
            if person_id is None:
                # We'll use a newly created person_id if the incoming patient wasn't
                # passed with an existing person_id (meaning it had no matches)
                insert_new_person = SQL(
                    "INSERT INTO {person_table} VALUES (default) RETURNING person_id;"
                ).format(person_table=Identifier(self.person_table))
                db_cursor.execute(insert_new_person)

                # Retrieve newly generated person_id
                person_id = db_cursor.fetchall()[0][0]

            # Or, if a person_id was passed, then we'll use that instead
            else:
                # No need to change person_id or update any other records
                matched = True

            # Step 3: if external info (ID + source name) was passed and we
            # got here, we didn't find any other patients with that same
            # combination of external ID and source, so write a new row in
            # the external tables to track this
            if external_person_id != "'NULL'" and external_source_name != "'NULL'":
                # Check if we need to create a new external source
                source_query = SQL(
                    "SELECT external_source_key FROM {external_source_table} WHERE external_source_name = %s"  # noqa
                ).format(external_source_table=Identifier(self.external_source_table))
                query_data = [external_source_name]
                db_cursor.execute(source_query, query_data)
                returned_data = db_cursor.fetchall()

                # Add new source row if none exists
                if returned_data is None or len(returned_data) == 0:
                    insert_new_source = SQL(
                        "INSERT INTO {external_source_table} (external_source_name) VALUES (%s) RETURNING external_source_key;"  # noqa
                    ).format(
                        external_source_table=Identifier(self.external_source_table)
                    )
                    source_data = [external_source_name]
                    db_cursor.execute(insert_new_source, source_data)
                    source_key = db_cursor.fetchall()[0][0]

                # Otherwise grab the UUID of this external source to reference it
                else:
                    source_key = returned_data[0][0]

                # Now insert a row into the table of external_ids representing
                # this unique combination of person, external id, and source
                insert_new_external_id = SQL(
                    "INSERT INTO {external_ids_table} (person_id, external_person_id, external_source_key) VALUES (%s, %s, %s);"  # noqa
                ).format(external_ids_table=Identifier(self.external_person_id_table))
                external_data = [person_id, external_person_id, source_key]
                db_cursor.execute(insert_new_external_id, external_data)

        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")
        return matched, person_id
