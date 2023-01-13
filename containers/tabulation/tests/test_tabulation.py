# flake8: noqa
import os
from fastapi.testclient import TestClient
import json
from unittest import mock
import pathlib
import copy
import urllib
import datetime
from app.main import app, tabulate

valid_schema_path = (
    pathlib.Path(__file__).parent.parent.parent.parent
    / "tests"
    / "assets"
    / "valid_schema.json"
)

valid_schema = json.load(open(valid_schema_path))

valid_tabulate_request = {
    "output_type": "csv",
    "schema_name": "new_schema",
    "fhir_url": "http://localhost:8000/fhir/",
    "schema": valid_schema,
}

client = TestClient(app)

valid_validate_request = {"schema": valid_schema}

invalid_validate_request = {"schema": {}}

valid_response = {}


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK"}


def test_validate_schema_pass():
    actual_response = client.post("/validate-schema", json=valid_validate_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "success": True,
        "isValid": True,
        "message": "Valid Schema",
    }


def test_validate_validation_fail():
    actual_response = client.post("/validate-schema", json=invalid_validate_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "success": True,
        "isValid": False,
        "message": "Invalid schema: Validation exception",
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_valid_request(patched_tabulate):
    valid_request = copy.deepcopy(valid_tabulate_request)
    actual_response = client.post("/tabulate", json=valid_request)
    valid_request["cred_manager"] = None
    valid_request["schema_"] = valid_tabulate_request["schema"]
    valid_request["schema_name"] = valid_request["schema"]["metadata"]["schema_name"]
    valid_request.pop("schema")
    assert actual_response.status_code == 200
    assert actual_response.json() == {}
    patched_tabulate.assert_called_with(**valid_request)


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_missing_schema(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request.pop("schema")
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "schema"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_invalid_schema(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request["schema"] = {}
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "schema"],
                "msg": "Must provide a valid schema.",
                "type": "assertion_error",
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_missing_output_type(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request.pop("output_type")
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "output_type"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_invalid_output_type(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request["output_type"] = "blah"
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "output_type"],
                "msg": "unexpected value; permitted: 'parquet', 'csv', 'sql'",
                "type": "value_error.const",
                "ctx": {"given": "blah", "permitted": ["parquet", "csv", "sql"]},
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_invalid_cred_manager(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request["cred_manager"] = "blah"
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "cred_manager"],
                "msg": "unexpected value; permitted: 'azure', 'gcp'",
                "type": "value_error.const",
                "ctx": {"given": "blah", "permitted": ["azure", "gcp"]},
            }
        ]
    }


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_missing_schema_name(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request.pop("schema_name")
    invalid_tabulate_request["schema"]["metadata"].pop("schema_name")
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 422
    assert actual_response.json() == {
        "detail": [
            {
                "loc": ["body", "schema"],
                "msg": "Must provide a valid schema.",
                "type": "assertion_error",
            }
        ]
    }  # noqa


@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_missing_fhirl_url(patched_tabulate):
    invalid_tabulate_request = copy.deepcopy(valid_tabulate_request)
    invalid_tabulate_request.pop("fhir_url")
    actual_response = client.post("/tabulate", json=invalid_tabulate_request)
    assert actual_response.status_code == 400
    assert (
        actual_response.json()
        == "The following values are required, but were not included in the request and could not be read from the environment. Please resubmit the request including these values or add them as environment variables to this service. missing values: fhir_url."
    )  # noqa


@mock.patch("app.main.get_cred_manager")
@mock.patch("app.main.tabulate")
def test_tabulate_endpoint_instantiate_cred_manager(
    patched_tabulate, patched_get_cred_manager
):
    tabulate_request = copy.deepcopy(valid_tabulate_request)
    tabulate_request["cred_manager"] = "azure"
    actual_response = client.post("/tabulate", json=tabulate_request)
    assert actual_response.status_code == 200
    assert actual_response.json() == {}
    patched_get_cred_manager.assert_called_with(
        cred_manager=tabulate_request["cred_manager"],
        location_url=tabulate_request["fhir_url"],
    )


@mock.patch("app.main.write_data")
@mock.patch("app.main.tabulate_data")
@mock.patch("app.main.extract_data_from_fhir_search_incremental")
@mock.patch("app.main._generate_search_urls")
def test_tabulate(
    patched_generate_search_urls,
    patched_extract_data_from_fhir_search_incremental,
    patched_tabulate_data,
    patched_write_data,
):
    tabulate_request = copy.deepcopy(valid_tabulate_request)
    tabulate_request["schema_"] = tabulate_request["schema"]
    tabulate_request.pop("schema")

    search_urls = {"my-table": "my-table-search-url"}
    patched_generate_search_urls.return_value = search_urls

    incremental_results = ("some-incremental-results", None)
    patched_extract_data_from_fhir_search_incremental.return_value = incremental_results

    patched_tabulate_data.return_value = "some-tabulated-incremental-results"

    pq_writer = mock.Mock()
    patched_write_data.return_value = pq_writer

    directory = (
        pathlib.Path()
        / "tables"
        / tabulate_request["schema_name"]
        / datetime.datetime.now().strftime("%m-%d-%YT%H%M%S")
    )

    tabulate(**tabulate_request)

    patched_generate_search_urls.assert_called_with(schema=tabulate_request["schema_"])
    patched_extract_data_from_fhir_search_incremental.assert_called_with(
        search_url=urllib.parse.urljoin(
            tabulate_request["fhir_url"], search_urls["my-table"]
        ),
        cred_manager=None,
    )
    patched_tabulate_data.assert_called_with(
        incremental_results[0], tabulate_request["schema_"], list(search_urls.keys())[0]
    )
    patched_write_data.assert_called_with(
        tabulated_data=patched_tabulate_data(),
        directory=str(directory),
        filename=list(search_urls.keys())[0],
        output_type=tabulate_request["output_type"],
        db_file=tabulate_request["schema_name"],
        db_tablename=list(search_urls.keys())[0],
        pq_writer=None,
    )
    assert pq_writer.close.called
