import pathlib
import pytest

from phdi.fhir.conversion import convert_to_fhir
from phdi.fhir.conversion.convert import ConversionError, _get_fhir_conversion_settings
from phdi.harmonization import standardize_hl7_datetimes
from unittest import mock


def test_get_fhir_conversion_settings():
    # HL7 case 1 (using the demo message from the HL7 API walkthrough)
    message = ""
    with open(pathlib.Path(__file__).parent.parent / "assets" / "sample_hl7.hl7") as fp:
        message = fp.read()
    settings = _get_fhir_conversion_settings(message)
    assert settings == {
        "root_template": "ORU_R01",
        "input_type": "hl7v2",
    }

    # HL7 case 2, when MSH[3] is set
    message = ""
    with open(
        pathlib.Path(__file__).parent.parent / "assets" / "hl7_with_msh_3_set.hl7"
    ) as fp:
        message = fp.read()
    settings = _get_fhir_conversion_settings(message)
    assert settings == {
        "root_template": "ADT_A01",
        "input_type": "hl7v2",
    }

    # CCDA case (using an example found at https://github.com/HL7/C-CDA-Examples)
    message = ""
    with open(
        pathlib.Path(__file__).parent.parent / "assets" / "ccda_sample.xml"
    ) as fp:
        message = fp.read()
    settings = _get_fhir_conversion_settings(message)
    assert settings == {
        "root_template": "ProcedureNote",
        "input_type": "ccda",
    }

    # CCDA case (using an adpated example found at
    # https://github.com/HL7/C-CDA-Examples)
    message = ""
    with open(
        pathlib.Path(__file__).parent.parent / "assets" / "ccda_sample_unknowntype.xml"
    ) as fp:
        message = fp.read()
    with pytest.raises(KeyError):
        _get_fhir_conversion_settings(message)

    settings = _get_fhir_conversion_settings(message=message, use_default_ccda=True)
    assert settings == {
        "root_template": "CCD",
        "input_type": "ccda",
    }


@mock.patch("requests.Session")
def test_convert_to_fhir_success_cred_manager(mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {"resourceType": "Bundle", "entry": [{"hello": "world"}]},
    )

    mock_access_token_value = "some-token"
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token_value

    message = ""
    with open(pathlib.Path(__file__).parent.parent / "assets" / "sample_hl7.hl7") as fp:
        message = fp.read()
    response = convert_to_fhir(
        message,
        "some-converter-url",
        mock_cred_manager,
    )

    mock_requests_session_instance.post.assert_called_with(
        url="some-converter-url",
        headers={"Authorization": f"Bearer {mock_access_token_value}"},
        json={
            "input_data": standardize_hl7_datetimes(message),
            "input_type": "hl7v2",
            "root_template": "ORU_R01",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"resourceType": "Bundle", "entry": [{"hello": "world"}]}


@mock.patch("requests.Session")
def test_convert_to_fhir_success_auth_header(mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {"resourceType": "Bundle", "entry": [{"hello": "world"}]},
    )

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    headers = {"Authorization": "Basic dGVzdDp0ZXN0"}

    message = ""
    with open(pathlib.Path(__file__).parent.parent / "assets" / "sample_hl7.hl7") as fp:
        message = fp.read()
    response = convert_to_fhir(
        message,
        "some-converter-url",
        headers=headers,
    )

    mock_requests_session_instance.post.assert_called_with(
        url="some-converter-url",
        headers=headers,
        json={
            "input_data": standardize_hl7_datetimes(message),
            "input_type": "hl7v2",
            "root_template": "ORU_R01",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"resourceType": "Bundle", "entry": [{"hello": "world"}]}


@mock.patch("requests.Session")
def test_convert_to_fhir_unrecognized_data(mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value

    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=200,
        json=lambda: {"resourceType": "Bundle", "entry": [{"hello": "world"}]},
    )

    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token

    message = ""
    with open(pathlib.Path(__file__).parent.parent / "assets" / "sample_hl7.hl7") as fp:
        message = fp.read()

    message_without_types_parts = message.split("|")
    message_without_types_parts[8] = ""

    message_without_type = "|".join(message_without_types_parts)
    print(message_without_type)

    response = None
    with pytest.raises(
        ConversionError, match="Could not determine HL7 message structure"
    ):
        response = convert_to_fhir(
            message_without_type,
            mock_cred_manager,
            "some-converter-url",
        )
    assert response is None

    message_bad = "BAD Message Data"

    with pytest.raises(
        ConversionError,
        match="Input message has unrecognized data type, should be HL7v2 or XML.",
    ):
        response = convert_to_fhir(
            message_bad,
            "some-converter-url",
            mock_cred_manager,
        )
    assert response is None


@mock.patch("requests.Session")
def test_convert_to_fhir_failure(mock_requests_session):
    mock_requests_session_instance = mock_requests_session.return_value
    mock_access_token_value = "some-token"
    mock_access_token = mock.Mock()
    mock_access_token.token = mock_access_token_value
    mock_cred_manager = mock.Mock()
    mock_cred_manager.get_access_token.return_value = mock_access_token
    mock_requests_session_instance.post.return_value = mock.Mock(
        status_code=400,
        text='{ "resourceType": "Bundle", "entry": [{"hello": "world"}] }',
    )

    message = ""
    with open(pathlib.Path(__file__).parent.parent / "assets" / "sample_hl7.hl7") as fp:
        message = fp.read()

    # Most efficient way to verify that the function will raise an exception,
    # since we're not using a unittest class structure and the exception is
    # _not_ merely a unittest.mock.side_effect of the session instance
    response = None
    with pytest.raises(
        ConversionError,
        match="^Conversion exception occurred with status code"
        + " 400 returned from the converter service.$",
    ):
        response = convert_to_fhir(
            message,
            "some-converter-url",
            mock_cred_manager,
        )
    assert response is None


def test_conversion_error():
    mock_response = mock.Mock(status_code=400)

    with pytest.raises(
        ConversionError,
        match="^Conversion exception occurred with "
        + "status code 400 returned from the converter service.$",
    ):
        raise ConversionError(mock_response)

    with pytest.raises(ConversionError, match="^some other message$"):
        raise ConversionError(mock_response, message="some other message")
