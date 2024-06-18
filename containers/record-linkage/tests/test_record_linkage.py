# flake8: noqa
# fmt: off
import copy
import json
import os
import pathlib

import pytest
from app.config import get_settings
from app.utils import pop_mpi_env_vars
from app.utils import set_mpi_env_vars

set_mpi_env_vars()

from fastapi import status
from fastapi.testclient import TestClient
from app.main import app, run_migrations
from app.utils import _clean_up
import copy
import json
import pathlib
# fmt: on
client = TestClient(app)


def load_test_bundle():
    test_bundle = json.load(
        open(
            pathlib.Path(__file__).parent
            / "assets"
            / "patient_bundle_to_link_with_mpi.json"
        )
    )
    return test_bundle


@pytest.fixture(autouse=True)
def setup_and_clean_tests():
    # This code will always run before every test in this file
    # We want it to set up env variables and run migrations
    set_mpi_env_vars()
    run_migrations()

    # pytest will automatically plug each test in this scoped file
    # in place of this yield
    yield

    # This code will run at the end of the test plugged into the yield
    _clean_up()
    pop_mpi_env_vars()


def test_health_check():
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {"status": "OK", "mpi_connection_status": "OK"}


def test_openapi():
    actual_response = client.get("/record-linkage/openapi.json")
    assert actual_response.status_code == 200


def test_linkage_bundle_with_no_patient():
    bad_bundle = {"entry": []}
    expected_response = {
        "message": "Supplied bundle contains no Patient resource to link on.",
        "found_match": False,
        "updated_bundle": bad_bundle,
    }
    actual_response = client.post(
        "/link-record",
        json={"bundle": bad_bundle},
    )
    assert actual_response.json() == expected_response
    assert actual_response.status_code == status.HTTP_400_BAD_REQUEST


def test_linkage_invalid_db_type():
    invalid_db_type = "mssql"
    os.environ["mpi_db_type"] = invalid_db_type
    get_settings.cache_clear()

    test_bundle = load_test_bundle()

    expected_response = {
        "message": f"Unsupported database type {invalid_db_type} supplied. "
        + "Make sure your environment variables include an entry "
        + "for `mpi_db_type` and that it is set to 'postgres'.",
        "found_match": False,
        "updated_bundle": test_bundle,
    }
    actual_response = client.post("/link-record", json={"bundle": test_bundle})
    assert actual_response.json() == expected_response
    assert actual_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_linkage_success():
    test_bundle = load_test_bundle()
    entry_list = copy.deepcopy(test_bundle["entry"])

    bundle_1 = test_bundle
    bundle_1["entry"] = [entry_list[0]]
    resp_1 = client.post("/link-record", json={"bundle": bundle_1})
    new_bundle = resp_1.json()["updated_bundle"]
    person_1 = [
        r.get("resource")
        for r in new_bundle["entry"]
        if r.get("resource").get("resourceType") == "Person"
    ][0]
    assert not resp_1.json()["found_match"]

    bundle_2 = test_bundle
    bundle_2["entry"] = [entry_list[1]]
    resp_2 = client.post("/link-record", json={"bundle": bundle_2})
    new_bundle = resp_2.json()["updated_bundle"]
    person_2 = [
        r.get("resource")
        for r in new_bundle["entry"]
        if r.get("resource").get("resourceType") == "Person"
    ][0]
    assert resp_2.json()["found_match"]
    assert person_2.get("id") == person_1.get("id")

    bundle_3 = test_bundle
    bundle_3["entry"] = [entry_list[2]]
    resp_3 = client.post("/link-record", json={"bundle": bundle_3})
    assert not resp_3.json()["found_match"]

    # Cluster membership failure--justified non-match
    bundle_4 = test_bundle
    bundle_4["entry"] = [entry_list[3]]
    resp_4 = client.post("/link-record", json={"bundle": bundle_4})
    new_bundle = resp_4.json()["updated_bundle"]
    person_4 = [
        r.get("resource")
        for r in new_bundle["entry"]
        if r.get("resource").get("resourceType") == "Person"
    ][0]
    assert not resp_4.json()["found_match"]

    bundle_5 = test_bundle
    bundle_5["entry"] = [entry_list[4]]
    resp_5 = client.post("/link-record", json={"bundle": bundle_5})
    assert not resp_5.json()["found_match"]

    bundle_6 = test_bundle
    bundle_6["entry"] = [entry_list[5]]
    resp_6 = client.post("/link-record", json={"bundle": bundle_6})
    new_bundle = resp_6.json()["updated_bundle"]
    person_6 = [
        r.get("resource")
        for r in new_bundle["entry"]
        if r.get("resource").get("resourceType") == "Person"
    ][0]
    assert not resp_6.json()["found_match"]


def test_use_enhanced_algo():
    test_bundle = load_test_bundle()
    entry_list = copy.deepcopy(test_bundle["entry"])

    bundle_1 = test_bundle
    bundle_1["entry"] = [entry_list[0]]
    resp_1 = client.post(
        "/link-record", json={"bundle": bundle_1, "use_enhanced": True}
    )
    new_bundle = resp_1.json()["updated_bundle"]
    person_1 = [
        r.get("resource")
        for r in new_bundle["entry"]
        if r.get("resource").get("resourceType") == "Person"
    ][0]
    assert not resp_1.json()["found_match"]

    bundle_2 = test_bundle
    bundle_2["entry"] = [entry_list[1]]
    resp_2 = client.post(
        "/link-record", json={"bundle": bundle_2, "use_enhanced": True}
    )
    new_bundle = resp_2.json()["updated_bundle"]
    person_2 = [
        r.get("resource")
        for r in new_bundle["entry"]
        if r.get("resource").get("resourceType") == "Person"
    ][0]
    assert resp_2.json()["found_match"]
    assert person_2.get("id") == person_1.get("id")

    bundle_3 = test_bundle
    bundle_3["entry"] = [entry_list[2]]
    resp_3 = client.post(
        "/link-record", json={"bundle": bundle_3, "use_enhanced": True}
    )
    assert not resp_3.json()["found_match"]

    bundle_4 = test_bundle
    bundle_4["entry"] = [entry_list[3]]
    resp_4 = client.post(
        "/link-record", json={"bundle": bundle_4, "use_enhanced": True}
    )
    new_bundle = resp_4.json()["updated_bundle"]
    person_4 = [
        r.get("resource")
        for r in new_bundle["entry"]
        if r.get("resource").get("resourceType") == "Person"
    ][0]
    assert resp_4.json()["found_match"]
    assert person_4.get("id") == person_1.get("id")

    bundle_5 = test_bundle
    bundle_5["entry"] = [entry_list[4]]
    resp_5 = client.post(
        "/link-record", json={"bundle": bundle_5, "use_enhanced": True}
    )
    assert not resp_5.json()["found_match"]

    bundle_6 = test_bundle
    bundle_6["entry"] = [entry_list[5]]
    resp_6 = client.post(
        "/link-record", json={"bundle": bundle_6, "use_enhanced": True}
    )
    new_bundle = resp_6.json()["updated_bundle"]
    person_6 = [
        r.get("resource")
        for r in new_bundle["entry"]
        if r.get("resource").get("resourceType") == "Person"
    ][0]
    assert not resp_6.json()["found_match"]
