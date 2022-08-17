import hl7

import xml.etree.ElementTree as et

from phdi.harmonization import standardize_hl7_datetimes
from phdi.cloud.core import BaseCredentialManager
from phdi.fhir.transport import http_request_with_reauth


CCDA_CODES_TO_CONVERSION_RESOURCE = {
    "34133-9": "CCD",
    "11488-4": "ConsultationNote",
    "18842-5": "DischargeSummary",
    "34117-2": "HistoryandPhysical",
    "11504-8": "OperativeNote",
    "28570-0": "ProcedureNote",
    "11506-3": "ProgressNote",
    "57133-1": "ReferralNote",
    "18761-7": "TransferSummary",
}


def convert_to_fhir(
    message: str,
    cred_manager: BaseCredentialManager,
    fhir_url: str,
    use_default_ccda=False,
):
    """
    Given a message in either HL7 v2 (pipe-delimited flat file) or
    CCDA (XML), attempt to convert that message into FHIR format
    (JSON) for further processing using the FHIR server. HL7v2
    messages have their datetimes standardized before conversion.

    The FHIR server will respond with a status code of 400 if the
    message itself is invalid, such as containing improperly
    formatted timestamps.  Otherwise, the FHIR server will respond
    with the converted FHIR data. In either case, a
    `requests.Response` object will be returned.


    :param message: The raw message that needs to be converted to
      FHIR. Must be HL7v2 or CCDA
    :param cred_manager: Service used to get an access token used to
      make a request
    :param fhir_url: A URL that points to the location of the FHIR
      server
    :param use_default_ccda: Optionally, whether to default to the
      base "CCD" root template if a resource's LOINC code doesn't
      map to a specific supported template. Default is No.
    """
    conversion_settings = _get_fhir_conversion_settings(message, use_default_ccda)
    if conversion_settings.get("input_data_type") == "HL7v2":
        message = standardize_hl7_datetimes(message)

    url = f"{fhir_url}/$convert-data"
    data = {
        "resourceType": "Parameters",
        "parameter": [
            {"name": "inputData", "valueString": message},
            {
                "name": "inputDataType",
                "valueString": conversion_settings.get("input_data_type"),
            },
            {
                "name": "templateCollectionReference",
                "valueString": conversion_settings.get("template_collection"),
            },
            {
                "name": "rootTemplate",
                "valueString": conversion_settings.get("root_template"),
            },
        ],
    }
    access_token = cred_manager.get_access_token().token
    headers = {"Authorization": f"Bearer {access_token}"}

    response = http_request_with_reauth(
        cred_manager=cred_manager,
        url=url,
        retry_count=3,
        request_type="POST",
        allowed_methods=["POST"],
        headers=headers,
        data=data,
    )

    if response.status_code != 200:
        raise Exception(
            f"HTTP {str(response.status_code)} code encountered in $convert-data for a message"  # noqa
        )
    return response


def _get_fhir_conversion_settings(message: str, use_default_ccda=False) -> dict:
    """
    Private helper function to determine what settings to use with the
    FHIR server to facilitate message conversion. Some data streams
    will be encoded in HL7 format, whereas others will be XML data.
    Attempts to identify which data type the input has and determine
    the appropriate FHIR converter root template to use. If the user
    opts to not use the default CCDA root template in cases where an
    input resource isn't supported, the functionwill raise an
    exception if a message's extracted LOINC code doesn't correspond to
    an existing CCDA template. More information about the required
    templates and settings can be found here:

    https://docs.microsoft.com/en-us/azure/healthcare-apis/azure-api-for-fhir/convert-data

    :param message: The incoming message (already cleaned, if
      applicable)
    :param use_default_ccda: Optionally, whether to default to the
      base "CCD" root template if a resource's LOINC code doesn't
      map to a specific supported template. Default is No.
    :return: A dictionary holding the settings of parameters to-be
      set when converting the input to FHIR
    """
    # Some streams (e.g. ELR, VXU) are HL7v2 encoded
    if message[:3] == "MSH":
        try:
            parsed_msg = hl7.parse(message)
            extracted_code = str(parsed_msg.segment("MSH")[9])

            # HL7 MSH segment 9 has three components: message code, trigger
            # event, and message structure. We can extract based on number of
            # present separators and recombine to create a robust formatted code
            extracted_code_tokenized = extracted_code.split(parsed_msg.separators[3])
            formatted_code = ""
            if (len(extracted_code_tokenized) >= 3) and (
                extracted_code_tokenized[2] != ""
            ):
                formatted_code = extracted_code_tokenized[2]
            elif len(extracted_code_tokenized) == 2:
                formatted_code = (
                    f"{extracted_code_tokenized[0]}_{extracted_code_tokenized[1]}"
                )

            if formatted_code == "":
                raise Exception("Could not determine HL7 message structure")

            return {
                "root_template": formatted_code,
                "input_data_type": "HL7v2",
                "template_collection": "microsofthealth/fhirconverter:default",
            }
        except hl7.exceptions.ParseException:
            raise hl7.exceptions.ParseException("Input HL7 message could not be parsed")

    # Others conform to C-CDA standards (e.g. ECR)
    else:
        try:
            root = et.fromstring(message)

            # The Clinical Document tag and codeSystem together denote
            # accepted LOINC codes for convertible resources
            if root.tag.strip() == "{urn:hl7-org:v3}ClinicalDocument":
                for child in root:
                    if (
                        child.tag.strip() == "{urn:hl7-org:v3}code"
                        and child.get("codeSystem") == "2.16.840.1.113883.6.1"
                    ):
                        break
                ccda_code = child.attrib.get("code")

                try:
                    root_template = CCDA_CODES_TO_CONVERSION_RESOURCE[ccda_code]
                    return {
                        "root_template": root_template,
                        "input_data_type": "Ccda",
                        "template_collection": "microsofthealth/ccdatemplates:default",
                    }
                except KeyError:
                    if use_default_ccda:
                        return {
                            "root_template": "CCD",
                            "input_data_type": "Ccda",
                            "template_collection": "microsofthealth/ccdatemplates:default",  # noqa
                        }
                    else:
                        raise KeyError(
                            "Resource code does not match any provided input template"
                        )

        except et.ParseError:
            raise Exception(
                "Input message has unrecognized data type, should be HL7v2 or XML"
            )
