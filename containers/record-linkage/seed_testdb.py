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


def seed_testdb():
    # Start with fresh tables
    _clean_up()
    set_mpi_env_vars()
    run_migrations()
    test_bundle = load_test_bundle()

    for r in range(6, len(test_bundle["entry"])):
        if "resource" in test_bundle["entry"][r].keys():
            print(test_bundle["entry"][r])
            print()
            bundle = {
                "resourceType": "Bundle",
                "identifier": {"value": "a very contrived FHIR bundle"},
                "entry": [test_bundle["entry"][r]],
            }
            resp = client.post(
                "/link-record", json={"bundle": bundle, "use_enhanced": False}
            )
            print(resp.json())
            print()

    _clean_up()
    pop_mpi_env_vars()


if __name__ == "__main__":
    seed_testdb()


# {
#     "resource": {
#         "resourceType": "Patient",
#         "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380b22",
#         "identifier": [
#             {
#                 "value": "1234567890",
#                 "type": {
#                     "coding": [
#                         {
#                             "code": "MR",
#                             "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
#                             "display": "Medical record number",
#                         }
#                     ]
#                 },
#             }
#         ],
#         "name": [
#             {"family": "Diop", "given": ["Issa", "Rae"], "use": "official"},
#             {"family": "Rae", "given": ["Issa"], "use": "official"},
#         ],
#         "birthDate": "1985-01-12",
#         "gender": "female",
#         "address": [
#             {
#                 "line": ["1234 Insecure Road", "Apt 2"],
#                 "city": "Los Angeles",
#                 "state": "California",
#                 "postalCode": "90210",
#                 "use": "home",
#             },
#             {
#                 "line": ["1234 Insecure Road", "Apt 2"],
#                 "city": "Los Angeles",
#                 "state": "California",
#                 "postalCode": "90210",
#                 "use": "home",
#             },
#         ],
#     }
# }


# {
#     "resource": {
#         "resourceType": "Patient",
#         "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380b23",
#         "identifier": [
#             {
#                 "value": None,
#                 "type": {
#                     "coding": [
#                         {
#                             "code": "MR",
#                             "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
#                             "display": "Medical record number",
#                         }
#                     ]
#                 },
#             }
#         ],
#         "name": [
#             {"family": "Rae", "given": ["Issa"], "use": "official"},
#         ],
#         "birthDate": "1985-01-12",
#         "gender": "female",
#         "address": [
#             {
#                 "line": ["1234 Insecure Road", "Apt 2"],
#                 "city": "Los Angeles",
#                 "state": "California",
#                 "postalCode": "90210",
#                 "use": "home",
#             }
#         ],
#     }
# }
