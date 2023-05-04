import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retries = Retry(total=51, backoff_factor=1.0, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)


def test_kafka_flow():
    # Load data to kafka
    request_body = {
        "kafka_provider": "local_kafka",
        "storage_provider": "local_storage",
        "kafka_server": "kafka:9092",
        "kafka_topic": "test",
        "storage_account": "phdidev3phi9d194c64",
        "container": "lakehouse",
        "delta_table_name": "test-kafka-to-delta-1",
        "client_id": "0ea52a1c-f029-411b-8379-f2100c4fc8e5",
        "tenant_id": "28cf58df-efe8-4135-b2d1-f697ee74c00c",
        "key_vault_name": "dev3vault9d194c64",
        "client_secret_name": "test-kafka-to-delta",
        "schema": {"first_name": "string", "last_name": "string"},
        "kafka_data": [
            {"first_name": "Foo", "last_name": "Bar"},
            {"first_name": "Fiz", "last_name": "Biz"},
        ],
    }

    response = session.post(
        "http://kafka-to-delta-table:8080/load-data-to-kafka", json=request_body
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["status"] == "success"

    # Create delta tables
    request_body = {
        "kafka_provider": "local_kafka",
        "storage_provider": "local_storage",
        "kafka_server": "kafka:9092",
        "kafka_topic": "test",
        "storage_account": "phdidev3phi9d194c64",
        "container": "lakehouse",
        "delta_table_name": "test-kafka-to-delta-1",
        "client_id": "0ea52a1c-f029-411b-8379-f2100c4fc8e5",
        "tenant_id": "28cf58df-efe8-4135-b2d1-f697ee74c00c",
        "key_vault_name": "dev3vault9d194c64",
        "client_secret_name": "test-kafka-to-delta",
        "schema": {"first_name": "string", "last_name": "string"},
    }

    response = session.post(
        "http://kafka-to-delta-table:8080/kafka-to-delta-table", json=request_body
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["status"] == "success"

    request_body = {
        "kafka_provider": "local_kafka",
        "storage_provider": "local_storage",
        "kafka_server": "localhost:9092",
        "kafka_topic": "test",
        "storage_account": "phdidev3phi9d194c64",
        "container": "lakehouse",
        "delta_table_name": "test-table",
        "client_id": "0ea52a1c-f029-411b-8379-f2100c4fc8e5",
        "tenant_id": "28cf58df-efe8-4135-b2d1-f697ee74c00c",
        "key_vault_name": "dev3vault9d194c64",
        "client_secret_name": "test-kafka-to-delta",
        "schema": {"first_name": "string", "last_name": "string"},
    }

    response = session.post(
        "http://kafka-to-delta-table:8080/delta-table", json=request_body
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert "Foo|      Bar" in response_json["message"]
    assert "Fiz|      Biz" in response_json["message"]
    assert "first_name|last_name" in response_json["message"]
