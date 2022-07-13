import logging
import re
import hl7

from phdi_building_blocks.azure import (
    AzureFhirServerCredentialManager,
    _http_request_with_reauth,
)

from typing import List, Dict

from requests import Response


def clean_message(message: str) -> str:
    """
    Prepare an HL7 message for conversion by normalizing / sanitizing
    fields that are known to contain data in problematic formats. This
    function helps to-be-converted messages conform to expectations.
    Cleaning operations include:

    * Convert segment terminators from ``\\n`` to ``\\r``
    * Normalize datetime fields
    * Convert segment terminators back from ``\\r`` to ``\\n``

    :param message: The raw HL7 message to sanitize
    """
    parsed_message: hl7.Message = None
    try:
        # Conversion from \n to \r EOL characters is needed for hl7
        # module, and doesn't impact conversion ability
        parsed_message = hl7.parse(message.replace("\n", "\r"))

        # Normalize Dates
        # MSH-7 - Message date/time
        normalize_hl7_datetime_segment(parsed_message, "MSH", [7])

        # PID-7 - Date of Birth
        # PID-29 - Date of Death
        # PID-33 - Last update date/time
        normalize_hl7_datetime_segment(parsed_message, "PID", [7, 29, 33])

        # PV1-44 - Admisstion Date
        # PV1-45 - Discharge Date
        normalize_hl7_datetime_segment(parsed_message, "PV1", [44, 45])

        # ORC-9 Date/time of transaction
        # ORC-15 Order effective date/time
        # ORC-27 Filler's expected availability date/time
        normalize_hl7_datetime_segment(parsed_message, "ORC", [9, 15, 27])

        # OBR-7 Observation date/time
        # OBR-8 Observation end date/time
        # OBR-22 Status change date/time
        # OBR-36 Scheduled date/time
        normalize_hl7_datetime_segment(parsed_message, "OBR", [7, 8, 22, 36])

        # OBX-12 Effective date/time of reference range
        # OBX-14 Date/time of observation
        # OBX-19 Date/time of analysis
        normalize_hl7_datetime_segment(parsed_message, "OBX", [12, 14, 19])

        # TQ1-7 Start date/time
        # TQ1-8 End date/time
        normalize_hl7_datetime_segment(parsed_message, "TQ1", [7, 8])

        # SPM-18 Specimen received date/time
        # SPM-19 Specimen expiration date/time
        normalize_hl7_datetime_segment(parsed_message, "SPM", [18, 19])

        # RXA-3 Date/time start of administration
        # RXA-4 Date/time end of administration
        # RXA-16 Substance expiration date
        # RXA-22 System entry date/time
        normalize_hl7_datetime_segment(parsed_message, "RXA", [3, 4, 16, 22])

    except Exception:
        logging.exception(
            "Exception occurred while cleaning message.  "
            + "Passing through original message."
        )

        return message

    return str(parsed_message).replace("\r", "\n")


def default_hl7_value(
    message: str, segment_id: str, field_num: int, default_value: str
):
    """
    Default a field value in an HL7 message.

    :param message: String representing the HL7 message use to modify a value
    :param segment_id: Segment type (MSH, PID, etc)
    :param field_num: Field to replace in the HL7 message
    :param default_value: If the selected field is blank, set the field's value to this
    """

    parsed_message: hl7.Message = None
    try:
        # Conversion from \n to \r EOL characters is needed for hl7
        # module, and doesn't impact conversion ability
        parsed_message = hl7.parse(message.replace("\n", "\r"))

        segment: hl7.Segment = None
        try:
            segment = parsed_message.segment(segment_id=segment_id)
        except KeyError:
            # If the segment is not found, there is nothing to do
            return message

        if (
            segment.extract_field(field_num=field_num) is None
            or segment.extract_field(field_num=field_num) == ""
        ):
            segment.assign_field(value=default_value, field_num=field_num)

    except Exception:
        logging.exception(
            "Exception occurred while cleaning message.  "
            + "Passing through original message."
        )

        return message

    return str(parsed_message).replace("\r", "\n")


def normalize_hl7_datetime_segment(
    message: hl7.Message, segment_id: str, field_list: list
) -> None:
    """
    Utility function used to apply datetime normalization
    to multiple fields in a segment.

    :param message: The HL7 message, represented as a list
      of indexable component strings (which is how the HL7 library
      processes and returns messages)
    :param segment_id: The HL7-specified segment (ex. PID) to
      normalize the fields of
    :param field_list: The list of fields contained in the
      indexed message component, which are themselves indices to
      data strings
    """
    try:
        for segment in message.segments(segment_id):
            for field_num in field_list:
                if len(segment) > field_num and segment[field_num][0] != "":
                    cleaned_datetime = normalize_hl7_datetime(segment[field_num][0])
                    segment[field_num][0] = cleaned_datetime
    except KeyError:
        logging.debug(f"Segment {segment_id} not found in message.")


