from pathlib import Path
import subprocess
import json
import uuid


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
    if input_type == "elr" or input_type == "vxu":
        template_directory_path = "/build/FHIR-Converter/data/Templates/Hl7v2"
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
        fhir_conversion_command, shell=True, capture_output=True
    )

    print(converter_response)

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
