from contextlib import contextmanager
import psycopg2
from sqlalchemy import MetaData, create_engine, Table
from sqlalchemy.orm import sessionmaker, scoped_session


class PGDataAccessLayer(object):
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
        self.Session = None
        self.Meta = MetaData()
        self.PATIENT_TABLE = None
        self.PERSON_TABLE = None

    def get_connection(self, engine_url: str, engine_echo: bool = True) -> None:
        """
        Establish a connection to the database

        this method initiates a connection to the database specified
        by the parameters defined in environment variables. Builds 
        engine and Session class for app layer 'if_drop==True' then 
        drop existing tables and rebuild schema
        
        :param engine_url: The URL of the database engine
        :param engine_echo: If True, print SQL statements to stdout
        :return: None
        """

        # create engine/connection
        self.engine = create_engine(
            engine_url,
            client_encoding="utf8",
            pool_reset_on_return=None,
            echo=engine_echo,
        )

        self.Session = scoped_session(
            sessionmaker(bind=self.engine)
        )  # NOTE extra config can be implemented in this call to sessionmaker factory

    def initialize_schema(self) -> None:
        """
        Initialize the database schema

        This method initializes the patient and person tables using SQLAlchemy's
        MetaData object

        :return: None
        """
        # create a metadata object to access the DB to ORM
        self.PATIENT_TABLE = Table("patient", self.Meta, autoload_with=self.engine)
        self.PERSON_TABLE = Table("person", self.Meta, autoload_with=self.engine)

    @contextmanager
    def transaction(self) -> None:
        """
        Execute a database transaction

        this method safely wraps a session object in a transactional scope
        used for basic create, select, update and delete procedures

        :yield: SQLAlchemy session object
        :raises ValueError: if an error occurs during the transaction
        """
        session = self.Session()

        try:
            yield session
            session.commit()

        except Exception as error:
            session.rollback()
            raise ValueError(f"{error}")

        finally:
            session.close()

    def bulk_insert(self, table_object: Table, records: list[dict]) -> None:
        """
        Perform a bulk insert operation on a table

        this method inserts a list of records into the specified table

        :param table_object: the SQLAlchemy table object to insert into
        :param records: a list of records as a dictionary
        :return: None
        """
        with self.transaction() as session:
            for record in records:
                stmt = table_object.insert().values(record)
                session.execute(stmt)

    def safe_append(self, records: list[dict], keep_errors: bool =True):
        """
        Performs a 'safe append' of an object where integrity errors are
        caught and the db is rolled back.

        :param records: a list of records as a dictionary
        :param keep_errors: default is true; if true, will keep any error
        :return: a tuple containing error_records
        """

        error_messages = []
        error_records = []

        for rec in records:
            try:
                with self.transaction() as session:
                    session.add(rec)

            except psycopg2.IntegrityError as err:
                error_messages.append(err.message)  # append message and errors
                error_records += [rec]
                continue

        return error_records, error_messages

    def get_session(self) -> scoped_session:
        """
        Get a session object

        this method returns a session object to the caller

        :return: SQLAlchemy scoped session
        """
        return self.Session()
