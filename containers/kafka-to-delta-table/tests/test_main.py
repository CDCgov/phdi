from app.main import app
from unittest import mock
from fastapi.testclient import TestClient

client = TestClient(app)


def test_kafka_to_delta_invalid_schema():
    request_body = {
        "kafka_provider": "local_kafka",
        "storage_provider": "local_storage",
        "delta_table_name": "test_table",
        "schema": {"first_name": "string", "last_name": "unknown_type"},
        "kafka_server": "some-server",
        "kafka_topic": "some-topic",
    }

    response = client.post("/kafka-to-delta-table", json=request_body)
    assert response.status_code == 400
    assert response.json() == {
        "status": "failed",
        "message": "Invalid type for field last_name: unknown_type. Valid types are"
        + " ['string', 'integer', 'float', 'boolean', 'date', 'timestamp'].",
        "spark_log": "",
    }


@mock.patch("app.main.subprocess")
def test_kafka_to_delta_spark_failure(patched_subprocess):
    request_body = {
        "kafka_provider": "local_kafka",
        "storage_provider": "local_storage",
        "delta_table_name": "test_table",
        "schema_name": "test_schema.json",
        "kafka_server": "some-server",
        "kafka_topic": "some-topic",
    }

    kafka_to_delta_result = mock.Mock()
    kafka_to_delta_result.returncode = 1
    kafka_to_delta_result.stdout = "Spark output"
    kafka_to_delta_result.stderr = "Spark error"
    patched_subprocess.run.return_value = kafka_to_delta_result

    response = client.post("/kafka-to-delta-table", json=request_body)
    assert response.status_code == 200
    assert response.json() == {
        "status": "failed",
        "message": "",
        "spark_log": "Spark error",
    }


@mock.patch("app.main.subprocess")
def test_kafka_to_delta_spark_success(patched_subprocess):
    request_body = {
        "kafka_provider": "local_kafka",
        "storage_provider": "local_storage",
        "delta_table_name": "test_table",
        "schema_name": "test_schema.json",
        "kafka_server": "some-server",
        "kafka_topic": "some-topic",
    }

    kafka_to_delta_result = mock.Mock()
    kafka_to_delta_result.returncode = 0
    kafka_to_delta_result.stdout = "Spark output"
    patched_subprocess.run.return_value = kafka_to_delta_result

    response = client.post("/kafka-to-delta-table", json=request_body)
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "",
        "spark_log": "Spark output",
    }
