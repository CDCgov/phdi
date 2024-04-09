# flake8: noqa
# fmt: off
import os

from app.utils import set_mpi_env_vars


set_mpi_env_vars()

from fastapi.testclient import TestClient
from app.main import app, run_migrations
from app.utils import _clean_up
from app.utils import pop_mpi_env_vars
import json
import pathlib
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
