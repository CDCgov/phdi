import logging
import re
import requests
from typing import List, Dict


def clean_message(message: str, delimiter: str = "\n") -> str:
    cleaned_message = re.sub("[\r\n]+", delimiter, message)

    # These are unicode for vertical tab and file separator, respectively
    # \u000b appears before every MSH segment, and \u001c appears at the
    # end of the message in some of the data we've been receiving, so
    # we're explicitly removing them here.
    cleaned_message = re.sub("[\u000b\u001c]", "", cleaned_message).strip()
    return cleaned_message


# This method was adopted from PRIME ReportStream, which can be found here:
# https://github.com/CDCgov/prime-reportstream/blob/194396582be02fcc51295089f20b0c2b90e7c830/prime-router/src/main/kotlin/serializers/Hl7Serializer.kt#L121
def convert_batch_messages_to_list(content: str, delimiter: str = "\n") -> List[str]:
    """
    FHS is a "File Header Segment", which is used to head a file (group of batches)
    FTS is a "File Trailer Segment", which defines the end of a file
    BHS is "Batch Header Segment", which defines the start of a batch
    BTS is "Batch Trailer Segment", which defines the end of a batch

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
    them in a message
    """

    cleaned_message = clean_message(content)
    message_lines = cleaned_message.split(delimiter)
    next_message = ""
    output = []

    for line in message_lines:
        if line.startswith("FHS"):
            continue
        if line.startswith("BHS"):
            continue
        if line.startswith("BTS"):
            continue
        if line.startswith("FTS"):
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
    access_token: str,
    fhir_url: str,
) -> dict:
    """
    Given a message in either HL7 v2 (pipe-delimited flat file) or HL7 v3 (XML),
    attempt to convert that message into FHIR format (JSON) for further processing
    using the FHIR server. The FHIR server will respond with a status code of 400 if
    the message itself is invalid, such as containing improperly formatted timestamps,
    and if that occurs that an empty dictionary is returned so the pipeline knows to
    store the original message in a separate container. Otherwise, the FHIR data is
    returned.

    :param message The raw message that needs to be converted to FHIR. Must be HL7
    v2 or HL7 v3
    :param input_data_type The data type of the message. Must be one of Hl7v2 or Ccda
    :param root_template The core template that should be used when attempting to
    convert the message to FHIR. More data can be found here:
    https://docs.microsoft.com/en-us/azure/healthcare-apis/azure-api-for-fhir/convert-data
    :param template_collection Further specification of which template to use. More
    information can be found here:
    https://docs.microsoft.com/en-us/azure/healthcare-apis/azure-api-for-fhir/convert-data
    :param access_token A Bearer token used to authenticate with the FHIR server
    :param fhir_url A URL that points to the location of the FHIR server
    """
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
    response = requests.post(
        url=url, json=data, headers={"Authorization": f"Bearer {access_token}"}
    )

    if response.status_code != 200:

        error_info = ""

        # Try to parse the non-success response as OperationOutcome FHIR JSON
        try:
            response_json = response.json()

            logging.info("non-200 response from fhir converter: " + str(response_json))

            # If it's FHIR, unpack the response
            if response_json["resourceType"] == "OperationOutcome":
                for issue in response_json["issue"]:
                    issue_severity = issue.get("severity")
                    issue_code = issue.get("code")
                    issue_diagnostics = issue.get("diagnostics")
                    single_error_info = (
                        f"Error processing: {filename}  "
                        + f"HTTP Code: {response.status_code}  "
                        + f"FHIR Severity: {issue_severity}  "
                        + f"Code: {issue_code}  "
                        + f"Diagnostics: {issue_diagnostics}"
                    )
                    if error_info == "":
                        error_info = single_error_info
                    else:
                        error_info += "\n\t" + single_error_info

        except Exception:
            # ; If an exception occurs while parsing FHIR JSON,
            # Log the full response content
            decoded_response = response.content.decode("utf-8")
            error_info = (
                f"HTTP Code: {response.status_code}, "
                + f"Response Content {decoded_response}"
            )

        logging.error(f"Error during $convert-data -- {error_info}")

        return {}

    return response.json()
