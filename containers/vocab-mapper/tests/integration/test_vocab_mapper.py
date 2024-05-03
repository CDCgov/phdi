import httpx
import pytest

PARSER_URL = "http://0.0.0.0:8080"


@pytest.mark.integration
def test_health_check(setup):
    health_check_response = httpx.get(PARSER_URL)
    assert health_check_response.status_code == 200
