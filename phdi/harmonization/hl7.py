import logging
import re
from typing import List

import hl7


def standardize_hl7_datetimes(message: str) -> str:
    """
    Prepares an HL7 message for conversion by normalizing / sanitizing
    fields that are known to contain datetime data in problematic formats. This
    function helps messages conform to expectations.

    This function accepts either segments terminated by `\\r` or `\\n`, but always
    returns data with `\\n` as the segment terminator.

    :param message: The raw HL7 message to sanitize.
    :return: The HL7 message with potential problem formats resolved. If the function
      is unable to parse a date, the original value is retained.
    """
    parsed_message: hl7.Message = None
    try:
        # The hl7 module requires \n characters be replaced with \r
        parsed_message = hl7.parse(message.replace("\n", "\r"))

        # MSH-7 - Message date/time
        normalize_hl7_datetime_segment(parsed_message, "MSH", [7])

        # PID-7 - Date of Birth
        # PID-29 - Date of Death
        # PID-33 - Last update date/time
        normalize_hl7_datetime_segment(parsed_message, "PID", [7, 29, 33])

        # PV1-44 - Admission Date
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

    # @TODO: Eliminate logging, raise an exception, document the exception
    # in the docstring, and make this fit into our new structure of allowing
    # the caller to implement more robust error handling
    except Exception:
        logging.exception(
            "Exception occurred while cleaning message.  "
            + "Passing through original message."
        )

        return message

    return str(parsed_message).replace("\r", "\n")


def convert_hl7_batch_messages_to_list(
    content: str, delimiter: str = "\n"
) -> List[str]:
    """
    Converts a batch file of messages into a list of strings
    representing parts of the message. This function is based
    on the following header/tail segments:

    * FHS is a "File Header Segment," which is used to head a file
        (group of batches)
    * FTS is a "File Trailer Segment," which defines the end of a file
    * BHS is "Batch Header Segment," which defines the start of a batch
    * BTS is "Batch Trailer Segment," which defines the end of a batch

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

    Ignores lines that start with these header/tail segments since we don't want to
    include them in a message.

    :param content: The batch content to turn into a list.
    :param delimiter: The character delimiting messages in the batch.
    :return: A list of separated, cleaned HL7 messages.
    """

    cleaned_batch = _clean_hl7_batch(content)
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


def default_hl7_value(
    message: str, segment_id: str, field_num: int, default_value: str
):
    """
    Defaults a field value in an HL7 message.

    This function accepts either segments terminated by `\\r` or `\\n`, but always
    returns data with `\\n` as the segment terminator.

    :param message: A string representing the HL7 message used to modify
      a value.
    :param segment_id: The segment type (MSH, PID, etc) of the field to replace.
    :param field_num: The field number to replace in the segment named by `segment_id`.
    :param default_value: If the selected field is blank, set the
      field's value to this value.
    :return: The HL7 message with default value inserted at the
      specified segment location, if possible. If not, then the
      original message.
    """

    parsed_message: hl7.Message = None
    try:
        # The hl7 module requires \n characters be replaced with \r
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

    # @TODO: Eliminate logging, raise an exception, document the exception
    # in the docstring, and make this fit into our new structure of allowing
    # the caller to implement more robust error handling
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
    Applies datetime normalization to multiple fields in a segment,
    overwriting values in the input segment as necessary.

    :param message: The HL7 message, represented as a list
      of indexable component strings (which is how the HL7 library
      processes and returns messages).
    :param segment_id: The segment type (MSH, PID, etc) of the field to replace.
    :param field_num: The field number to replace in the segment named by `segment_id`.
    :param field_list: The list of field numbers to replace in the segment named
      by `segement_id`.
    """
    try:
        for segment in message.segments(segment_id):
            for field_num in field_list:
                # Datetime value is always in first component
                component_num = 0
                if len(segment) > field_num and segment[field_num][component_num] != "":
                    cleaned_datetime = normalize_hl7_datetime(segment[field_num][0])
                    segment[field_num][0] = cleaned_datetime

    # @TODO: Eliminate logging, raise an exception, document the exception
    # in the docstring, and make this fit into our new structure of allowing
    # the caller to implement more robust error handling
    except KeyError:
        logging.debug(f"Segment {segment_id} not found in message.")


def normalize_hl7_datetime(hl7_datetime: str) -> str:
    """
    Splits HL7 datetime-formatted fields into the following parts:
    <integer 8+ digits>[.<integer 1+ digits>][+/-<integer 4+ digits>]

    Each group of integers is truncated to conform to the HL7
    specification:

    - first integer group: max 14 digits
    - following decimal point: max 4 digits
    - following +/- (timezone): 4 digits

    This normalization facilitates downstream processing using
    cloud providers that have particular requirements for dates.

    :param hl7_datetime: The raw datetime string to clean.
    :return: The datetime string with normalizing substitutions
      performed, or the original HL7 datetime if no matching
      format could be found.
    """

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


def _clean_hl7_batch(batch: str, delimiter: str = "\n") -> str:
    """
    Cleans a batch file by replacing Windows (CR-LF) newlines with
    the specified newline delimiter (LF by default). Also, strips
    vertical tab and file separator characters which can appear
    in input batch file data.

    :param batch: The batch file data to clean.
    :param delimiter: The newline character to standardize.
    :return: The batch file with newline characters standardized
      and file separators removed.
    """
    cleaned_batch = re.sub("[\r\n]+", delimiter, batch)

    # These are unicode for vertical tab and file separator, respectively
    # \u000b appears before every MSH segment, and \u001c appears at the
    # end of the message in some of the data we've been receiving, so
    # we're explicitly removing them here.
    cleaned_batch = re.sub("[\u000b\u001c]", "", cleaned_batch).strip()
    return cleaned_batch