def normalize_hl7_datetime(hl7_datetime: str) -> str:
    """
    Split HL7 datetime-formatted fields into the following parts:
    <integer 8+ digits>[.<integer 1+ digits>][+/-<integer 4+ digits>]

    Each group of integers is truncated to conform to the HL7 specification:
    - first integer group: max 14 digits
    - following decimal point: max 4 digits
    - following +/- (timezone): 4 digits

    This normalization facilitates downstream processing using cloud
    providers that have particular requirements for dates.

    :param hl7_datetime: The raw datetime string to clean
    """

    # Use regex to achieve the datetime formatting described above
    hl7_datetime_match = re.match(r"(\d{8}\d*)(\.\d+)?([+-]\d+)?", hl7_datetime)

    if not hl7_datetime_match:
        return hl7_datetime

    hl7_datetime_parts = hl7_datetime_match.groups()

    # Start with date base
    normalized_datetime = hl7_datetime_parts[0][:14]  # First 14 digits

    # Add date decimal if present
    if hl7_datetime_parts[1]:
        normalized_datetime += hl7_datetime_parts[1][:5]  # . plus first 4 digits

    # Add timezone information if present
    if hl7_datetime_parts[2] and len(hl7_datetime_parts[2]) >= 5:
        normalized_datetime += hl7_datetime_parts[2][:5]  # +/- plus 4 digits

    return normalized_datetime


def clean_batch(batch: str, delimiter: str = "\n") -> str:
    """
    Clean a batch file by replacing Windows (CR-LF) newlines with the specified
    newline delimiter (LF by default). Also, strip vertical tab and file
    separator characters which can appear in input batch file data.

    :param batch: The batch file data to clean
    :param delimiter: The newline character to standardize
    """
    cleaned_batch = re.sub("[\r\n]+", delimiter, batch)

    # These are unicode for vertical tab and file separator, respectively
    # \u000b appears before every MSH segment, and \u001c appears at the
    # end of the message in some of the data we've been receiving, so
    # we're explicitly removing them here.
    cleaned_batch = re.sub("[\u000b\u001c]", "", cleaned_batch).strip()
    return cleaned_batch


# This method was adapted from PRIME ReportStream, which can be found here:
# https://github.com/CDCgov/prime-reportstream/blob/194396582be02fcc51295089f20b0c2b90e7c830/prime-router/src/main/kotlin/serializers/Hl7Serializer.kt#L121
def convert_batch_messages_to_list(content: str, delimiter: str = "\n") -> List[str]:
    """
    Convert a batch file of messages into a list of strings representing
    parts of the message. This function is based on the following header/tail
    segments:

    * FHS is a "File Header Segment", which is used to head a file
        (group of batches)
    * FTS is a "File Trailer Segment", which defines the end of a file
    * BHS is "Batch Header Segment", which defines the start of a batch
    * BTS is "Batch Trailer Segment", which defines the end of a batch

    The structure of an HL7 Batch looks like this:
    [FHS] (file header segment) { [BHS] (batch header segment)
    { [MSH (zero or more HL7 messages)
    ....
    ....
    ....
    ] }
    [BTS] (batch trailer segment)
    }
    [FTS] (file trailer segment)

    We ignore lines that start with these since we don't want to include
    them in a message.

    :param content: the batch content to turn into a list
    :param delimiter: the character delimiting messages in the batch
    """

    cleaned_batch = clean_batch(content)
    message_lines = cleaned_batch.split(delimiter)
    next_message = ""
    output = []

    for line in message_lines:
        if line.startswith(("FHS", "BHS", "BTS", "FTS")):
            continue

        # If we reach a line that starts with MSH and we have
        # content in nextMessage, then by definition we have
        # a full message in next_message and need to append it
        # to output. This will not trigger the first time we
        # see a line with MSH since next_message will be empty
        # at that time.
        if next_message != "" and line.startswith("MSH"):
            output.append(next_message)
            next_message = ""

        # Otherwise, continue to add the line of text to next_message
        if line != "":
            next_message += f"{line}\r"

    # Since our loop only adds messages to output when it finds
    # a line that starts with MSH, the last message would never
    # be added. So we explicitly add it here.
    if next_message != "":
        output.append(next_message)

    return output


def get_file_type_mappings(blob_name: str) -> Dict[str, str]:
    """
    Determine the input data and the FHIR converter schema to apply to
    a given message file based on the data stream the file comes from.
    E.g., ECR data will require a different conversion standard than
    VXU data (different root segments/templates, etc.).

    :param blob_name: The name of the blob to determine conversion
        mappings for
    """

    # Determine if the blob can be processed with our heuristics
    file_suffix = blob_name[-3:].lower()
    if file_suffix not in ("hl7", "xml"):
        raise Exception(f"invalid file extension for {blob_name}")

    filetype = blob_name.split("/")[-2].lower()

    if filetype == "elr":
        bundle_type = "ELR"
        root_template = "ORU_R01"
        input_data_type = "Hl7v2"
        template_collection = "microsofthealth/fhirconverter:default"
    elif filetype == "vxu":
        bundle_type = "VXU"
        root_template = "VXU_V04"
        input_data_type = "Hl7v2"
        template_collection = "microsofthealth/fhirconverter:default"
    elif filetype == "eicr":
        bundle_type = "ECR"
        root_template = "CCD"
        input_data_type = "Ccda"
        template_collection = "microsofthealth/ccdatemplates:default"
    else:
        raise Exception(f"Found an unidentified message_format: {filetype}")

    return {
        "file_suffix": file_suffix,
        "bundle_type": bundle_type,
        "root_template": root_template,
        "input_data_type": input_data_type,
        "template_collection": template_collection,
    }


def convert_message_to_fhir(
    message: str,
    filename: str,
    input_data_type: str,
    root_template: str,
    template_collection: str,
    cred_manager: AzureFhirServerCredentialManager,
    fhir_url: str,
) -> Response:
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
