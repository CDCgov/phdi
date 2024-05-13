import os

import httpx
import pytest


@pytest.mark.integration
def test_health_check(setup):
    """
    Basic test to make sure the message refiner service can communicate with
    other up and running services.
    """
    port_number_strings = [
        "MESSAGE_REFINER_PORT_NUMBER",
        "TRIGGER_CODE_REFERENCE_PORT_NUMBER",
    ]

    for port_number in port_number_strings:
        port = os.getenv(port_number)
        service_response = httpx.get(f"http://0.0.0.0:{port}")
        print(
            "Health check response for",
            port_number.replace("_PORT_NUMBER", ""),
            ":",
            service_response,
        )
        assert service_response.status_code == 200
