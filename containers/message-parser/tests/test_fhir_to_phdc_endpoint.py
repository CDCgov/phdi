import json
import uuid
from datetime import date
from pathlib import Path
from unittest.mock import patch

from app import utils
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

fhir_bundle_path = (
    Path(__file__).parent.parent / "assets" / "demo_phdc_conversion_bundle.json"
)


with open(fhir_bundle_path, "r") as file:
    fhir_bundle = json.load(file)

test_schema_path = (
    Path(__file__).parent.parent
    / "app"
    / "default_schemas"
    / "phdc_case_report_schema.json"
)

with open(test_schema_path, "r") as file:
    test_schema = json.load(file)

expected_successful_response = utils.read_file_from_assets("demo_phdc.xml")


@patch.object(uuid, "uuid4", lambda: "495669c7-96bf-4573-9dd8-59e745e05576")
@patch.object(utils, "get_datetime_now", lambda: date(2010, 12, 15))
def test_endpoint():
    test_request = {
        "phdc_report_type": "case_report",
        "message": fhir_bundle,
    }
    actual_response = client.post("/fhir_to_phdc", json=test_request)
    assert actual_response.status_code == 200
    assert actual_response.text == expected_successful_response
    # print(actual_response.text)
