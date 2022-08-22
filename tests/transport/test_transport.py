from unittest import mock

import requests
from requests import Session
from phdi.transport import http_request_with_retry
from phdi.transport.http import _generate_custom_response


@mock.patch.object(Session, "post")
@mock.patch("phdi.transport.http.Retry")
def test_http_request_with_retry_post(mock_retry_strategy, mock_post):

    http_url = "https://some-url"
    http_action = "POST"
    http_header = {"some-header": "some-header-value"}
    http_data = {"some-data": "some-data-value"}
    http_retry_count = 5

    return_value = mock.Mock()

    mock_post.return_value = return_value

    response = http_request_with_retry(
        http_url, http_retry_count, http_action, [http_action], http_header, http_data
    )

    mock_retry_strategy.assert_called_with(
        total=http_retry_count,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=[http_action],
    )

    mock_post.assert_called_with(
        url=http_url,
        headers=http_header,
        json=http_data,
    )

    assert response == return_value


@mock.patch.object(Session, "get")
@mock.patch("phdi.transport.http.Retry")
def test_http_request_with_retry_get(mock_retry_strategy, mock_get):

    http_url = "https://some-url"
    http_action = "GET"
    http_header = {"some-header": "some-header-value"}
    http_retry_count = 5

    return_value = mock.Mock()

    mock_get.return_value = return_value

    response = http_request_with_retry(
        http_url, http_retry_count, http_action, [http_action], http_header
    )

    mock_retry_strategy.assert_called_with(
        total=http_retry_count,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=[http_action],
    )

    mock_get.assert_called_with(
        url=http_url,
        headers=http_header,
    )

    assert response == return_value


def test_generate_custom_response():
    test_response = _generate_custom_response(
        url="https://some_fhir_server_url",
        status_code=400,
        content=b'{"message": "test"}',
    )

    expected_json = {"message": "test"}
    expected_status_code = 400
    expected_url = "https://some_fhir_server_url"

    assert test_response.url == expected_url
    assert test_response.status_code == expected_status_code
    assert test_response.json() == expected_json
    assert isinstance(test_response, requests.Response)
