from phdi.linkage.postgres import PostgresConnectorClient


def test_postgres_connection_local():
    postgres_client = PostgresConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
    )
    assert postgres_client.connection is not None


def test_generate_block_query():
    postgres_client = PostgresConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
    )
    table_name = "test_patient_mpi"
    block_data = {"ZIP": "90120-1001", "FIRST4": "JOSE", "LAST4": "GONZ"}
    expected_query = (
        "SELECT * FROM test_patient_mpi WHERE ZIP = '90120-1001' "
        + "AND FIRST4 = 'JOSE' AND LAST4 = 'GONZ';"
    )

    generated_query = postgres_client._generate_block_query(table_name, block_data)

    assert expected_query == generated_query


def test_block_data():
    postgres_client = PostgresConnectorClient(
        database="testdb",
        user="postgres",
        password="pw",
        host="localhost",
        port="5432",
        patient_table="test_patient_mpi",
        person_table="test_person_mpi",
    )
    table_name = "test_patient_mpi"
    block_data = {"LAST4": "GONZ"}

    # Create test table and insert data
    funcs = {
        "create": (
            f"CREATE TABLE IF NOT EXISTS {table_name} "
            + "(patient_id int, FIRST4 varchar(4), "
            + "LAST4 varchar(4), ZIP varchar(10));"
        ),
        "insert": (
            f"INSERT INTO {table_name} (patient_id, FIRST4, LAST4, ZIP) VALUES "
            + "(1, 'JOHN', 'SMIT','90120-1001'),"
            + "(2, 'JOSE', 'GONZ','90120-1001'),"
            + "(3, 'MARI', 'GONZ','90120-1001');"
        ),
    }

    for command, statement in funcs.items():
        try:
            postgres_client.cursor.execute(statement)
            postgres_client.connection.commit()
        except Exception as e:
            print(f"{command} was unsuccessful")
            print(e)
            postgres_client.connection.rollback()

    blocked_data = postgres_client.block_data(table_name, block_data)

    # Assert that all returned data matches blocking criterion
    for row in blocked_data:
        assert row[2] == block_data["LAST4"]

    # Assert returned data are LoL
    assert type(blocked_data[0]) is list

    # Clean up
    postgres_client.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    postgres_client.connection.close()
