import copy
import datetime
import logging
import uuid
from functools import cache
from typing import Dict
from typing import List
from typing import Literal

from sqlalchemy import and_
from sqlalchemy import Select
from sqlalchemy import select
from sqlalchemy import text

from phdi.fhir.utils import extract_value_with_resource_path
from phdi.linkage.core import BaseMPIConnectorClient
from phdi.linkage.dal import DataAccessLayer
from phdi.linkage.utils import load_mpi_env_vars_os


class DIBBsMPIConnectorClient(BaseMPIConnectorClient):
    """
    Represents a Postgres-specific Master Patient Index (MPI) connector
    client for the DIBBs implementation of the record linkage building
    block. Callers should use the provided interface functions (e.g.,
    block_vals) to interact with the underlying vendor-specific client
    property.

    """

    def __init__(self, pool_size: int = 5, max_overflow: int = 10):
        """
        Initialize the MPI connector client with the MPI database.
        :param pool_size: The number of connections to keep open to the database.
        :param max_overflow: The number of connections to allow in connection pool.
        """
        dbsettings = load_mpi_env_vars_os()
        dbuser = dbsettings.get("user")
        dbname = dbsettings.get("dbname")
        dbpwd = dbsettings.get("password")
        dbhost = dbsettings.get("host")
        dbport = dbsettings.get("port")
        self.dal = DataAccessLayer()
        self.dal.get_connection(
            engine_url=f"postgresql+psycopg2://{dbuser}:"
            + f"{dbpwd}@{dbhost}:{dbport}/{dbname}",
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.dal.initialize_schema()
        self.column_to_fhirpaths = {
            "patient": {
                "root_path": "Patient",
                "fields": {
                    "patient_id": "id",
                    "person_id": "person",
                    "dob": "birthDate",
                    "sex": "gender",
                    "race": """
                        extension.where(url =
                         'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race')
                        .extension.valueCoding.display""",
                    "ethnicity": """
                    extension.where(url =
                    'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity')
                    .extension.valueCoding.display""",
                },
            },
            "name": {
                "root_path": "Patient.name",
                "fields": {
                    "last_name": "family",
                    "given_name": "given",
                    "type": "use",
                },
            },
            "phone_number": {
                "root_path": "Patient.telecom.where(system='phone')",
                "fields": {
                    "phone_number": "value",
                    "start_date": "period.start",
                    "end_date": "period.end",
                    "type": "use",
                },
            },
            "address": {
                "root_path": "Patient.address",
                "fields": {
                    "line_1": "line[0]",
                    "line_2": "line[1]",
                    "city": "city",
                    "state": "state",
                    "zip_code": "postalCode",
                    "country": "country",
                    "latitude": """
                        extension.where(url =
                          'http://hl7.org/fhir/StructureDefinition/geolocation')
                        .extension.where(url = 'latitude').valueDecimal""",
                    "longitude": """extension.where(url =
                          'http://hl7.org/fhir/StructureDefinition/geolocation')
                          .extension.where(url = 'longitude').valueDecimal""",
                    "type": "use",
                    "start_date": "period.start",
                    "end_date": "period.end",
                },
            },
            "identifier": {
                "root_path": "Patient.identifier",
                "fields": {
                    "patient_identifier": "value",
                    "type_code": "type.coding[0].code",
                    "type_display": "type.coding[0].display",
                    "type_system": "type.coding[0].system",
                },
            },
        }

    def get_block_data(self, block_criteria: Dict) -> List[list]:
        """
        Returns a list of lists containing records from the MPI database that
        match on the incoming record's block criteria and values. If blocking
        on 'ZIP' and the incoming record's ip code is '90210', the resulting
        block of data would contain records that all
        have the same zip code of 90210.

        :param block_criteria: Dictionary containing key value pairs
            for the column name for blocking and the data for the
            incoming record as well as any transformations,
          e.g., {"ZIP": {"value": "90210"}} or
          {"ZIP": {"value": "90210",}, "transformation":"first4"}.
        :return: A list of records that are within the block, e.g.,
            records that all have 90210 as their ZIP.
        """
        logging.info("In get_block_data")
        if len(block_criteria) == 0:
            raise ValueError("`block_vals` cannot be empty.")

        # Get the base query that will select all necessary
        # columns for linkage with some basic filtering
        logging.info(
            f"Starting _get_base_query at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        query = self._get_base_query()
        logging.info(
            f"Done with _get_base_query at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )

        # now get the criteria organized by table so the
        # CTE queries can be constructed and then added
        # to the base query
        logging.info(
            f"Starting _organize_block_criteria at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        organized_block_vals = self._organize_block_criteria(block_criteria)
        logging.info(
            f"Done with _organize_block_criteria at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}",  # noqa
        )

        # now tack on the where criteria using the block_vals
        # while ensuring they exist in the table structure ORM
        logging.info(
            f"Starting _generate_block_query at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        query_w_ctes = self._generate_block_query(
            organized_block_criteria=organized_block_vals, query=query
        )
        logging.info(
            f"Done with _generate_block_query at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        logging.info(
            f"Starting dal.select_results at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        blocked_data = self.dal.select_results(
            select_statement=query_w_ctes, include_col_header=True
        )
        logging.info(
            f"Done with dal.select_results at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )

        return blocked_data

    def insert_matched_patient(
        self,
        patient_resource: Dict,
        person_id=None,
        external_person_id=None,
    ) -> str:
        """
        If a matching person ID has been found in the MPI, inserts a new patient into
        the patient table and all other subsequent MPI tables, including the
        matched person id, to link the new patient and matched person ID;
        else inserts a new patient into the patient table, as well as all other
        subsequent MPI tables, and inserts a new person into the person table
        linking the new person to the new patient.

        :param patient_resource: A FHIR patient resource.
        :param person_id: The person ID matching the patient record if a match has been
          found in the MPI, defaults to None.
        :param external_person_id: The external person id for the person that matches
          the patient record if a match has been found in the MPI, defaults to None.
        """
        logging.info(
            f"Starting insert_matched_patient at {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )

        try:
            if person_id is None:
                logging.info(
                    f"person_id was None; starting _insert_person at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                )
                person_id = self._insert_person()
                logging.info(
                    f"person_id was None; done with _insert_person at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                )
            patient_resource["person"] = person_id
            logging.info(
                f"Starting _get_mpi_records at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
            mpi_records = self._get_mpi_records(patient_resource)
            logging.info(
                f"Done with _get_mpi_records at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
            logging.info(
                f"Starting dal.bulk_insert_dict at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
            self.dal.bulk_insert_dict(
                records_with_table=mpi_records, return_primary_keys=False
            )
            logging.info(
                f"Done with dal.bulk_insert_dict at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )

            if external_person_id is not None:
                logging.info(
                    f"""external_person_id was not None;
                      starting _insert_external_person_id at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                )
                self._insert_external_person_id(person_id, external_person_id)
                logging.info(
                    f"""external_person_id was not None;
                      done with _insert_external_person_id at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                )
        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")

        return person_id

    def _generate_where_criteria(self, block_criteria: dict, table_name: str) -> list:
        """
        Generates a list of where criteria leveraging the blocking criteria,
        including transformations such as 'first 4' or 'last 4'.  This
        function leverages the ORM to determine the table and columns.

        :param block_criteria: a dictionary that contains the blocking criteria.
        :return: A list of where criteria used to append to the end of a query.

        """
        where_criteria = []
        for key, value in block_criteria.items():
            criteria_value = value["value"]
            criteria_transform = value.get("transformation", None)

            if criteria_transform is None:
                where_criteria.append(f"{table_name}.{key} = '{criteria_value}'")
            else:
                if criteria_transform == "first4":
                    where_criteria.append(
                        f"LEFT({table_name}.{key},4) = '{criteria_value}'"
                    )
                elif criteria_transform == "last4":
                    where_criteria.append(
                        f"RIGHT({table_name}.{key},4) = '{criteria_value}'"
                    )
        return where_criteria

    def _generate_block_query(
        self, organized_block_criteria: dict, query: Select
    ) -> Select:
        """
        Generates a query for selecting a block of data from the MPI tables per the
        block field criteria.  The block field criteria should be a dictionary
        organized by MPI table name, with the ORM table object, and the blocking
        criteria.

        :param organized_block_vals: a dictionary organized by MPI table name,
            with the ORM table object, and the blocking criteria.
        :return: A 'Select' statement built by the sqlalchemy ORM utilizing
            the blocking criteria.

        """
        new_query = query

        for table_key, table_info in organized_block_criteria.items():
            query_criteria = None
            cte_query = None
            sub_query = None

            cte_query_table = table_info["table"]
            query_criteria = self._generate_where_criteria(
                table_info["criteria"], table_key
            )

            if query_criteria is not None and len(query_criteria) > 0:
                if self.dal.does_table_have_column(cte_query_table, "patient_id"):
                    cte_query = (
                        select(cte_query_table.c.patient_id.label("patient_id"))
                        .where(text(" AND ".join(query_criteria)))
                        .cte(f"{table_key}_cte")
                    )
                else:
                    fk_query_table = copy.deepcopy(cte_query_table)
                    fk_info = fk_query_table.foreign_keys.pop()
                    fk_column = fk_info.column
                    fk_table = fk_info.column.table
                    sub_query = (
                        select(cte_query_table)
                        .where(text(" AND ".join(query_criteria)))
                        .subquery(f"{cte_query_table.name}_cte_subq")
                    )
                    cte_query = (
                        select(fk_table.c.patient_id).join(
                            sub_query,
                            text(
                                f"{fk_table.name}.{fk_column.name} = "
                                + f"{sub_query.name}.{fk_column.name}"
                            ),
                        )
                    ).cte(f"{table_key}_cte")
            if cte_query is not None:
                new_query = new_query.join(
                    cte_query,
                    and_(cte_query.c.patient_id == self.dal.PATIENT_TABLE.c.patient_id),
                )

        return new_query

    def _organize_block_criteria(self, block_fields: dict) -> dict:
        """
        Creates a dictionary with the MPI Table Names as keys
        that also stores the ORM Table Object, for each table,
        as well as the blocking criteria for each of the tables.
        The Table is discovered based upon the blocking columns.
        There is some transformation that occurs between certain
        blocking column criteria and the actual column names.
        Accepted blocking fields include: first_name, last_name,
        birthdate, address line 1, city, state, zip, mrn, and sex.

        :param block_fields: A dictionary that contains the
            configured block fields along with the criteria
            and values for blocking.
        :return: A dictionary organized by table name that
            has the ORM Table Object and all blocking
            criteria and values.
        """
        # Accepted blocking fields include: first_name, last_name,
        # birthdate, address line 1, city, state, zip, mrn, and sex.
        organized_block_vals = {}
        for block_key, block_value in block_fields.items():
            sub_dict = {}
            # TODO: we may find a better way to handle this, but for now
            # just convert the known fields into their proper column counterparts
            if block_key == "address":
                sub_dict["line_1"] = block_value
                table_orm = self.dal.get_table_by_column("line_1")
            elif block_key == "zip":
                sub_dict["zip_code"] = block_value
                table_orm = self.dal.get_table_by_column("zip_code")
            elif block_key == "first_name":
                sub_dict["given_name"] = block_value
                table_orm = self.dal.get_table_by_column("given_name")
            elif block_key == "birthdate":
                sub_dict["dob"] = block_value
                table_orm = self.dal.get_table_by_column("dob")
            elif block_key == "mrn":
                sub_dict["patient_identifier"] = block_value
                # mrn specific criteria
                sub_dict["type_code"] = {"value": "MR"}
                table_orm = self.dal.get_table_by_column("patient_identifier")
            else:
                sub_dict[block_key] = block_value
                table_orm = self.dal.get_table_by_column(block_key)
            if table_orm is not None:
                if table_orm.name in organized_block_vals.keys():
                    organized_block_vals[table_orm.name]["criteria"].update(sub_dict)
                else:
                    organized_block_vals[table_orm.name] = {
                        "table": table_orm,
                        "criteria": sub_dict,
                    }
            else:
                continue
        return organized_block_vals

    def _get_base_query(self) -> Select:
        """
        Generates a select query that pulls all the relevant
        MPI records from the MPI tables, using an ORM, for
        Patient Matching/Blocking.

        :return: A single select statement queries all relevant
            blocking columns and tables from the MPI.
        """

        id_sub_query = (
            select(
                self.dal.ID_TABLE.c.patient_identifier.label("mrn"),
                self.dal.ID_TABLE.c.patient_id.label("patient_id"),
            )
            .where(self.dal.ID_TABLE.c.type_code == "MR")
            .subquery("ident_subq")
        )

        # TODO: keeping this here for the time
        # when we decide to add phone numbers into
        # the blocking data
        #
        #  phone_sub_query = (
        #     select(
        #         self.dal.PHONE_TABLE.c.phone_number.label("phone_number"),
        #         self.dal.PHONE_TABLE.c.type.label("phone_type"),
        #         self.dal.PHONE_TABLE.c.patient_id.label("patient_id"),
        #     )
        #     .where(self.dal.PHONE_TABLE.c.type.in_(["home", "cell"]))
        #     .subquery()
        # )

        query = (
            select(
                self.dal.PATIENT_TABLE.c.patient_id,
                self.dal.PATIENT_TABLE.c.person_id,
                self.dal.PATIENT_TABLE.c.dob.label("birthdate"),
                self.dal.PATIENT_TABLE.c.sex,
                id_sub_query.c.mrn,
                self.dal.NAME_TABLE.c.last_name,
                self.dal.GIVEN_NAME_TABLE.c.given_name,
                self.dal.GIVEN_NAME_TABLE.c.given_name_index,
                self.dal.GIVEN_NAME_TABLE.c.name_id,
                # TODO: keeping this here for the time
                # when we decide to add phone numbers into
                # the blocking data
                #
                # phone_sub_query.c.phone_number,
                # phone_sub_query.c.phone_type,
                self.dal.ADDRESS_TABLE.c.line_1.label("address"),
                self.dal.ADDRESS_TABLE.c.zip_code.label("zip"),
                self.dal.ADDRESS_TABLE.c.city,
                self.dal.ADDRESS_TABLE.c.state,
            )
            .outerjoin(
                id_sub_query,
            )
            .outerjoin(self.dal.NAME_TABLE)
            .outerjoin(self.dal.GIVEN_NAME_TABLE)
            # TODO: keeping this here for the time
            # when we decide to add phone numbers into
            # the blocking data
            #
            # .outerjoin(phone_sub_query)
            .outerjoin(self.dal.ADDRESS_TABLE)
        )
        return query

    def _get_mpi_records(self, patient_resource: dict) -> dict:
        """
        Generates a dictionary with the different MPI Table
        Name as keys along with the records for each of the
        MPI Tables, based upon the FHIR Patient Resource data
        passed in.
        There are cases where a direct insert occurs to get
        the primary key, that will be used as a foreign key
        in another MPI Table record.  ie. patient_id is used
        in almost every table, so a patient insert must occur
        first to get the Patient primary key for the other
        MPI table foreign keys.


        :param patient_resource: The FHIR Patient Resource that
            contains patient data to create new MPI records.
        :return: A dictionary of MPI Table names and records.
        """
        records = {}
        if patient_resource["resourceType"] != "Patient":
            return records

        # Check if patient_id exists
        if patient_resource.get("id", None) is None:
            patient_id = uuid.uuid4()
            patient_resource["id"] = patient_id
        else:
            patient_id = patient_resource.get("id")

        for table in self.column_to_fhirpaths.keys():
            table_dict = self.column_to_fhirpaths.get(table)
            table_fields = table_dict.get("fields")

            # Parse root path
            root = extract_value_with_resource_path(
                patient_resource, table_dict.get("root_path"), selection_criteria="all"
            )
            # Parse fields
            table_records = []
            if root is not None:
                for element in root:
                    record = {"patient_id": patient_id}
                    if table == "name":
                        name_id = uuid.uuid4()
                        record["name_id"] = name_id
                    for field in table_fields.keys():
                        selection_criteria = "first"
                        if field == "given_name":
                            selection_criteria = "all"

                        value = extract_value_with_resource_path(
                            element,
                            table_fields.get(field),
                            selection_criteria=selection_criteria,
                        )
                        # Create given_name table in records
                        if field == "given_name":
                            given_name_table_records = self._extract_given_names(
                                value, name_id
                            )
                            if field not in records.keys():
                                records[field] = given_name_table_records
                            else:
                                for given_name_table_record in given_name_table_records:
                                    records[field].append(given_name_table_record)
                            continue
                        record[field] = value

                    table_records.append(record)

            records[table] = table_records

        return records

    def _extract_given_names(self, given_names: list, name_id: uuid) -> dict:
        """
        Separates given_name into it's own table and creates the given_name_index
        ahead of inserting the table into the MPI.

        :param given_names: List of given names.
        :return: List of dictionaries containing entries for the given_name table with
            1 given name and index per row as well as an associated given_name_id.
        """
        table_records = []
        if given_names is not None:
            for idx, name in enumerate(given_names):
                record = {
                    "name_id": name_id,
                    "given_name": name,
                    "given_name_index": idx,
                }
                table_records.append(record)
        else:
            record = {
                "name_id": name_id,
                "given_name": None,
                "given_name_index": 0,
            }
            table_records.append(record)
        return table_records

    def _insert_external_person_id(
        self,
        person_id: str,
        external_person_id: str,
    ):
        """
        Inserts a new external person id record into the MPI if the external_person_id
        does not already exist in the MPI.

        :param person_id: The person_id matching the patient record if a match has been
            found in the MPI.
        :param external_person_id: The external_person_id for the patient record if it
            exists.

        """
        if person_id is None or external_person_id is None:  # pragma: no cover
            raise ValueError("person_id and external_person_id must be provided.")

        external_source_id = self._get_external_source_id("IRIS")

        if external_source_id is not None:
            query = select(self.dal.EXTERNAL_PERSON_TABLE).where(
                text(
                    f"{self.dal.EXTERNAL_PERSON_TABLE.name}.external_person_id"
                    + f" = '{external_person_id}' AND "
                    + f"{self.dal.EXTERNAL_PERSON_TABLE.name}.person_id = '{person_id}'"
                    + f" AND {self.dal.EXTERNAL_PERSON_TABLE.name}.external_source_id "
                    + f" = '{external_source_id}'"
                )
            )
            external_person_record = self.dal.select_results(query, False)

            if len(external_person_record) == 0:
                new_external_person_record = {
                    "person_id": person_id,
                    "external_person_id": external_person_id,
                    "external_source_id": external_source_id,
                }
                self.dal.bulk_insert_list(
                    self.dal.EXTERNAL_PERSON_TABLE, [new_external_person_record], False
                )

    @cache
    def _get_external_source_id(self, external_source_name: str) -> Literal[str, None]:
        """
        Gets the external source id for the external source name provided.
        :param external_source_name: The external source name.
        :return: The external source id if found, otherwise None.
        """

        external_source_id_query = select(self.dal.EXTERNAL_SOURCE_TABLE).where(
            text(
                f"{self.dal.EXTERNAL_SOURCE_TABLE.name}.external_source_name"
                + f" = '{external_source_name}'"
            )
        )
        external_source_record = self.dal.select_results(
            external_source_id_query, False
        )

        external_source_id = None
        if len(external_source_record) > 0:
            external_source_id = external_source_record[0][0]

        return external_source_id

    def _generate_dict_record_from_results(
        self, results_list: List[list]
    ) -> List[dict]:
        """
        Converts a list of list of records into a
        dictionary using the column name header, in the
        first row (first list) along with the values in
        the rest of the rows (lists).


        :param results_list: a list of list containing mpi
            records.
        :return: A dictionary that has the key value pairs
            of the results list.
        """
        return_records = []
        # we must ensure that there is a header AND at least
        # one record or there is much of a point in moving forward
        if len(results_list) > 1 and len(results_list[0]) > 0:
            for row_index, record in enumerate(results_list):
                if row_index > 0:
                    columns_and_values = {}
                    for col_index, row_header in enumerate(results_list[0]):
                        columns_and_values[row_header] = record[col_index]
                    return_records.append(columns_and_values)
        return return_records

    def _insert_person(self) -> str:
        """
        Simple insert of a new person record, which contains
        a new id (pk)

        :return: The newly created person id.
        """
        person_record = {}
        person_id = self.dal.bulk_insert_list(
            self.dal.PERSON_TABLE, [person_record], True
        )
        return person_id[0]
