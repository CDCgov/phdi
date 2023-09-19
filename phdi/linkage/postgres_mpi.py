from typing import List, Dict, Union
from sqlalchemy import Table, select, text
from phdi.linkage.core import BaseMPIConnectorClient
from sqlalchemy.orm import Query
from phdi.linkage.utils import load_mpi_env_vars_os
from phdi.linkage.dal import PGDataAccessLayer


class PGMPIConnectorClient(BaseMPIConnectorClient):
    """
    Represents a Postgres-specific Master Patient Index (MPI) connector
    client for the DIBBs implementation of the record linkage building
    block. Callers should use the provided interface functions (e.g.,
    block_vals) to interact with the underlying vendor-specific client
    property.

    """

    def __init__(self):
        dbsettings = load_mpi_env_vars_os()
        dbuser = dbsettings.get("user")
        dbname = dbsettings.get("dbname")
        dbpwd = dbsettings.get("password")
        dbhost = dbsettings.get("host")
        dbport = dbsettings.get("port")
        self.dal = PGDataAccessLayer()
        self.dal.get_connection(
            engine_url=f"postgresql+psycopg2://{dbuser}:"
            + f"{dbpwd}@{dbhost}:{dbport}/{dbname}"
        )

    def _initialize_schema(self):
        self.dal.initialize_schema()

    # TODO: remove this from here and from core, it shouldn't be needed
    # it is here now just to satisfy the interface of core.py
    def get_connection(self) -> Union[any, None]:
        return self.dal.get_session()

    def block_data(self, block_vals: Dict) -> List[list]:
        # TODO: This comment may need to be updated with the changes made

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

        # Generate ORM query using block_vals as criteria
        query = select(self.dal.PATIENT_TABLE)

        # now tack on the where criteria using the block_vals
        # while ensuring they exist in the table structure ORM
        query = self._generate_block_query(
            block_vals=block_vals,
            query=query,
            table=self.dal.PATIENT_TABLE,
        )

        blocked_data = self.dal.select_results(select_stmt=query)

        return blocked_data

    def insert_match_patient(
        self,
        patient_resource: Dict,
        person_id=None,
        external_person_id=None,
    ) -> Union[None, tuple]:
        # TODO: This comment may need to be updated with the changes made

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

        # try:
        #     # TODO: use this function from the DAL instead of
        #     # doing manual insert - see commented out code example below
        #     # self.dal.bulk_insert(self.dal.PATIENT_TABLE, patient_record_dict)

        return None

    def _generate_block_query(
        self, block_vals: dict, query: Query, table: Table
    ) -> Query:
        # TODO: This comment may need to be updated with the changes made
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
        :return: A 'Select' statement built by the sqlalchemy ORM

        """

        new_query = None
        where_criteria = []
        table_columns = self._get_table_columns(table)
        for key, value in block_vals.items():
            try:
                col_index = table_columns.index(key)
                for key2, value2 in value.items():
                    if key2 == "value":
                        where_criteria.append(
                            f"{table.name}.{table_columns[col_index]} = '{value2}'"
                        )
            except ValueError as err:
                print(err)
                continue
        new_query = query.where(text(" AND ".join(where_criteria)))

        return new_query

    def _get_table_columns(self, table: Table) -> List:
        columns = []
        for col in table.c:
            columns.append(str(col).split(".")[1])

        return columns

    def _insert_person(
        self,
        person_id: str = None,
        external_person_id: str = None,
    ) -> tuple:
        # TODO: This comment may need to be updated with the changes made

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
        # # TODO: use the DAL to perform this going forward

        return None
