def _set_up_postgres_client():
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
    }
    postgres_client = DIBBsConnectorClient()
    pg_connection = postgres_client.get_connection()
    pg_cursor = pg_connection.cursor

    # Generate test tables
    funcs = {
        "drop tables": (
            """
        DROP TABLE IF EXISTS patient;
        DROP TABLE IF EXISTS person;
        """
        ),
        "create_patient": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + "CREATE TABLE IF NOT EXISTS patient "
            + "(patient_id UUID DEFAULT uuid_generate_v4 (), person_id UUID, "
            + "patient_resource JSONB);"
        ),
        "create_person": (
            """
            BEGIN;

            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
            + "CREATE TABLE IF NOT EXISTS person "
            + "(person_id UUID DEFAULT uuid_generate_v4 (), "
            + "external_person_id VARCHAR(100));"
        ),
    }

    for command, statement in funcs.items():
        try:
            pg_cursor.execute(statement)
            pg_connection.commit()
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            pg_connection.rollback()

    return postgres_client


def _clean_up_postgres_client(postgres_client):
    os.environ = {
        "mpi_dbname": "testdb",
        "mpi_user": "postgres",
        "mpi_password": "pw",
        "mpi_host": "localhost",
        "mpi_port": "5432",
    }
    postgres_client = DIBBsConnectorClient()
    pg_connection = postgres_client.get_connection()
    pg_cursor = pg_connection.cursor

    pg_cursor.execute("DROP TABLE IF EXISTS patient")
    pg_connection.commit()
    pg_cursor.execute("DROP TABLE IF EXISTS person")
    pg_connection.commit()
    pg_cursor.close()
    pg_connection.close()
