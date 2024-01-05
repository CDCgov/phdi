from unittest import mock

import pytest
from requests import Session

from phdi.transport import http_request_with_retry


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


def test_http_request_with_retry_unsupported_action():
    http_url = "https://some-url"
    http_action = "BADACTION"
    http_header = {"some-header": "some-header-value"}
    http_retry_count = 5

    with pytest.raises(ValueError):
        http_request_with_retry(
            http_url, http_retry_count, http_action, [http_action], http_header
        )
