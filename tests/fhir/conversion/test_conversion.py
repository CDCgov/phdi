import pathlib
from unittest import mock

import pytest
from lxml import etree

from phdi.fhir.conversion import convert_to_fhir
from phdi.fhir.conversion.convert import _get_fhir_conversion_settings
from phdi.fhir.conversion.convert import add_rr_data_to_eicr
from phdi.fhir.conversion.convert import ConversionError
from phdi.harmonization import standardize_hl7_datetimes


def test_get_fhir_conversion_settings():
    # HL7 case 1 (using the demo message from the HL7 API walkthrough)
    message = ""
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "hl7v2"
        / "sample_hl7.hl7"
    ) as fp:
        message = fp.read()
    settings = _get_fhir_conversion_settings(message)
    assert settings == {
        "root_template": "ORU_R01",
        "input_type": "hl7v2",
    }

    # HL7 case 2, when MSH[3] is set
    message = ""
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "hl7v2"
        / "hl7_with_msh_3_set.hl7"
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
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "ccda"
        / "ccda_sample.xml"
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
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "ccda"
        / "ccda_sample_unknowntype.xml"
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
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "hl7v2"
        / "sample_hl7.hl7"
    ) as fp:
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
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "hl7v2"
        / "sample_hl7.hl7"
    ) as fp:
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
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "hl7v2"
        / "sample_hl7.hl7"
    ) as fp:
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
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "hl7v2"
        / "sample_hl7.hl7"
    ) as fp:
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


def test_add_rr_to_ecr():
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "rr_extraction"
        / "CDA_RR.xml"
    ) as fp:
        rr = fp.read()

    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "rr_extraction"
        / "CDA_eICR.xml"
    ) as fp:
        ecr = fp.read()

    # extract rr fields, insert to ecr
    ecr = add_rr_data_to_eicr(rr, ecr)

    # confirm root tag added
    ecr_root = ecr.splitlines()[0]
    xsi_tag = "xmlns:xsi"
    assert xsi_tag in ecr_root

    # confirm new section added
    ecr = etree.fromstring(ecr)
    tag = "{urn:hl7-org:v3}" + "section"
    section = ecr.find(f"./{tag}", namespaces=ecr.nsmap)
    assert section is not None

    # confirm required elements added
    rr_tags = [
        "templateId",
        "id",
        "code",
        "title",
        "effectiveTime",
        "confidentialityCode",
        "entry",
    ]
    rr_tags = ["{urn:hl7-org:v3}" + tag for tag in rr_tags]
    for tag in rr_tags:
        element = section.find(f"./{tag}", namespaces=section.nsmap)
        assert element is not None

    # ensure that status has been pulled over
    entry_tag = "{urn:hl7-org:v3}" + "entry"
    template_id_tag = "{urn:hl7-org:v3}" + "templateId"
    code_tag = "{urn:hl7-org:v3}" + "code"
    for entry in section.find(f"./{entry_tag}", namespaces=section.nsmap):
        for temps in entry.findall(f"./{template_id_tag}", namespaces=entry.nsmap):
            status_code = entry.find(f"./{code_tag}", namespaces=entry.nsmap)
            assert temps is not None
            assert temps.attrib["root"] == "2.16.840.1.113883.10.20.15.2.3.29"
            assert "RRVS19" in status_code.attrib["code"]


def test_add_rr_to_ecr_rr_already_present(capfd):
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "rr_extraction"
        / "CDA_RR.xml"
    ) as fp:
        rr = fp.read()

    # This eICR has already been merged with an RR
    with open(
        pathlib.Path(__file__).parent.parent.parent
        / "assets"
        / "fhir-converter"
        / "rr_extraction"
        / "merged_eICR.xml"
    ) as fp:
        ecr = fp.read()

    merged_ecr = add_rr_data_to_eicr(rr, ecr)
    assert merged_ecr == ecr

    out, err = capfd.readouterr()
    assert "This eCR has already been merged with RR data." in out
