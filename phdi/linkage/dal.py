from contextlib import contextmanager
from sqlalchemy import (
    MetaData,
    create_engine,
    Table,
    select,
    update,
)
from sqlalchemy.orm import sessionmaker, scoped_session
from typing import List


class DataAccessLayer(object):
    """
    Base class for Database API objects - manages transactions,
    sessions and holds a reference to the engine.
    Acts as a simple session context manager and creates a
    uniform API for querying using the ORM
    This class could be thought of as a singleton factory.
    Applications should only ever use one instance per database.
    Example:
        dal = DataAccessLayer()
        dal.connect(engine_url=..., engine_echo=False)
    """

    def __init__(self) -> None:
        self.engine = None
        self.session = None
        self.Meta = MetaData()
        self.PATIENT_TABLE = None
        self.PERSON_TABLE = None
        self.NAME_TABLE = None
        self.GIVEN_NAME_TABLE = None
        self.ID_TABLE = None
        self.PHONE_TABLE = None
        self.ADDRESS_TABLE = None
        self.EXT_PERSON_TABLE = None
        self.EXT_SOURCE_TABLE = None
        self.TABLE_LIST = []

    def get_connection(self, engine_url: str, engine_echo: bool = False) -> None:
        """
        Establish a connection to the database

        this method initiates a connection to the database specified
        by the parameters defined in environment variables. Builds
        engine and Session class for app layer

        :param engine_url: The URL of the database engine
        :param engine_echo: If True, print SQL statements to stdout
        :return: None
        """

        # create engine/connection
        self.engine = create_engine(
            engine_url,
            client_encoding="utf8",
            echo=engine_echo,
        )

        self.session = scoped_session(
            sessionmaker(bind=self.engine)
        )  # NOTE extra config can be implemented in this call to sessionmaker factory

    def initialize_schema(self) -> None:
        """
        Initialize the database schema

        This method initializes the patient and person tables using SQLAlchemy's
        Table object

        :return: None
        """

        self.PATIENT_TABLE = Table("patient", self.Meta, autoload_with=self.engine)
        self.PERSON_TABLE = Table("person", self.Meta, autoload_with=self.engine)
        self.NAME_TABLE = Table("name", self.Meta, autoload_with=self.engine)
        self.GIVEN_NAME_TABLE = Table(
            "given_name", self.Meta, autoload_with=self.engine
        )
        self.ID_TABLE = Table("identifier", self.Meta, autoload_with=self.engine)
        self.PHONE_TABLE = Table("phone_number", self.Meta, autoload_with=self.engine)
        self.ADDRESS_TABLE = Table("address", self.Meta, autoload_with=self.engine)
        self.EXT_PERSON_TABLE = Table(
            "external_person", self.Meta, autoload_with=self.engine
        )
        self.EXT_SOURCE_TABLE = Table(
            "external_source", self.Meta, autoload_with=self.engine
        )

        self.TABLE_LIST.append(self.PATIENT_TABLE)
        self.TABLE_LIST.append(self.PERSON_TABLE)
        self.TABLE_LIST.append(self.NAME_TABLE)
        self.TABLE_LIST.append(self.GIVEN_NAME_TABLE)
        self.TABLE_LIST.append(self.ID_TABLE)
        self.TABLE_LIST.append(self.PHONE_TABLE)
        self.TABLE_LIST.append(self.ADDRESS_TABLE)
        self.TABLE_LIST.append(self.EXT_PERSON_TABLE)
        self.TABLE_LIST.append(self.EXT_SOURCE_TABLE)

    @contextmanager
    def transaction(self) -> None:
        """
        Execute a database transaction

        this method safely wraps a session object in a transactional scope
        used for basic create, select, update and delete procedures

        :yield: SQLAlchemy session object
        :raises ValueError: if an error occurs during the transaction
        """
        session = self.session()

        try:
            yield session
            session.commit()

        except Exception as error:
            session.rollback()
            raise ValueError(f"{error}")

        finally:
            session.close()

    def single_insert(
        self,
        table_name: str,
        record: dict,
        return_pk: bool = False,
        return_full: bool = False,
    ) -> list:
        """
        Perform a single insert operation on a table for a record.
         One can have the primary key for the insert returned by
         using the return_pk parameter.

        :param table_object: the SQLAlchemy table object to insert into
        :param record: a record as a dictionary
        :param return_pk: boolean indicating if you want the inserted
            primary key for the table returned or not, defaults to False
        :return: a primary key or None
        """

        new_pk = None
        table = self.get_table_by_name(table_name)
        print(f"REC LEN: {len(record.items())}")
        print(f"TABLE: {table_name}")
        if len(record.items()) > 0 and table is not None:
            print("GOOD TABLE AND REC")
            pk_column = table.primary_key.c[0]
            print(f"PK COL: {pk_column}")
            with self.transaction() as session:
                if table_name == "person":
                    record = {}
                if return_pk or return_full:
                    stmt = table.insert().values(record).returning(pk_column)
                    # TODO: leaving this logic here
                    # as we may be able to leverage ctes
                    # for inserts in the future to insert
                    # multiple records in different tables at once
                    # and get the pk back to be used as the fk
                    # in the folllowing insert statement
                    #     stmt = (
                    #         table.insert()
                    #         .values(record)
                    #         .where(~exists(cte_query.select()))
                    #         .returning(pk_column)
                    #     )
                    pk = session.execute(stmt)

                    if return_full:
                        new_pk = pk.first()
                    elif return_pk:
                        # TODO: I don't like this, but seems to
                        # be one of the only ways to get this to work
                        #  I have tried using the column name from the
                        # PK defined in the table and that doesn't work
                        new_pk = pk.first()[0]
                else:
                    stmt = table.insert().values(record)
                    session.execute(stmt)
        return new_pk

    def bulk_insert_list(
        self, table: Table, records: list[dict], return_pks: bool = True
    ) -> list:
        """
        Perform a bulk insert operation on a table.  A list of records
        as dictionaries are inserted into the specified table.  A list
        of primary keys from the bulk insert can be returned if return_pks
        is set to True.

        :param table_object: the SQLAlchemy table object to insert into
        :param records: a list of records as a dictionaries
        :param return_pk: boolean indicating if you want the inserted
            primary keys for the table returned or not, defaults to False
        :return: a list of primary keys or an empty list
        """
        new_pks = []
        if len(records) > 0 and table is not None:
            pk_column = table.primary_key.c[0]
            with self.transaction() as session:
                for record in records:
                    if return_pks:
                        stmt = table.insert().values(record).returning(pk_column)
                        new_pk = session.execute(stmt)
                        # TODO: I don't like this, but seems to
                        # be one of the only ways to get this to work
                        #  I have tried using the column name from the
                        # PK defined in the table and that doesn't work
                        new_pks.append(new_pk.first()[0])
                    else:
                        stmt = table.insert().values(record)
                        session.execute(stmt)
        return new_pks

    def bulk_insert_dict(
        self, records_with_table: dict, return_pks: bool = False
    ) -> dict:
        """
        Perform a bulk insert operation on a table as defined
        by the 'table' element in the dictionary along with the
        record(s), a list of record(s) as dictionaries.  This
        allows for several inserts to occur for different tables
        along with a single or multiple records for each table.

        :param records_with_table: a dictionary that defines the
            the SQLAlchemy table object 'table' to insert into
            along with a list of dictionaries as records to
            insert into the specified table
        :param return_pks: boolean indicating if you want the inserted
            primary keys for the table returned or not, defaults to False
        :return: a dictionary that contains table names as keys
            along with a list of the primary keys, if requested.
        """
        return_results = {}
        for key, value in records_with_table.items():
            new_pks = []
            table = self.get_table_by_name(key)
            records = value.get("records")
            if table is not None and records is not None and len(records) > 0:
                new_pks = self.bulk_insert_list(table, records, return_pks)
                return_results[key] = {"results": new_pks}
        return return_results

    def select_results(
        self, select_stmt: select, include_col_header: bool = True
    ) -> List[list]:
        """
        Perform a select query and add the results to a
        list of lists.  Then add the column header as the
        first row, in the list of lists

        :param select_stmt: the select statment to execute
        :param include_col_header: boolean value to indicate if
            one wants to include a top row of the column headers
            or not, defaults to True
        :return: List of lists of select results
        """
        list_results = [[]]
        with self.transaction() as session:
            results = session.execute(select_stmt)
            list_results = [list(row) for row in results]
            if include_col_header:
                list_results.insert(0, list(results.keys()))
        return list_results

    def get_session(self) -> scoped_session:
        """
        Get a session object

        this method returns a session object to the caller

        :return: SQLAlchemy scoped session
        """

        return self.session()

    def get_table_by_name(self, table_name: str) -> Table:
        if len(self.TABLE_LIST) == 0:
            self.initialize_schema()

        if table_name is not None and table_name != "":
            # TODO: I am sure there is an easier way to do this
            for table in self.TABLE_LIST:
                if table.name == table_name:
                    return table
        return None

    def get_table_by_column(self, column_name: str) -> Table:
        if len(self.TABLE_LIST) == 0:
            self.initialize_schema()

        if column_name is not None and column_name != "":
            # TODO: I am sure there is an easier way to do this
            for table in self.TABLE_LIST:
                if column_name in table.c:
                    return table
        return None

    def does_table_have_column(self, table: Table, column_name: str) -> bool:
        if table is None or column_name is None or column_name == "":
            return False
        else:
            return column_name in table.c
