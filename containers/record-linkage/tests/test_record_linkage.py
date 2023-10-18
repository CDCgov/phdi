# flake8: noqa
# fmt: off
import os
from app.config import get_settings

def set_mpi_env_vars():
    os.environ["mpi_db_type"] = "postgres"
    os.environ["mpi_dbname"] = "testdb"
    os.environ["mpi_user"] = "postgres"
    os.environ["mpi_password"] = "pw"
    os.environ["mpi_host"] = "localhost"
    os.environ["mpi_port"] = "5432"
    get_settings.cache_clear()


set_mpi_env_vars()

from fastapi import status
from fastapi.testclient import TestClient
from app.main import app, run_migrations
from sqlalchemy import text
import copy
import json
import pathlib
from phdi.linkage.mpi import PGMPIConnectorClient
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


def pop_mpi_env_vars():
    os.environ.pop("mpi_db_type", None)
    os.environ.pop("mpi_dbname", None)
    os.environ.pop("mpi_user", None)
    os.environ.pop("mpi_password", None)
    os.environ.pop("mpi_host", None)
    os.environ.pop("mpi_port", None)


def _clean_up():
    MPI = PGMPIConnectorClient()

    with MPI.dal.engine.connect() as pg_connection:
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_person CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS external_source CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS address CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS phone_number CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS identifier CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS give_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS given_name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS name CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS patient CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS person CASCADE;"""))
        pg_connection.execute(text("""DROP TABLE IF EXISTS public.pyway;"""))
        pg_connection.commit()
        pg_connection.close()


def test_health_check():
    set_mpi_env_vars()
    actual_response = client.get("/")
    assert actual_response.status_code == 200
    assert actual_response.json() == {
        "status": "OK",
        "mpi_connection_status": "OK",
    }
    pop_mpi_env_vars()


def test_linkage_bundle_with_no_patient():
    set_mpi_env_vars()
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
    pop_mpi_env_vars()


def test_linkage_invalid_db_type():
    set_mpi_env_vars()
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

    pop_mpi_env_vars()
    os.environ.pop("mpi_db_type", None)


def test_linkage_success():
    set_mpi_env_vars()
    run_migrations()
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

    bundle_4 = test_bundle
    bundle_4["entry"] = [entry_list[3]]
    resp_4 = client.post("/link-record", json={"bundle": bundle_4})
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
    assert resp_6.json()["found_match"]
    assert person_6.get("id") == person_1.get("id")


def test_use_enhanced_algo():
    # Start with fresh tables to make tests atomic
    _clean_up()
    set_mpi_env_vars()
    run_migrations()
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
    assert resp_6.json()["found_match"]
    assert person_6.get("id") == person_1.get("id")

    _clean_up()
    pop_mpi_env_vars()
