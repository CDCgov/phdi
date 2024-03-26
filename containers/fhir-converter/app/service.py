import json
import os
import re
import subprocess
import uuid
from pathlib import Path

import hl7
from lxml import etree


def add_data_source_to_bundle(bundle: dict, data_source: str) -> dict:
    """
    Given a FHIR bundle and a data source parameter the function
    will loop through the bundle and add a Meta.source entry for
    every resource in the bundle.

    :param bundle: The FHIR bundle to add minimum provenance to.
    :param data_source: The data source of the FHIR bundle.
    :return: The FHIR bundle with the a Meta.source entry for each
      FHIR resource in the bunle
    """
    if data_source == "":
        raise ValueError(
            "The data_source parameter must be a defined, non-empty string."
        )

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if "meta" in resource:
            meta = resource["meta"]
        else:
            meta = {}
            resource["meta"] = meta

        if "source" in meta:
            meta["source"].append(data_source)
        else:
            meta["source"] = [data_source]

    return bundle


def resolve_references(input_data: str):
    try:
        ecr = etree.fromstring(input_data.encode())
    except etree.XMLSyntaxError:
        return input_data

    ns = {"hl7": "urn:hl7-org:v3"}
    refs = ecr.xpath("//hl7:reference", namespaces=ns)
    for ref in refs:
        ref_id = ref.attrib["value"][1:]
        value = " ".join(ecr.xpath("//*[@ID='" + ref_id + "']/text()"))
        ref.text = value

    return etree.tostring(ecr).decode()


def convert_to_fhir(
    input_data: str,
    input_type: str,
    root_template: str,
) -> dict:
    """
    Call the Microsoft FHIR Converter CLI tool to convert an Hl7v2, or C-CDA message
    to FHIR R4. The message to be converted can be provided either as a string via the
    input_data_content argument, or by specifying a path to a file containing the
    message with input_data_file_path. One, but not both of these parameters is
    required. When conversion is successful a dictionary containing the resulting FHIR
    bundle is returned. When conversion fails a dictionary containing the response from
    the FHIR Converter is returned. In order to successfully call this function,
    the conversion tool must be installed. For information on how to do this please
    refer to FHIR-Converter-Installation-And-Usage-Guide. The source code for the
    converter can be found at https://github.com/microsoft/FHIR-Converter.

    :param input_data: The message to be converted as a string.
    :param input_type: The type of message to be converted. Valid values are
        "elr", "vxu", and "ecr".
    :param root_template: Name of the liquid template within to be used for conversion.
        Options are listed in the FHIR-Converter README.md.
    """

    # Setup path variables
    converter_project_path = (
        "/build/FHIR-Converter/output/Microsoft.Health.Fhir.Liquid.Converter.Tool.dll"
    )
    if input_type == "vxu" or input_type == "elr":
        template_directory_path = "/build/FHIR-Converter/data/Templates/Hl7v2"
        input_data = standardize_hl7_datetimes(input_data)
    elif input_type == "ecr":
        template_directory_path = "/build/FHIR-Converter/data/Templates/eCR"
    else:
        raise ValueError(
            f"Invalid input_type {input_type}. Valid values are 'hl7v2' and 'ecr'."
        )
    output_data_file_path = "/tmp/output.json"

    # Write input data to file
    input_data_file_path = Path(f"/tmp/{input_type}-input.txt")
    input_data_file_path.write_text(input_data)

    # Formulate command for the FHIR Converter.
    fhir_conversion_command = [
        f"dotnet {converter_project_path} ",
        "convert -- ",
        f"--TemplateDirectory {template_directory_path} ",
        f"--RootTemplate {root_template} ",
        f"--InputDataFile {str(input_data_file_path)} "
        f"--OutputDataFile {str(output_data_file_path)} ",
    ]

    fhir_conversion_command = "".join(fhir_conversion_command)

    # Call the FHIR Converter.
    converter_response = subprocess.run(
        fhir_conversion_command, shell=True, capture_output=True, text=True
    )
    # Print the standard output
    dev_mode = os.getenv("DEV_MODE", "false").lower()
    if dev_mode == "true":
        print(converter_response.stdout)
    # Process the response from FHIR Converter.
    if converter_response.returncode == 0:
        result = json.load(open(output_data_file_path))
        old_id = None
        # Generate a new UUID for the patient resource.
        for entry in result["FhirResource"]["entry"]:
            if entry["resource"]["resourceType"] == "Patient":
                old_id = entry["resource"]["id"]
                break
        new_id = str(uuid.uuid4())
        result = json.dumps(result)
        if old_id is not None:
            result = result.replace(old_id, new_id)
        result = json.loads(result)
        add_data_source_to_bundle(result["FhirResource"], input_type)

    else:
        result = vars(converter_response)
        result["fhir_conversion_failed"] = "true"

    return {"response": result}


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
        print(
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
        print(f"Segment {segment_id} not found in message.")


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
