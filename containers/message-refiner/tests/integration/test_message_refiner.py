import httpx
import pytest


@pytest.mark.integration
def test_health_check(setup):
    """
    Basic test to make sure the message refiner service can communicate with
    other up and running services.
    """
    port_number_dict = {
        "MESSAGE_REFINER_PORT_NUMBER": "8080",
        "TRIGGER_CODE_REFERENCE_PORT_NUMBER": "8081",
    }

    for name, port in port_number_dict.items():
        service_response = httpx.get(f"http://0.0.0.0:{port}")
        print(
            "Health check response for",
            name.replace("_PORT_NUMBER", ""),
            ":",
            service_response,
        )
        assert service_response.status_code == 200
