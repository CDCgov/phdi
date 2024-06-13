import json
import os
from pathlib import Path
from unittest.mock import patch

import httpx
import psycopg2
import pytest
from app.config import get_settings
from app.main import app
from lxml import etree
from starlette.testclient import TestClient


@pytest.fixture
def clean_up_db():
    """
    Removes the test data that is inserted during testing to ensure idempotency.
    """
    connection_string = os.environ.get("DATABASE_URL").replace("@db", "@localhost")
    dbconn = psycopg2.connect(connection_string)
    cursor = dbconn.cursor()
    query = "DELETE FROM fhir;"
    cursor.execute(query)
    dbconn.commit()
    cursor.close()
    dbconn.close()


get_settings()

ORCHESTRATION_URL = "http://localhost:8080"
PROCESS_ENDPOINT = ORCHESTRATION_URL + "/process"
PROCESS_MESSAGE_ENDPOINT = ORCHESTRATION_URL + "/process-message"


@pytest.mark.integration
def test_health_check(setup):
    """
    Basic test to make sure the orchestration service can communicate with
    other up and running services.
    """
    port_number_strings = [
        "ORCHESTRATION_PORT_NUMBER",
        "VALIDATION_PORT_NUMBER",
        "FHIR_CONVERTER_PORT_NUMBER",
        "INGESTION_PORT_NUMBER",
        "MESSAGE_PARSER_PORT_NUMBER",
        "ECR_VIEWER_PORT_NUMBER",
    ]

    for port_number in port_number_strings:
        port = os.getenv(port_number)
        service_response = httpx.get(f"http://0.0.0.0:{port}")
        print(
            "Health check response for",
            port_number.replace("_PORT_NUMBER", ""),
            ":",
            service_response,
        )
        assert service_response.status_code == 200


@pytest.mark.integration
def test_process_message_endpoint(setup, clean_up_db):
    """
    Tests a basic scenario of accepting an eCR message in XML format and
    applying a full validation through parsing workflow.
    """
    message = open(Path(__file__).parent.parent / "assets" / "CDA_eICR.xml").read()
    request = {
        "message_type": "ecr",
        "data_type": "ecr",
        "config_file_name": "test-no-save.json",
        "message": message,
    }
    orchestration_response = httpx.post(PROCESS_MESSAGE_ENDPOINT, json=request)
    assert orchestration_response.status_code == 200
    assert orchestration_response.json()["message"] == "Processing succeeded!"


@pytest.mark.integration
def test_process_endpoint_with_zip(setup, clean_up_db):
    """
    Tests full orchestration functionality of an eCR file, but this time,
    the file is zipped rather than raw string.
    """
    with open(
        Path(__file__).parent.parent / "assets" / "test_zip.zip",
        "rb",
    ) as file:
        form_data = {
            "message_type": "ecr",
            "config_file_name": "test-no-save.json",
        }
        files = {"upload_file": ("file.zip", file)}
        orchestration_response = httpx.post(
            PROCESS_ENDPOINT, data=form_data, files=files
        )
        assert orchestration_response.status_code == 200
        assert orchestration_response.json()["message"] == "Processing succeeded!"


@pytest.mark.integration
def test_process_endpoint_with_zip_and_rr_data(setup, clean_up_db):
    """
    Full orchestration test of a zip file containing both an eICR and the
    associated RR data.
    """
    with open(
        Path(__file__).parent.parent / "assets" / "eICR_RR_combo.zip",
        "rb",
    ) as file:
        form_data = {
            "message_type": "ecr",
            "config_file_name": "test-no-save.json",
        }
        files = {"upload_file": ("file.zip", file)}
        orchestration_response = httpx.post(
            PROCESS_ENDPOINT, data=form_data, files=files, timeout=60
        )
        assert orchestration_response.status_code == 200
        assert orchestration_response.json()["message"] == "Processing succeeded!"
        assert orchestration_response.json()["processed_values"] is not None


@pytest.mark.integration
def test_failed_save_to_ecr_viewer(setup, clean_up_db):
    """
    Full orchestration test of a zip file containing both an eICR and the
    associated RR data.
    """
    with open(
        Path(__file__).parent.parent / "assets" / "eICR_RR_combo.zip",
        "rb",
    ) as file:
        form_data = {
            "message_type": "ecr",
            "data_type": "zip",
            "config_file_name": "sample-orchestration-s3-config.json",
        }
        files = {"upload_file": ("file.zip", file)}
        orchestration_response = httpx.post(
            PROCESS_ENDPOINT, data=form_data, files=files, timeout=60
        )
        assert orchestration_response.status_code == 400


