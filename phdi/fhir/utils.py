import hl7

from typing import List
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
    template_mappings: dict = CCDA_CODES_TO_CONVERSION_RESOURCE,
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
    :param template_mappings: An optional dictionary specifying how
      LOINC codes found in CCDA data inputs should map to convertible
      FHIR resources. A default mapping is provided, but the user
      is free to supply their own transformation if desired.
    """
    conversion_settings = _get_fhir_conversion_settings(message, template_mappings)
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
            f"HTTP {str(response.status_code)} code encountered in"
            + f" $convert-data for a message"
        )
    return response


def _get_fhir_conversion_settings(
    message: str, template_mappings: dict = CCDA_CODES_TO_CONVERSION_RESOURCE
) -> dict:
    """
    Private helper function to determine what settings to use with the
    FHIR server to facilitate message conversion. Some data streams
    will be encoded in HL7 format, whereas others will be XML data.
    Attempts to identify which data type the input has and determine
    the appropriate FHIR converter root template to use. Returns
    errors if the input data type isn't supported or if the user
    doesn't supply a dictionary mapping of LOINC codes to applicable
    CCDA templates. More information about the required templates and
    settings can be found here:

    https://docs.microsoft.com/en-us/azure/healthcare-apis/azure-api-for-fhir/convert-data

    :param message: The incoming message (already cleaned, if
      applicable)
    :param template_mappings: An optional dictionary specifying how
      LOINC codes found in CCDA data inputs should map to convertible
      FHIR resources. A default mapping is provided, but the user
      is free to supply their own transformation if desired.
    :return: A dictionary holding the settings of parameters to-be
      set when converting the input to FHIR
    """
    # Some streams (e.g. ELR, VXU) are HL7v2 encoded
    # If so, they'll always contain the root template value in
    # MSH 9.1-9.2
    try:
        parsed_msg = hl7.parse(message)
        extracted_code = str(parsed_msg.segment("MSH")[9])
        formatted_code = extracted_code.replace("^", "_")

        return {
            "root_template": formatted_code,
            "input_data_type": "HL7v2",
            "template_collection": "microsofthealth/fhirconverter:default",
        }

    # Others conform to C-CDA standards (e.g. ECR)
    except hl7.exceptions.ParseException:
        try:
            root = et.fromstring(message)

            # The Clinical Document tag and codeSystem together denote
            # accepted LOINC codes for convertible resources
            if "ClinicalDocument" in root.tag:
                for child in root:
                    if (
                        "code" in child.tag
                        and child.get("codeSystem") == "2.16.840.1.113883.6.1"
                    ):
                        break
                ccda_code = child.attrib.get("code")

                try:
                    root_template = template_mappings[ccda_code]
                    return {
                        "root_template": root_template,
                        "input_data_type": "Ccda",
                        "template_collection": "microsofthealth/ccdatemplates:default",
                    }
                except:
                    raise KeyError(
                        "Resource code does not match any provided input template"
                    )

        except:
            raise Exception(
                "Input message has unrecognized data type, should be HL7v2 or XML"
            )


def find_resource_by_type(bundle: dict, resource_type: str) -> List[dict]:
    """
    Collect all resources of a specific type in a bundle of FHIR data and
    return references to them in a list.

    :param bundle: The FHIR bundle to find patients in
    :param resource_type: The type of FHIR resource to find
    :return: List holding all resources of the requested type that were
      found in the input bundle
    """
    return [
        resource
        for resource in bundle.get("entry")
        if resource.get("resource").get("resourceType") == resource_type
    ]


# @TODO: Improve this function for more general use, since it's user-
# facing (i.e. make it more robust, less fragile, etc.)
def get_field(resource: dict, field: str, use: str, default_field: int) -> str:
    """
    For a given field (such as name or address), find the first-occuring
    instance of the field in a given FHIR-formatted JSON dict, such that
    the instance is associated with a particular "use" case of the field
    (use case here refers to the FHIR-based usage of classifying how a
    value is used in reporting). For example, find the first name for a
    patient that has a "use" of "official" (meaning the name is used
    for official reports). If no instance of a field with the requested
    use case can be found, instead return a specified default field.

    :param resource: Resource from a FHIR bundle
    :param field: The field to extract
    :param use: The use the field must have to qualify
    :param default_field: The index of the field type to treat as
      the default return type if no field with the requested use case is
      found
    :return: The first instance of the field value matching the desired
      use, or a default field value if a match couldn't be found
    """
    # The next function returns the "next" (in our case first) item from an
    # iterator that meets a given condition; if non exist, we index the
    # field for a default value
    return next(
        (item for item in resource[field] if item.get("use") == use),
        resource[field][default_field],
    )
