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
import json
import pathlib
from phdi.linkage.mpi import DIBBsMPIConnectorClient
# fmt: on
client = TestClient(app)


def load_test_bundle():
    test_bundle = json.load(
        open(
            pathlib.Path(__file__).parent
            / "tests"
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
    MPI = DIBBsMPIConnectorClient()

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


def seed_testdb():
    # Start with fresh tables
    _clean_up()
    set_mpi_env_vars()
    run_migrations()
    test_bundle = load_test_bundle()

    for r in range(len(test_bundle["entry"])):
        print(r)
        if "resource" in test_bundle["entry"][r].keys():
            if r == 1:
                external_person_id = "KNOWN IRIS ID"
                bundle = {
                    "resourceType": "Bundle",
                    "identifier": {"value": "a very contrived FHIR bundle"},
                    "entry": [test_bundle["entry"][r]],
                }
                resp = client.post(
                    "/link-record",
                    json={
                        "bundle": bundle,
                        "use_enhanced": False,
                        "external_person_id": external_person_id,
                    },
                )
            elif r == 3:
                external_person_id = "ANOTHER KNOWN IRIS ID"
                bundle = {
                    "resourceType": "Bundle",
                    "identifier": {"value": "a very contrived FHIR bundle"},
                    "entry": [test_bundle["entry"][r]],
                }
                resp = client.post(
                    "/link-record",
                    json={
                        "bundle": bundle,
                        "use_enhanced": False,
                        "external_person_id": external_person_id,
                    },
                )
            else:
                bundle = {
                    "resourceType": "Bundle",
                    "identifier": {"value": "a very contrived FHIR bundle"},
                    "entry": [test_bundle["entry"][r]],
                }
                resp = client.post(
                    "/link-record",
                    json={
                        "bundle": bundle,
                        "use_enhanced": False,
                    },
                )

        print(resp.json())

    pop_mpi_env_vars()


if __name__ == "__main__":
    seed_testdb()
