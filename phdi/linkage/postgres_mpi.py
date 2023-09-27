from typing import List, Dict, Union
from sqlalchemy import Select, and_, select, text
from phdi.linkage.core import BaseMPIConnectorClient
from phdi.linkage.utils import load_mpi_env_vars_os
from phdi.linkage.dal import DataAccessLayer


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
        self.dal = DataAccessLayer()
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

        # Get the base query that will select all necessary
        # columns for linkage with some basic filtering
        query = self._get_base_query()
        # now get the criteria organized by table so the
        # CTE queries can be constructed and then added
        # to the base query
        organized_block_vals = self._organize_block_criteria(block_vals)

        # now tack on the where criteria using the block_vals
        # while ensuring they exist in the table structure ORM
        query_w_ctes = self._generate_block_query(
            organized_block_vals=organized_block_vals, query=query
        )
        blocked_data = self.dal.select_results(select_stmt=query_w_ctes)

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

        # First, if person_id is not supplied, see if we can find a
        # matching person_id based upon the exernal person id, if supplied
        #  we have to get a person or insert a new person
        #  first to satisfy the link between the person and patient
        if person_id is None:
            external_person_record = self._get_external_person(
                external_person_id=external_person_id
            )
            person_id = external_person_id.get("person_id")

        # store it in a friendly location in the patient dict for access later
        if person_id is not None:
            patient_resource["person"] = person_id

        # try:
        #     # TODO: use this function from the DAL instead of
        #     # doing manual insert - see commented out code example below
        #     # self.dal.bulk_insert(self.dal.PATIENT_TABLE, patient_record_dict)

        {
            "resourceType": "Patient",
            "id": "fd645c21-4a6f-11eb-99fd-ad786a821574",
            "identifier": [
                {
                    "value": "7845451380",
                    "type": {
                        "coding": [
                            {
                                "code": "MR",
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "display": "Medical record number",
                            }
                        ]
                    },
                }
            ],
            "name": [{"family": "Shepard", "given": ["John"], "use": "official"}],
            "birthDate": "2053-11-07",
            "gender": "male",
            "address": [
                {
                    "line": ["1234 Silversun Strip"],
                    "buildingNumber": "1234",
                    "city": "Zakera Ward",
                    "state": "Citadel",
                    "postalCode": "99999",
                    "use": "home",
                }
            ],
            "telecom": [{"use": "home", "system": "phone", "value": "123-456-7890"}],
        }

        return None

    def _generate_where_criteria(self, block_vals: dict, table_name: str) -> list:
        where_criteria = []
        for key, value in block_vals.items():
            criteria_value = value["value"]
            criteria_transform = value.get("transformation", None)

            if criteria_transform is None:
                where_criteria.append(f"{table_name}.{key} = '{criteria_value}'")
            else:
                if criteria_transform == "first4":
                    where_criteria.append(
                        f"{table_name}.{key} starts with '{criteria_value}'"
                    )
                elif criteria_transform == "last4":
                    where_criteria.append(
                        f"{table_name}.{key} like_regex '{criteria_value}$$'"
                    )
        return where_criteria

    def _generate_block_query(
        self, organized_block_vals: dict, query: Select
    ) -> Select:
        # TODO: This comment may need to be updated with the changes made
        """
        Generates a query for selecting a block of data from the patient table per the
        block_vals parameters. Accepted blocking fields include: first_name, last_name,
        birthdate, address, city, state, zip, mrn, and sex.

        :param table_name: Table name.
        :param block_vals: Dictionary containing key value pairs for the column name for
          blocking and the data for the incoming record as well as any transformations,
          e.g., {["ZIP"]: {"value": "90210"}} or
          {["ZIP"]: {"value": "90210",}, "transformation":"first4"}.
        :raises ValueError: If column key in `block_vals` is not supported.
        :return: A 'Select' statement built by the sqlalchemy ORM

        """
        new_query = query

        for table_key, table_info in organized_block_vals.items():
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
                    fk_info = cte_query_table.foreign_keys.pop()
                    fk_table = fk_info.column.table
                    fk_column = fk_info.column
                    sub_query = (
                        select(cte_query_table)
                        .where(text(" AND ".join(query_criteria)))
                        .subquery()
                    )

                    cte_query = (
                        select(fk_table.c.patient_id.label("patient_id"))
                        .join(sub_query)
                        .where(
                            text(
                                f"{fk_table.name}.{fk_column.name} = "
                                + f"{cte_query_table.name}.{fk_column.name}"
                            )
                        )
                    ).cte(f"{table_key}_cte")

            if cte_query is not None:
                new_query = new_query.join(
                    cte_query,
                    and_(cte_query.c.patient_id == self.dal.PATIENT_TABLE.c.patient_id),
                )

        return new_query

    def _insert_person(
        self,
        person_id: str = None,
        external_person_id: str = None,
    ) -> tuple:
        return None

    def _organize_block_criteria(self, block_fields: dict) -> dict:
        # Accepted blocking fields include: first_name, last_name,
        # birthdate, address line 1, city, state, zip, mrn, and sex.
        organized_block_vals = {}

        count = 0
        for block_key, block_value in block_fields.items():
            count += 1
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

    def _get_base_query(self) -> select:
        name_sub_query = (
            select(
                self.dal.GIVEN_NAME_TABLE.c.given_name.label("given_name"),
                self.dal.GIVEN_NAME_TABLE.c.name_id.label("name_id"),
            )
            .where(self.dal.GIVEN_NAME_TABLE.c.given_name_index == 0)
            .subquery()
        )

        id_sub_query = (
            select(
                self.dal.ID_TABLE.c.value.label("mrn"),
                self.dal.ID_TABLE.c.patient_id.label("patient_id"),
            )
            .where(self.dal.ID_TABLE.c.type_code == "MR")
            .subquery()
        )

        phone_sub_query = (
            select(
                self.dal.PHONE_TABLE.c.phone_number.label("phone_number"),
                self.dal.PHONE_TABLE.c.type.label("phone_type"),
                self.dal.PHONE_TABLE.c.patient_id.label("patient_id"),
            )
            .where(self.dal.PHONE_TABLE.c.type.in_(["home", "cell"]))
            .subquery()
        )

        query = (
            select(
                self.dal.PATIENT_TABLE.c.patient_id,
                self.dal.PERSON_TABLE.c.person_id,
                self.dal.PATIENT_TABLE.c.dob,
                self.dal.PATIENT_TABLE.c.sex,
                id_sub_query.c.mrn,
                self.dal.NAME_TABLE.c.last_name,
                name_sub_query.c.given_name,
                phone_sub_query.c.phone_number,
                phone_sub_query.c.phone_type,
                self.dal.ADDRESS_TABLE.c.line_1.label("address_line_1"),
                self.dal.ADDRESS_TABLE.c.zip_code,
                self.dal.ADDRESS_TABLE.c.city,
                self.dal.ADDRESS_TABLE.c.state,
            )
            .outerjoin(
                id_sub_query,
            )
            .outerjoin(self.dal.NAME_TABLE)
            .outerjoin(name_sub_query)
            .outerjoin(phone_sub_query)
            .outerjoin(self.dal.ADDRESS_TABLE)
            .outerjoin(self.dal.PERSON_TABLE)
        )
        return query

    def _get_mpi_records(self, patient_resource: dict) -> dict:
        records = {}
        if patient_resource["resourceType"] != "Patient":
            return records

        # let's start with the patient record
        patient = {
            "patient_id": None,
            "person_id": patient_resource.get("person"),
            "dob": patient_resource.get("birthdate"),
            "sex": patient_resource.get("gender"),
            # TODO: find a way to get race and
            # ethnicity included here           #
            # "race": patient_resource.get("extension"),
            # "ethnicity": patient_resource.get("extension"),
        }
        records["patient"] = {"table": self.dal.PATIENT_TABLE, "records": [patient]}

        {
            "resourceType": "Patient",
            "id": "fd645c21-4a6f-11eb-99fd-ad786a821574",
            "identifier": [
                {
                    "value": "7845451380",
                    "type": {
                        "coding": [
                            {
                                "code": "MR",
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                "display": "Medical record number",
                            }
                        ]
                    },
                }
            ],
            "name": [{"family": "Shepard", "given": ["John"], "use": "official"}],
            "birthDate": "2053-11-07",
            "gender": "male",
            "address": [
                {
                    "line": ["1234 Silversun Strip"],
                    "buildingNumber": "1234",
                    "city": "Zakera Ward",
                    "state": "Citadel",
                    "postalCode": "99999",
                    "use": "home",
                }
            ],
            "telecom": [{"use": "home", "system": "phone", "value": "123-456-7890"}],
        }

    def _get_external_person(
        self,
        external_person_id: str,
    ) -> dict:
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
        return_record = {}
        if external_person_id is None:
            return None
        else:
            # if external person id is supplied then find if there is already
            #  a person with that external person id already within the MPI
            #  - if so, return that person id
            person_query = select(self.dal.EXTERNAL_PERSON_TABLE).where(
                text(
                    f"{self.dal.EXTERNAL_PERSON_TABLE.name}.external_person_id"
                    + f" = '{external_person_id}'"
                )
            )

            ext_person_record = self.dal.select_results(person_query)

        # if a person was found based upon the external
        # person id then return that full person record
        # for reference
        if len(ext_person_record) > 0 and len(ext_person_record[0]) > 0:
            return_record = {
                "external_id": ext_person_record[0][0],
                "person_id": ext_person_record[0][1],
                "external_person_id": external_person_id,
                "external_source_id": ext_person_record[0][3],
            }
        # otherwise, insert a new person and a new external person
        # record with the external_person_id
        else:
            new_person_record = {"person_id": None}
            person_id = self.dal.single_insert(self.dal.PERSON_TABLE, new_person_record)
            new_ext_person_record = {
                "external_id": None,
                "person_id": person_id,
                "external_person_id": external_person_id,
                "external_source_id": None,
            }
            ext_person_id = self.dal.single_insert(
                self.dal.EXT_PERSON_TABLE, new_ext_person_record
            )

            return_record = {
                "external_id": ext_person_id,
                "person_id": person_id,
                "external_person_id": external_person_id,
                "external_source_id": None,
            }

        return return_record
