import hl7

from typing import List, Dict
import xml.etree.ElementTree as et


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


def convert_to_fhir(message: str, cred_manager, fhir_url: str):
    """
    Given a message in either HL7 v2 (pipe-delimited flat file) or CCDA
    (XML), attempt to convert that message into FHIR format (JSON) for
    further processing using the FHIR server. HL7v2 messages are cleaned
    (minor corrections made) via the clean_message function prior to conversion.

    The FHIR server will respond with a status code of 400 if the message itself
    is invalid, such as containing improperly formatted timestamps.  Otherwise, the
    FHIR server will respond with the converted FHIR data. In either case, a
    `requests.Response` object will be returned.


    :param message: The raw message that needs to be converted to FHIR.
        Must be HL7v2 or CCDA
    :param input_data_type: The data type of the message. Must be one
        of Hl7v2 or Ccda
    :param root_template: The core template that should be used when
        attempting to convert the message to FHIR. More data can be found here:
        https://docs.microsoft.com/en-us/azure/healthcare-apis/azure-api-for-fhir/convert-data
    :param template_collection: Further specification of which template
        to use. More information can be found here:
        https://docs.microsoft.com/en-us/azure/healthcare-apis/azure-api-for-fhir/convert-data
    :param cred_manager: Service used to get an access token used to make a
        request.
    :param fhir_url: A URL that points to the location of the FHIR server
    """
    if input_data_type == "Hl7v2":
        message = clean_message(message)

    url = f"{fhir_url}/$convert-data"
    data = {
        "resourceType": "Parameters",
        "parameter": [
            {"name": "inputData", "valueString": message},
            {"name": "inputDataType", "valueString": input_data_type},
            {"name": "templateCollectionReference", "valueString": template_collection},
            {"name": "rootTemplate", "valueString": root_template},
        ],
    }
    access_token = cred_manager.get_access_token().token
    headers = {"Authorization": f"Bearer {access_token}"}

    response = _http_request_with_reauth(
        cred_manager=cred_manager,
        url=url,
        retry_count=3,
        request_type="POST",
        allowed_methods=["POST"],
        headers=headers,
        data=data,
    )

    if response.status_code != 200:
        logging.error(
            f"HTTP {str(response.status_code)} code encountered on"
            + f" $convert-data for {filename}"
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
    CCDA templates.

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


message = (
    "MSH|^~\&|GHH LAB|ELAB-3|GHH OE|BLDG4|200202150930||ORU^R01|CNTRL-3456|P|2.4\r"
)
message += "PID|||555-44-4444||EVERYWOMAN^EVE^E^^^^L|JONES|196203520|F|||153 FERNWOOD DR.^^STATESVILLE^OH^35292||(206)3345232|(206)752-121||||AC555444444||67-A4335^OH^20030520\r"
message += "OBR|1|845439^GHH OE|1045813^GHH LAB|1554-5^GLUCOSE|||200202150730||||||||555-55-5555^PRIMARY^PATRICIA P^^^^MD^^LEVEL SEVEN HEALTHCARE, INC.|||||||||F||||||444-44-4444^HIPPOCRATES^HOWARD H^^^^MD\r"
message += "OBX|1|SN|1554-5^GLUCOSE^POST 12H CFST:MCNC:PT:SER/PLAS:QN||^182|mg/dl|70_105|H|||F\r"
_get_fhir_conversion_settings(message)
