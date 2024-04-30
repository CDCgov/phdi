import httpx
import pytest

PARSER_URL = "http://0.0.0.0:8080"
PARSE_MESSAGE = PARSER_URL + "/parse_message"
FHIR_TO_PHDC = PARSER_URL + "/fhir_to_phdc"


@pytest.fixture
def fhir_bundle(read_json_from_test_assets):
    return read_json_from_test_assets("sample_fhir_bundle_for_phdc_conversion.json")


@pytest.fixture
def test_schema(read_schema_from_default_schemas):
    return read_schema_from_default_schemas("phdc_case_report_schema.json")


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(PARSER_URL)
    assert health_check_response.status_code == 200
