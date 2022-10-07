import hl7
import requests

import xml.etree.ElementTree as et

from phdi.harmonization import standardize_hl7_datetimes
from phdi.cloud.core import BaseCredentialManager
from phdi.fhir.transport import http_request_with_reauth
from phdi.transport.http import http_request_with_retry


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
    url: str,
    cred_manager: BaseCredentialManager = None,
    headers: dict = {},
    use_default_ccda=False,
):
    """
    Converts a given message from either HL7 v2 (pipe-delimited flat file) or CCDA (XML)
    into FHIR format (JSON) for further processing using the FHIR server. Standardizes
    datetimes in HL7v2 messages before conversion.

    This function uses a containerized version of the
    [Azure FHIR Converter](https://github.com/microsoft/FHIR-Converter).

    If conversion succeeds, a `requests.Response` object will be returned with the
    conversion response. Otherwise, a `ConversionError` is raised, with the
    `requests.Response` available as a property for troubleshooting and reporting
    purposes.

    :param message: The raw message that needs to be converted to
      FHIR. Currently, only HL7v2 or CCDA are supported.
    :param url: A URL that points to the location of the converter API.
    :param cred_manager: Service used to get an access token used to
      make a request.
    :param headers: JSON-type dictionary of headers to make the request with.
    :param use_default_ccda: Whether to default to the
      base "CCD" root template if a resource's LOINC code doesn't
      map to a specific supported template (Optional, default is No)
    :raises requests.HttpError: If the HTTP request was unsuccessful.
    :raises ConversionError: If the message could not be converted.
    :return: A requests.Response object

    """
    # TODO Update documentation with a link to the containerized FHIR converter, once
    # it's been ported over to the phdi repository.

    conversion_settings = _get_fhir_conversion_settings(message, use_default_ccda)
    if conversion_settings.get("input_type") == "hl7v2":
        message = standardize_hl7_datetimes(message)

    url = f"{url}"
    data = {
        "input_data": message,
        "input_type": conversion_settings.get("input_type"),
        "root_template": conversion_settings.get("root_template"),
    }

    if cred_manager:
        access_token = cred_manager.get_access_token()
        headers["Authorization"] = f"Bearer {access_token}"
        response = http_request_with_reauth(
            cred_manager=cred_manager,
            url=url,
            retry_count=3,
            request_type="POST",
            allowed_methods=["POST"],
            headers=headers,
            data=data,
        )
    else:
        response = http_request_with_retry(
            url=url,
            retry_count=3,
            request_type="POST",
            allowed_methods=["POST"],
            headers=headers,
            data=data,
        )

    if response.status_code != 200:
        raise ConversionError(response)

    return response


def _get_fhir_conversion_settings(message: str, use_default_ccda=False) -> dict:
    """
    Determines which settings to use with the FHIR server to facilitate message
    conversion by attempting to identify which data type the input has (HL7 or XML)
    and determine the appropriate FHIR converter root template to use. Raises
    an exception if the user opts to not use the default CCDA root template for
    an unsupported input resouece and a message's extracted LOINC code doesn't
    correspond to an existing CCDA template.

    More information about the required templates and settings can be found here:

    https://docs.microsoft.com/en-us/azure/healthcare-apis/azure-api-for-fhir/convert-data

    :param message: The incoming message.
    :param use_default_ccda: Whether to default to the
      base "CCD" root template if a resource's LOINC code doesn't
      map to a specific supported template. Default: `False`
    :raises ConversionError: If conversion settings cannot be derived.
    :return: A dictionary holding the settings of parameters to-be
      set when converting the input to FHIR.
    """
    # Some streams (e.g. ELR, VXU) are HL7v2 encoded
    if message[:3] == "MSH":
        parsed_msg = hl7.parse(message)
        extracted_code = str(parsed_msg.segment("MSH")[9])

        # HL7 MSH segment 9 has three components: message code, trigger
        # event, and message structure. We can extract based on number of
        # present separators and recombine to create a robust formatted code
        extracted_code_tokenized = extracted_code.split(parsed_msg.separators[3])
        formatted_code = ""
        if (len(extracted_code_tokenized) >= 3) and (extracted_code_tokenized[2] != ""):
            formatted_code = extracted_code_tokenized[2]
        elif len(extracted_code_tokenized) == 2:
            formatted_code = (
                f"{extracted_code_tokenized[0]}_{extracted_code_tokenized[1]}"
            )

        if formatted_code == "":
            raise ConversionError(message="Could not determine HL7 message structure")

        return {
            "root_template": formatted_code,
            "input_type": "hl7v2",
        }

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
                        "input_type": "ccda",
                    }
                except KeyError:
                    if use_default_ccda:
                        return {
                            "root_template": "CCD",
                            "input_type": "ccda",
                        }
                    else:
                        raise KeyError(
                            "Resource code does not match any provided input template"
                        )

        except et.ParseError as ex:
            raise ConversionError(
                message=(
                    "Input message has unrecognized data type, "
                    + "should be HL7v2 or XML."
                )
            ) from ex


class ConversionError(Exception):
    """
    Exception raised for errors that occur during conversion.
    """

    @property
    def http_response(self):
        return self.__http_response

    def __init__(self, http_response: requests.Response = None, message: str = None):
        """
        Creates a new ConversionError object.

        :param http_response: HTTP response returned by the converter service.
          Default: `None`
        :param message: Error message. Default: `None`
        """
        self.__http_response = http_response

        if (message is None) and not (http_response is None):
            message = (
                "Conversion exception occurred with status code"
                + f" {http_response.status_code} returned from the converter service."
            )
        self.message = message

        super().__init__(self.message)
