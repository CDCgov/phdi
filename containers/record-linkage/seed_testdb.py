# flake8: noqa
# fmt: off
import os

from app.config import get_settings
from app.utils import _clean_up

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
from app.linkage.mpi import DIBBsMPIConnectorClient
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
            elif r == 3:
                external_person_id = "ANOTHER KNOWN IRIS ID"
            else:
                external_person_id = None
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
        print(resp.json())

    pop_mpi_env_vars()


if __name__ == "__main__":
    seed_testdb()
