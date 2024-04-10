from unittest import mock

from app.fhir.transport import http_request_with_reauth


@mock.patch("requests.Session")
def test_auth_retry(patched_requests_session):
    mock_requests_session_instance = patched_requests_session.return_value

    response_content = '{"resourceType": "Patient", "id": "some-id"}'

    mock_requests_session_instance.get.side_effect = [
        mock.Mock(status_code=401),
        mock.Mock(status_code=200, text=response_content),
    ]

    mock_access_token_value1 = "some-token1"
    mock_access_token_value2 = "some-token2"

    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.side_effect = [
        mock_access_token_value1,
        mock_access_token_value2,
    ]

    url = "https://fhir-url"

    initial_access_token = mock_cred_manager.get_access_token()
    response = http_request_with_reauth(
        cred_manager=mock_cred_manager,
        url=url,
        retry_count=3,
        request_type="GET",
        allowed_methods=["GET"],
        headers={"Authorization": f"Bearer {initial_access_token}"},
    )

    assert response.status_code == 200
    assert response.text == response_content

    mock_cred_manager.get_access_token.call_count == 2

    mock_requests_session_instance.get.assert_called_with(
        url=url, headers={"Authorization": f"Bearer {mock_access_token_value2}"}
    )
    mock_requests_session_instance.get.call_count == 2


@mock.patch("requests.Session")
def test_auth_retry_double_fail(patched_requests_session):
    mock_requests_session_instance = patched_requests_session.return_value

    mock_requests_session_instance.get.side_effect = [
        mock.Mock(status_code=401),
        mock.Mock(status_code=401),
    ]

    mock_access_token_value1 = "some-token1"
    mock_access_token_value2 = "some-token2"

    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.side_effect = [
        mock_access_token_value1,
        mock_access_token_value2,
    ]

    url = "https://fhir-url"

    initial_access_token = mock_cred_manager.get_access_token()
    response = http_request_with_reauth(
        cred_manager=mock_cred_manager,
        url=url,
        retry_count=3,
        request_type="GET",
        allowed_methods=["GET"],
        headers={"Authorization": f"Bearer {initial_access_token}"},
    )

    assert response.status_code == 401

    mock_cred_manager.get_access_token.call_count == 2

    mock_requests_session_instance.get.assert_called_with(
        url=url, headers={"Authorization": f"Bearer {mock_access_token_value2}"}
    )
    mock_requests_session_instance.get.call_count == 2
