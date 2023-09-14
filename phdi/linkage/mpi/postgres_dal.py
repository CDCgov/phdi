from contextlib import contextmanager
import psycopg2
from sqlalchemy import MetaData, create_engine, Table
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.automap import automap_base


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

    def __init__(self):
        self.engine = None
        self.Session = None
        self.Meta = MetaData()
        self.PATIENT_TABLE = None
        self.PERSON_TABLE = None

    def get_connection(self, engine_url, engine_echo=True):
        """Builds engine and Session class for app layer
        if_drop==True then drop existing tables and rebuild schema

        Simple method for initiating a connection to the database specified
        by the parameters defined in environment variables.
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
        # create a metadata object to access the DB to ORM
        print("DAL INIT:")
        self.PATIENT_TABLE = Table("patient", self.Meta, autoload_with=self.engine)
        self.PERSON_TABLE = Table("person", self.Meta, autoload_with=self.engine)

    @contextmanager
    def transaction(self):
        """this method safely wraps a session object in a transactional scope
        used for basic create, select, update and delete procedures
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

    def bulk_insert(self, table_object, records):
        """performs a bulk insert on a list of records

        Arguments:
            records {list} -- obj records in list of dicts format
        """
        with self.transaction() as session:
            # values = []
            for record in records:
                stmt = table_object.insert().values(record)
                print("WE ARE CLOSE2:")
                print(stmt)
                session.execute(stmt)
            #     for key, value in record.items():
            #         values.append(key=value)
            # session.bulk_save_objects(records) # this doesn't work AT ALL

    def safe_append(self, records, keep_errors=True):
        """Performs a 'safe append' of an object where integrity errors are
        caught and the db rolled back.

        Arguments:
            records {list} -- obj records in list of dict format

        Keyword Arguments:
            keep_errors {bool} -- will keep any error records for the user (default: {True})

        Returns:
            error_records, error_messages -- a tuple of lists with errors from the append
        """

        error_messages = []
        error_records = []

        for rec in records:
            try:
                with self.transaction() as session:
                    # l.info("inserting record: {}".format(r))
                    session.add(rec)

            except psycopg2.IntegrityError as err:
                error_messages.append(err.message)  # append message and errors
                error_records += [rec]
                continue

        return error_records, error_messages

    def get_session(self):
        """returns a session to the caller"""
        return self.Session()

    def get_patient_table(self):
        return self.PATIENT_TABLE

    def get_person_table(self):
        return self.PERSON_TABLE