@pytest.mark.integration
def test_success_save_to_ecr_viewer(setup, clean_up_db):
    """
    Full orchestration test of a zip file containing both an eICR and the
    associated RR data.
    """
    with open(
        Path(__file__).parent.parent / "assets" / "test_zip.zip",
        "rb",
    ) as file:
        form_data = {
            "message_type": "ecr",
            "data_type": "zip",
            "config_file_name": "sample-orchestration-config.json",
        }
        files = {"upload_file": ("file.zip", file)}
        orchestration_response = httpx.post(
            PROCESS_ENDPOINT, data=form_data, files=files, timeout=60
        )

        assert orchestration_response.status_code == 200


@pytest.mark.integration
def test_process_message_fhir(setup):
    """
    Integration test of a different workflow and data type, a FHIR bundle
    passed through standardization.
    """
    message = json.load(
        open(
            Path(__file__).parent.parent / "assets" / "demo_phdc_conversion_bundle.json"
        )
    )
    request = {
        "message_type": "fhir",
        "data_type": "fhir",
        "config_file_name": "sample-fhir-test-config.json",
        "message": message,
    }
    orchestration_response = httpx.post(PROCESS_MESSAGE_ENDPOINT, json=request)
    assert orchestration_response.status_code == 200
    assert orchestration_response.json()["message"] == "Processing succeeded!"


@pytest.mark.integration
def test_process_message_fhir_phdc(setup):
    """
    Integration test of a different workflow and data type, a FHIR bundle
    passed through standardization to create a PHDC XML. The HTTP request is mocked
    to return a 200 response.
    """
    message = json.load(
        open(
            Path(__file__).parent.parent.parent
            / "tests"
            / "assets"
            / "demo_phdc_conversion_bundle.json"
        )
    )
    request = {
        "message_type": "fhir",
        "data_type": "fhir",
        "config_file_name": "sample-fhir-test-config-xml.json",
        "message": message,
    }
    # Define the mock XML content to be returned
    mock_xml_content = "<root><element>Test</element></root>"

    # Create a mock response
    mock_response = httpx.Response(status_code=200, text=mock_xml_content)

    # Patch the httpx.Client.post method
    with patch.object(httpx.Client, "post", return_value=mock_response):
        # Perform the HTTP request (which will be intercepted by the mock)
        client = httpx.Client()
        orchestration_response = client.post("dummy_url", json=request)

        # Assertions
        assert orchestration_response.status_code == 200
        try:
            parsed_xml = etree.fromstring(orchestration_response.text.encode())
            assert parsed_xml.tag == "root"  # Confirm correct root element
        except etree.XMLSyntaxError as e:
            pytest.fail(f"XML parsing error: {e}")


@pytest.mark.integration
def test_process_message_hl7(setup):
    """
    Full orchestrated test of validating, converting to FHIR, and geocoding
    an eLR HL7v2 message.
    """
    message = open(
        Path(__file__).parent.parent / "assets" / "hl7_with_msh_3_set.hl7"
    ).read()
    request = {
        "message_type": "elr",
        "data_type": "hl7",
        "config_file_name": "sample-hl7-test-config.json",
        "message": message,
    }
    orchestration_response = httpx.post(
        PROCESS_MESSAGE_ENDPOINT, json=request, timeout=30
    )
    assert orchestration_response.status_code == 200
    assert orchestration_response.json()["message"] == "Processing succeeded!"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_websocket_process_message_endpoint(setup):
    expected_response_message = {
        "validate": {
            "status": "success",
            "status_code": 200,
            "response": {
                "message_valid": True,
                "validation_results": {
                    "fatal": [],
                    "errors": [],
                    "warnings": [],
                    "information": [],
                    "message_ids": {
                        "eicr": {
                            "extension": None,
                            "root": "1.2.840.114350.1.13.297.3.7.8.688883.532013",
                        },
                        "rr": {},
                    },
                },
            },
        },
    }
    client = TestClient(app)

    # Pull in and read test zip file
    with open(
        Path(__file__).parent.parent / "assets" / "test_zip.zip",
        "rb",
    ) as file:
        test_zip = file.read()

    # Create fake websocket connection
    with client.websocket_connect("/process-ws") as websocket:
        # Send zip into fake connection, triggering process-ws endpoint
        websocket.send_bytes(test_zip)

        # Pull response message from websocket connection like frontend would
        messages = websocket.receive_json()

    assert messages == expected_response_message
