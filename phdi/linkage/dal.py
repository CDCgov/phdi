import datetime
import logging
from contextlib import contextmanager
from typing import List

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import Table
from sqlalchemy import text
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


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
        self.Meta = MetaData()
        self.PATIENT_TABLE = None
        self.PERSON_TABLE = None
        self.NAME_TABLE = None
        self.GIVEN_NAME_TABLE = None
        self.ID_TABLE = None
        self.PHONE_TABLE = None
        self.ADDRESS_TABLE = None
        self.EXTERNAL_PERSON_TABLE = None
        self.EXTERNAL_SOURCE_TABLE = None
        self.TABLE_LIST = []

    def get_connection(
        self,
        engine_url: str,
        engine_echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        """
        Establish a connection to the database

        this method initiates a connection to the database specified
        by the parameters defined in environment variables. Builds
        engine and Session class for app layer

        :param engine_url: The URL of the database engine
        :param engine_echo: If True, print SQL statements to stdout
        :param pool_size: The number of connections to keep open in the connection pool
        :param max_overflow: The number of connections to allow in the connection pool
          “overflow”
        :return: None
        """

        # create engine/connection
        self.engine = create_engine(
            engine_url,
            client_encoding="utf8",
            echo=engine_echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

    def initialize_schema(self) -> None:
        """
        Initialize the database schema

        This method initializes all the MPI Database tables using SQLAlchemy's
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
        self.EXTERNAL_PERSON_TABLE = Table(
            "external_person", self.Meta, autoload_with=self.engine
        )
        self.EXTERNAL_SOURCE_TABLE = Table(
            "external_source", self.Meta, autoload_with=self.engine
        )

        # order of the list determines the order of
        # inserts due to FK constraints
        self.TABLE_LIST = []
        self.TABLE_LIST.append(self.PERSON_TABLE)
        self.TABLE_LIST.append(self.EXTERNAL_SOURCE_TABLE)
        self.TABLE_LIST.append(self.EXTERNAL_PERSON_TABLE)
        self.TABLE_LIST.append(self.PATIENT_TABLE)
        self.TABLE_LIST.append(self.NAME_TABLE)
        self.TABLE_LIST.append(self.GIVEN_NAME_TABLE)
        self.TABLE_LIST.append(self.ID_TABLE)
        self.TABLE_LIST.append(self.PHONE_TABLE)
        self.TABLE_LIST.append(self.ADDRESS_TABLE)

    @contextmanager
    def transaction(self) -> None:
        """
        Execute a database transaction

        this method safely wraps a session object in a transactional scope
        used for basic create, select, update and delete procedures

        :yield: SQLAlchemy session object
        :raises ValueError: if an error occurs during the transaction
        """
        session = self.get_session()

        try:
            yield session
            session.commit()

        except Exception as error:
            session.rollback()
            raise ValueError(f"{error}")

        finally:
            session.close()

    def bulk_insert_list(
        self, table: Table, records: list[dict], return_primary_keys: bool = True
    ) -> list:
        """
        Perform a bulk insert operation on a table.  A list of records
        as dictionaries are inserted into the specified table.  A list
        of primary keys from the bulk insert can be returned if return_pks
        is set to True.

        :param table_object: the SQLAlchemy table object to insert into
        :param records: a list of records as a dictionaries
        :param return_primary_key: boolean indicating if you want the inserted
            primary keys for the table returned or not, defaults to False
        :return: a list of primary keys or an empty list
        """
        new_primary_keys = []
        if len(records) > 0 and table is not None:
            logging.info(
                f"Getting primary_key_column at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
            primary_key_column = table.primary_key.c[0]
            with self.transaction() as session:
                logging.info(
                    f"Starting session at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                )
                n_records = 0
                for record in records:
                    n_records += 1
                    if return_primary_keys:
                        logging.info("Returned primary keys")
                        statement = (
                            table.insert().values(record).returning(primary_key_column)
                        )
                        logging.info(
                            f"""Starting statement execution getting
                              new_primary_key for record #{n_records}at:
                                {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                        )
                        new_primary_key = session.execute(statement)
                        # TODO: I don't like this, but seems to
                        # be one of the only ways to get this to work
                        #  I have tried using the column name from the
                        # PK defined in the table and that doesn't work
                        logging.info(
                            f""" Done with statement execution getting new_primary_key
                              for record #{n_records} at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                        )
                        new_primary_keys.append(new_primary_key.first()[0])
                    else:
                        logging.info("Did not return primary keys")
                        statement = table.insert().values(record)
                        logging.info(
                            f"Starting statement execution for record #{n_records} at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                        )
                        session.execute(statement)
                        logging.info(
                            f"""Done with statement execution
                              for record #{n_records} at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                        )
        return new_primary_keys

    def bulk_insert_dict(
        self, records_with_table: dict, return_primary_keys: bool = False
    ) -> dict:
        """
        Perform a bulk insert operation on a table as defined
        by the 'table' element in the dictionary along with the
        record(s), a list of record(s) as dictionaries.  This
        allows for several inserts to occur for different tables
        along with a single or multiple records for each table.

        :param records_with_table: a dictionary that defines the
            the SQLAlchemy table name to insert into
            along with a list of dictionaries as records to
            insert into the specified table
            eg. {
            "patient": [{"patient_id": UUID()}],
            "address": [{"line_1": "1313 Mocking Bird Lane, "city": "Scranton"},]
            }
        :param return_primary_keys: boolean indicating if you want the inserted
            primary keys for the table returned or not, defaults to False
        :return: a dictionary that contains table names as keys
            along with a list of the primary keys, if requested.
        """
        return_results = {}
        statements = []
        with self.transaction() as session:
            logging.info(
                f"Starting session at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
            n_records = 0
            for table in self.TABLE_LIST:
                records = records_with_table.get(table.name)
                if records is not None:
                    new_primary_keys = []

                    if len(records) > 0 and table is not None:
                        logging.info(
                            f"Getting primary_key_column at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                        )
                        primary_key_column = table.primary_key.c[0]

                        for record in records:
                            n_records += 1
                            if return_primary_keys:
                                logging.info("Returned primary keys")
                                statement = (
                                    table.insert()
                                    .values(record)
                                    .returning(primary_key_column)
                                )
                                logging.info(
                                    f"""Starting statement execution getting
                                    new_primary_key for record #{n_records}at:
                                        {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                                )
                                new_primary_key = session.execute(statement)
                                # TODO: I don't like this, but seems to
                                # be one of the only ways to get this to work
                                #  I have tried using the column name from the
                                # PK defined in the table and that doesn't work
                                logging.info(
                                    f""" Done with statement execution getting new_primary_key
                                    for record #{n_records} at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                                )
                                new_primary_keys.append(new_primary_key.first()[0])
                            else:
                                logging.info("Did not return primary keys")
                                logging.info(
                                    f"""Starting statement creation for record #{n_records} at:
                                        {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                                )

                                if "dob" in record:
                                    if record["dob"] is not None:
                                        record["dob"] = datetime.datetime.strptime(
                                            record["dob"], "%Y-%m-%d"
                                        )

                                statement = table.insert().values(**record)

                                statement = statement.compile(
                                    self.engine,
                                    compile_kwargs={
                                        "literal_binds": True,
                                        "render_postprocess": str,
                                    },
                                )
                                statement = str(statement)
                                statements.append(statement)
                                logging.info(
                                    f"""Done with statement creation for record #{n_records} at:
                                        {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"""  # noqa
                                )

                    return_results[table.name] = {"primary_keys": new_primary_keys}

            if not return_primary_keys:
                statements = ";".join(statements)
                logging.info(
                    f"Starting INSERT statement execution at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                )
                session.execute(text(statements))
                logging.info(
                    f"Done with INSERT statement execution at:{datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
                )
        return return_results

    def select_results(
        self,
        select_statement: select,
        include_col_header: bool = True,
        query_params: dict = None,
    ) -> List[list]:
        """
        Perform a select query and add the results to a
        list of lists.  Then add the column header as the
        first row, in the list of lists if the
        'include_col_header' parameter is True.

        :param select_statement: the select statment to execute
        :param include_col_header: boolean value to indicate if
            one wants to include a top row of the column headers
            or not, defaults to True
        :return: List of lists of select results
        """
        list_results = [[]]
        logging.info(
            f"In select_results, starting new session at {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
        )
        with self.transaction() as session:
            logging.info(
                f"Starting to execute statement to return results at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
            results = session.execute(select_statement, query_params)

            logging.info(
                f"Done executing statement to return results at: {datetime.datetime.now().strftime('%m-%d-%yT%H:%M:%S.%f')}"  # noqa
            )
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

        session = scoped_session(
            sessionmaker(bind=self.engine)
        )  # NOTE extra config can be implemented in this call to sessionmaker factory
        return session()

    def get_table_by_name(self, table_name: str) -> Table:
        """
        Get an SqlAlchemy ORM Table Object based upon the table
        name passed in.

        :param table_name: the name of the table you want to get.
        :return: SqlAlchemy ORM Table Object.
        """

        if table_name is not None and table_name != "":
            # TODO: I am sure there is an easier way to do this
            for table in self.TABLE_LIST:
                if table.name == table_name:
                    return table
        return None

    def get_table_by_column(self, column_name: str) -> Table:
        """
        Finds a table in the MPI based upon the column name.
        Note, this won't work if the column name used exists
        in more than one table.

        :param column_name: the column name you want to find the
            table it belongs to.
        :return: SqlAlchemy ORM Table Object.
        """

        if column_name is not None and column_name != "":
            # TODO: I am sure there is an easier way to do this
            for table in self.TABLE_LIST:
                if column_name in table.c:
                    return table
        return None

    def does_table_have_column(self, table: Table, column_name: str) -> bool:
        """
        Verifies if a column exists in a particular table

        :param table: the table object to verify if column exists
            within.
        :param column_name: the column name you want to verify.
        :return: True or False.
        """
        if table is None or column_name is None or column_name == "":
            return False
        else:
            return column_name in table.c
