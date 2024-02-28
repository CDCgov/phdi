import pytest
from app.services import save_to_db_payload
from fastapi import HTTPException
from requests.models import Response


def test_save_to_db_payload():
    response = Response()
    response.status_code = 200
    response._content = b'{"bundle": {"entry": [{"resource": {"id": "foo"}}]}}'
    result = save_to_db_payload(bundle=response)
    expected_result = {
        "data": {"entry": [{"resource": {"id": "foo"}}]},
        "ecr_id": "foo",
    }

    assert result == expected_result


def test_save_to_db_failure_missing_eicr_id():
    response = Response()
    response.status_code = 200
    response._content = b'{"bundle": "bar", "parsed_values":{}}'

    with pytest.raises(HTTPException) as exc_info:
        save_to_db_payload(bundle=response)

    assert exc_info.value.status_code == 422
