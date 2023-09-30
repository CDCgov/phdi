from typing import List, Dict, Union
from sqlalchemy import Select, and_, select, text
from phdi.linkage.new_core import BaseMPIConnectorClient
from phdi.linkage.utils import (
    get_address_lines,
    get_geo_latitude,
    get_geo_longitude,
    get_patient_addresses,
    get_patient_names,
    get_patient_phones,
    load_mpi_env_vars_os,
    get_patient_ethnicity,
    get_patient_race,
    get_patient_identifiers,
)
from phdi.linkage.dal import DataAccessLayer


class PGMPIConnectorClient(BaseMPIConnectorClient):
    """
    Represents a Postgres-specific Master Patient Index (MPI) connector
    client for the DIBBs implementation of the record linkage building
    block. Callers should use the provided interface functions (e.g.,
    block_vals) to interact with the underlying vendor-specific client
    property.

    """

    matched: bool = False

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

    def get_block_data(self, block_vals: Dict) -> List[list]:
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

        blocked_data = self.dal.select_results(
            select_stmt=query_w_ctes, include_col_header=True
        )

        return blocked_data

    def insert_matched_patient(
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
        try:
            # First, if person_id is not supplied, see if we can find a
            # matching person_id based upon the exernal person id.
            # If  external person id is supplied then
            #  we have to get a person_id that is linked or insert a new person
            #  that is linked to an external person record and then use that
            # found or new person_id to link to the patient
            correct_person_id = self._get_person_id(
                person_id=person_id, external_person_id=external_person_id
            )
            patient_resource["person"] = correct_person_id

            mpi_records = self._get_mpi_records(patient_resource)

            self.dal.bulk_insert_dict(records_with_table=mpi_records, return_pks=False)

        except Exception as error:  # pragma: no cover
            raise ValueError(f"{error}")

        return (self.matched, correct_person_id)

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
                        f"LEFT({table_name}.{key},4) = '{criteria_value}'"
                    )
                elif criteria_transform == "last4":
                    where_criteria.append(
                        f"RIGHT({table_name}.{key},4) = '{criteria_value}'"
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
                        .subquery(f"{cte_query_table.name}_cte_subq")
                    )

                    cte_query = (
                        select(fk_table.c.patient_id.label("patient_id"))
                        .join(sub_query)
                        .where(
                            text(
                                f"{fk_table.name}.{fk_column.name} = "
                                + f"{sub_query.name}.{fk_column.name}"
                            )
                        )
                    ).cte(f"{table_key}_cte")
            if cte_query is not None:
                new_query = new_query.join(
                    cte_query,
                    and_(cte_query.c.patient_id == self.dal.PATIENT_TABLE.c.patient_id),
                )

        return new_query

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

    def _get_base_query(self) -> Select:
        name_sub_query = (
            select(
                self.dal.GIVEN_NAME_TABLE.c.given_name.label("given_name"),
                self.dal.GIVEN_NAME_TABLE.c.name_id.label("name_id"),
            )
            .where(self.dal.GIVEN_NAME_TABLE.c.given_name_index == 0)
            .subquery("gname_subq")
        )

        id_sub_query = (
            select(
                self.dal.ID_TABLE.c.value.label("mrn"),
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
                self.dal.PERSON_TABLE.c.person_id,
                self.dal.PATIENT_TABLE.c.dob.label("birthdate"),
                self.dal.PATIENT_TABLE.c.sex,
                id_sub_query.c.mrn,
                self.dal.NAME_TABLE.c.last_name,
                name_sub_query.c.given_name.label("first_name"),
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
            .outerjoin(name_sub_query)
            # TODO: keeping this here for the time
            # when we decide to add phone numbers into
            # the blocking data
            #
            # .outerjoin(phone_sub_query)
            .outerjoin(self.dal.ADDRESS_TABLE)
            .outerjoin(self.dal.PERSON_TABLE)
        )
        return query

    def _get_mpi_records(self, patient_resource: dict) -> dict:
        records = {}
        if patient_resource["resourceType"] != "Patient":
            return records

        patient = {
            "patient_id": None,
            "person_id": patient_resource.get("person"),
            "dob": patient_resource.get("birthdate"),
            "sex": patient_resource.get("gender"),
            "race": get_patient_race(patient_resource),
            "ethnicity": get_patient_ethnicity(patient_resource),
        }
        new_patient_id = self.dal.single_insert(
            table=self.dal.PATIENT_TABLE,
            record=patient,
            return_pk=True,
            return_full=False,
        )

        patient_ids = []
        for pat_id in get_patient_identifiers(patient_resource):
            ident = {
                "identifier_id": None,
                "patient_id": new_patient_id,
                "value": pat_id.get("value"),
                "type_code": pat_id.get("type").get("coding").get("code"),
                "type_display": pat_id.get("type").get("coding").get("display"),
                "type_system": pat_id.get("type").get("coding").get("system"),
            }
            patient_ids.append(ident)
        records["identifier"] = {"records": patient_ids}

        phones = []
        for pat_phone in get_patient_phones(patient_resource):
            phn = {
                "phone_number_id": None,
                "patient_id": new_patient_id,
                "phone_number": pat_phone.get("value"),
                "type": pat_phone.get("use"),
                "start_date": pat_phone.get("period").get("start"),
                "end_date": pat_phone.get("period").get("end"),
            }
            phones.append(phn)
        records["phone_number"] = {"records": phones}

        addresses = []
        for pat_addr in get_patient_addresses(patient_resource):
            addr_dict = {"address": pat_addr}
            addr_lines = get_address_lines(addr_dict)
            addr = {
                "address_id": None,
                "patient_id": new_patient_id,
                "line_1": addr_lines[0],
                "line_2": addr_lines[1],
                "city": pat_addr.get("city"),
                "zip_code": pat_addr.get("state"),
                "country": pat_addr.get("country"),
                "latitude": get_geo_latitude(addr_dict),
                "longitude": get_geo_longitude(addr_dict),
                "start_date": pat_addr.get("period").get("start"),
                "end_date": pat_addr.get("period").get("end"),
                "type": pat_addr.get("use"),
            }
            addresses.append(addr)
        records["address"] = {"records": addresses}

        given_names = []
        for pat_name in get_patient_names(patient_resource):
            given_names = []
            name_rec = {
                "name_id": None,
                "patient_id": new_patient_id,
                "last_name": pat_name.get("family"),
                "type": pat_name.get("use"),
            }
            new_name_id = self.dal.single_insert(
                table=self.dal.NAME_TABLE,
                record=name_rec,
                return_pk=True,
                return_full=False,
            )
            for name_index, gname in enumerate(pat_name.get("given")):
                gname_rec = {
                    "given_name_id": None,
                    "name_id": new_name_id,
                    "given_name": gname,
                    "given_name_index": name_index,
                }
                given_names.append(gname_rec)
        records["given_name"] = {"records": given_names}
        return records

    def _get_person_id(
        self,
        person_id: str,
        external_person_id: str,
    ) -> str:
        """
        If person id is not supplied and external person id is not supplied
        then insert a new person record with an auto-generated person id (UUID)
        and there won't be any external_person record associated with the new
        person record and return that new person_id.
        If the person_id is not supplied but an external_person_id is supplied try
        to find an existing person record using the external_person_id.
        If a person record is found then return the found person_id.
        Otherwise add a new person record with an auto-generated person_id (UUID)
        and link it with the supplied external person id
        and return the new person_id.
        If person id and external person id are both supplied then
        ensure there is an external person record that is linked to the
        person_id, if not then add one and return the person_id.

        :param external_person_id: The external person id
        :param person_id: The person id
        :return: The found or newly created person id
        """
        new_person_id = None
        if external_person_id is None and person_id is None:
            new_person_record = {"person_id": None}
            new_person_id = self.dal.single_insert(
                table=self.dal.PERSON_TABLE,
                record=new_person_record,
                cte_query=None,
                return_pk=True,
                return_full=False,
            )
        elif external_person_id is not None:
            # if external person id is supplied then find if there is already
            #  a person associated with that external person id already
            # within the MPI - if so, return that person id
            ext_person_query = select(self.dal.EXT_PERSON_TABLE.c.person_id).where(
                text(
                    f"{self.dal.EXT_PERSON_TABLE.name}.external_person_id"
                    + f" = '{external_person_id}'"
                )
            )
            person_record = self.dal.select_results(ext_person_query, True)

            # if a person was found based upon the external
            # person id then return that person id
            # otherwise, insert a new person and a new external person
            # and link them together
            if len(person_record) == 0:
                new_person_record = {"person_id": None}
                person_cte = self.dal.create_insert_cte(
                    self.dal.PERSON_TABLE, new_person_record
                )
                new_ext_person_record = {
                    "external_id": None,
                    "person_id": person_cte.c.person_id,
                    "external_person_id": external_person_id,
                    "external_source_id": None,
                }
                ext_person_record = self.dal.single_insert(
                    table=self.dal.EXT_PERSON_TABLE,
                    record=new_ext_person_record,
                    cte_query=person_cte,
                    return_pk=False,
                    return_full=True,
                )
                new_person_id = self._generate_dict_record_from_results(
                    ext_person_record
                ).get("person_id")
                # its a match because an external person id was supplied
                self.matched = True
            else:
                found_person_id = person_record[0][0]
                if person_id is not None:
                    # its a match because an person id was supplied
                    self.matched = True
                    if found_person_id != person_id:
                        new_ext_person_record = {
                            "external_id": None,
                            "person_id": person_id,
                            "external_person_id": external_person_id,
                            "external_source_id": None,
                        }
                        self.dal.single_insert(
                            table=self.dal.EXT_PERSON_TABLE,
                            record=new_ext_person_record,
                            cte_query=None,
                            return_pk=False,
                            return_full=False,
                        )
                    new_person_id = person_id
        return new_person_id

    def _generate_dict_record_from_results(
        self, results_list: List[list]
    ) -> List[dict]:
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
