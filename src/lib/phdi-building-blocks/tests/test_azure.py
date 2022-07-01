import json
import os

from phdi_building_blocks.azure import (
    _http_request_with_reauth,
    store_data,
    store_message_and_response,
)
from unittest import mock


@mock.patch("phdi_building_blocks.azure.get_blob_client")
def test_store_data(mock_get_client):
    mock_blob = mock.Mock()

    mock_client = mock.Mock()
    mock_client.get_blob_client.return_value = mock_blob

    mock_get_client.return_value = mock_client

    store_data(
        "some-url",
        "output/path",
        "some-filename-1.fhir",
        "some-bundle-type",
        {"hello": "world"},
    )

    mock_client.get_blob_client.assert_called_with(
        os.path.normpath("output/path/some-bundle-type/some-filename-1.fhir")
    )
    mock_blob.upload_blob.assert_called()


@mock.patch("requests.Session")
def test_auth_retry(patched_requests_session):
    mock_requests_session_instance = patched_requests_session.return_value

    response_content = '{"resourceType": "Patient", "id": "some-id"}'

    mock_requests_session_instance.get.side_effect = [
        mock.Mock(status_code=401),
        mock.Mock(status_code=200, text=response_content),
    ]

    mock_access_token_value1 = "some-token1"
    mock_access_token1 = mock.Mock()
    mock_access_token1.token = mock_access_token_value1

    mock_access_token_value2 = "some-token2"
    mock_access_token2 = mock.Mock()
    mock_access_token2.token = mock_access_token_value2

    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.side_effect = [
        mock_access_token1,
        mock_access_token2,
    ]

    url = "https://fhir-url"

    initial_access_token = mock_cred_manager.get_access_token().token
    response = _http_request_with_reauth(
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
    mock_access_token1 = mock.Mock()
    mock_access_token1.token = mock_access_token_value1

    mock_access_token_value2 = "some-token2"
    mock_access_token2 = mock.Mock()
    mock_access_token2.token = mock_access_token_value2

    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.side_effect = [
        mock_access_token1,
        mock_access_token2,
    ]

    url = "https://fhir-url"

    initial_access_token = mock_cred_manager.get_access_token().token
    response = _http_request_with_reauth(
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


@mock.patch("phdi_building_blocks.azure.store_data")
def test_store_message_and_response(patched_store):
    container_url = "some-url"
    output_path = "some/path"
    message_filename = "some-filename.msg"
    response_filename = "some-filename.msg.trantype-resp"
    bundle_type = "some-bundle-type"
    message = "original-message"
    response = mock.Mock(text=json.dumps({"resourceType": "Bundle"}))
    store_message_and_response(
        container_url=container_url,
        prefix=output_path,
        message_filename=message_filename,
        response_filename=response_filename,
        bundle_type=bundle_type,
        message=message,
        response=response,
    )

    patched_store.has_calls(
        [
            mock.call(
                container_url=container_url,
                prefix=output_path,
                message_filename=message_filename,
                bundle_type=bundle_type,
                message=message,
            ),
            mock.call(
                container_url=container_url,
                prefix=output_path,
                filename=response_filename,
                bundle_type=bundle_type,
                message=response.text,
            ),
        ]
    )

    patched_store.call_count = 2
