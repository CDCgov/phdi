from app.services import send_to_ecr_viewer


def test_send_to_ecr_viewer_success(mocker, requests_mock):
    mock_env = "http://example.com"
    mocker.patch("os.getenv", return_value=mock_env)
    bundle_mock = mocker.MagicMock()
    bundle_mock.json.return_value = {"bundle": "fhir_data"}

    expected_url = f"{mock_env}/api/save-fhir-data"
    expected_payload = {"fhirBundle": "fhir_data", "saveSource": "s3"}

    requests_mock.post(expected_url, json={"message": "success"}, status_code=200)

    response = send_to_ecr_viewer(bundle_mock, "s3")

    assert requests_mock.called_once
    assert requests_mock.request_history[0].json() == expected_payload
    assert response.status_code == 200
