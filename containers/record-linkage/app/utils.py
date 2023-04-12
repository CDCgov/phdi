from app.config import get_settings
from phdi.linkage import DIBBsConnectorClient

import os


def connect_to_mpi_with_env_vars():
    """
    Helper function to load MPI Database settings from the relevant
    environment variables, then spin up a connection to the MPI.
    This also automatically tests that a connection can be made as
    part of instantiating the DB Client.
    """
    dbname = get_settings().get("mpi_dbname")
    user = get_settings().get("mpi_user")
    password = get_settings().get("mpi_password")
    host = get_settings().get("mpi_host")
    port = get_settings().get("mpi_port")
    patient_table = get_settings().get("mpi_patient_table")
    person_table = get_settings().get("mpi_person_table")
    db_client = DIBBsConnectorClient(
        dbname, user, password, host, port, patient_table, person_table
    )
    return db_client


def load_mpi_env_vars_os():
    """
    Simple helper function to load some of the environment variables
    needed to make a database connection as part of the DB migrations.
    """
    dbname = os.getenv("mpi_dbname")
    user = os.getenv("mpi_user")
    password = os.getenv("mpi_password")
    host = os.getenv("mpi_host")
    return dbname, user, password, host
