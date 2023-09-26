from contextlib import contextmanager
from sqlalchemy import MetaData, create_engine, Table, select
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
        self, table: Table, record: dict, return_pk: bool = True
    ) -> list:
        """
        Perform a single insert operation on a table

        this method inserts a list of records into the specified table

        :param table_object: the SQLAlchemy table object to insert into
        :param records: a list of records as a dictionary
        :return: None
        """
        new_pk = None
        with self.transaction() as session:
            if return_pk:
                stmt = table.insert().values(record).returning(table.primary_key)
                new_pk = session.execute(stmt)
            else:
                stmt = table.insert().values(record)
        return new_pk


    def bulk_insert_list(
        self, table: Table, records: list[dict], return_pk: bool = True
    ) -> list:
        """
        Perform a bulk insert operation on a table

        this method inserts a list of records into the specified table

        :param table_object: the SQLAlchemy table object to insert into
        :param records: a list of records as a dictionary
        :return: None
        """
        new_pks = []
        with self.transaction() as session:
            for record in records:
                if return_pk:
                    stmt = table.insert().values(record).returning(table.primary_key)
                    new_pk = session.execute(stmt)
                    new_pks.append(new_pk)
                else:
                    stmt = table.insert().values(record)
        return new_pks

    def bulk_insert_dict(self, records_with_table: dict, return_pks: bool = True) -> dict:
        """
        Perform a bulk insert operation on a table as defined
            by the 'table' element in the dict along with the record

        this method inserts a list of records into the specified table

        :param table_object: the SQLAlchemy table object to insert into
        :param records: a list of records as a dictionary
        :return: None
        """
        return_results = {}
        for key, value in records_with_table.items():
            new_pks = []
            table = value.get("table")
            records = value.get("records"):
            new_pks = self.bulk_insert_list(table,records)
            return_results[key] = {
                "results": new_pks
            }
        return return_results


    def select_results(
        self, select_stmt: select, include_col_names: bool = True
    ) -> List[list]:
        """
        Perform a select query and add the results to a
        list of lists.  Then add the column names as the
        first row, as header, in the list of lists


        :param select_stmt: the select statment to execute
        :param records: a list of records as a dictionary
        :return: None
        """
        with self.transaction() as session:
            results = session.execute(select_stmt)
            list_results = [list(row) for row in results]
            if include_col_names:
                list_results.insert(0, list(results.keys()))
        return list_results

    # TODO:  add an update section here

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

        # TODO: I am sure there is an easier way to do this
        for table in self.TABLE_LIST:
            if table.name == table_name:
                return table
        return None

    def get_table_by_column(self, column_name: str) -> Table:
        if len(self.TABLE_LIST) == 0:
            self.initialize_schema()

        # TODO: I am sure there is an easier way to do this
        for table in self.TABLE_LIST:
            if column_name in table.c:
                return table
        return None

    def does_table_have_column(self, table: Table, column_name: str) -> bool:
        return column_name in table.c
