import json
import os

import requests

URL = "http://orchestration-service:8080"
BASEDIR = os.path.dirname(os.path.abspath(__file__))


def save_sql_insert_fhir(fhir_bundles):
    """
    Save FHIR bundles as SQL INSERT queries to a file.

    :param fhir_bundles: A list of FHIR bundles to be saved as SQL INSERT queries.
    """
    with open(os.path.join(BASEDIR, "sql", "data.sql"), "w") as output_file:
        for bundle in fhir_bundles:
            bundle_id = bundle["entry"][0]["resource"]["id"]
            bundle = json.dumps(bundle).replace("'", "''")
            query = f"INSERT INTO fhir (ecr_id, data) VALUES ('{bundle_id}', '{bundle}') ON CONFLICT (ecr_id) DO NOTHING;\n"
            output_file.write(query)


def save_sql_insert_metadata(metadata):
    """
    Save metadata as SQL INSERT queries to a file.

    :param metadata: A list of parsed values to be saved as SQL INSERT queries.
    """
    with open(os.path.join(BASEDIR, "sql", "data.sql"), "a") as output_file:
        for parsed_values in metadata:
            ecr_id = parsed_values["ecr_id"]
            last_name = parsed_values["last_name"]
            first_name = parsed_values["first_name"]
            birth_date = parsed_values["birth_date"]
            reportable_condition = parsed_values["reportable_condition"]
            rule_summary = parsed_values["rule_summary"]
            report_date = parsed_values["report_date"]
            data_source = "DB"
            query = f"""INSERT INTO fhir_metadata (
              ecr_id,patient_name_last,patient_name_first,patient_birth_date,data_source,reportable_condition,rule_summary,report_date
            ) VALUES (
              '{ecr_id}','{last_name}','{first_name}','{birth_date}','{data_source}','{reportable_condition}','{rule_summary}',{'NULL' if report_date is None else f"'{report_date}'"}
            ) ON CONFLICT (ecr_id) DO NOTHING;\n"""
            output_file.write(query)


def convert_files():
    """
    Convert eICR and RR into FHIR bundles using the FHIR converter.

    :return: A list of fhir bundles
    """
    print("Converting files...")
    fhir_bundles = []
    metadata = []
    # List the subfolders you want to check (TN, ME, LA)
    subfolders = ["TN", "ME", "LA", "KY"]
    # Iterate over the subfolders
    for subfolder in subfolders:
        subfolder_path = os.path.join(BASEDIR, "baseECR", subfolder)

        # Check if the subfolder exists and is a directory
        if os.path.isdir(subfolder_path):
            # Now iterate through the folders inside each subfolder
            for folder in os.listdir(subfolder_path):
                folder_path = os.path.join(subfolder_path, folder)

                # Check if it's a directory
                if os.path.isdir(folder_path):
                    try:
                        # Open the necessary files in the folder
                        with (
                            open(
                                os.path.join(folder_path, "CDA_RR.xml"), "r"
                            ) as rr_file,
                            open(
                                os.path.join(folder_path, "CDA_eICR.xml"), "r"
                            ) as eicr_file,
                        ):
                            payload = {
                                "message_type": "ecr",
                                "data_type": "ecr",
                                "config_file_name": "seed-ecr-viewer-config.json",
                                "message": eicr_file.read(),
                                "rr_data": rr_file.read(),
                            }

                            print(f"{URL}/process-message")
                            response = requests.post(
                                f"{URL}/process-message", json=payload
                            )
                            if response.status_code == 200:
                                responses_json = response.json()["processed_values"][
                                    "responses"
                                ]
                                for response in responses_json:
                                    if "stamped_ecr" in response:
                                        fhir_bundles.append(
                                            response["stamped_ecr"]["extended_bundle"]
                                        )
                                        with open(
                                            os.path.join(folder_path, "bundle.json"),
                                            "w",
                                        ) as fhir_file:
                                            json.dump(
                                                response["stamped_ecr"][
                                                    "extended_bundle"
                                                ],
                                                fhir_file,
                                                indent=4,
                                            )
                                    if "message_parser_values" in response:
                                        metadata.append(
                                            response["message_parser_values"][
                                                "parsed_values"
                                            ]
                                        )
                                        print(
                                            f"Converted {folder} in {subfolder} successfully."
                                        )
                            # Handle the case where the response fails
                            else:
                                print(f"Failed to convert {folder} in {subfolder}.")
                    # Handle file not found or other potential errors
                    except FileNotFoundError as e:
                        print(f"Required file not found in {folder_path}: {e}")
                    except Exception as e:
                        print(
                            f"An error occurred processing {folder} in {subfolder}: {e}"
                        )
                # If the subfolder is not a directory, print a message
                else:
                    print(f"{subfolder_path} is not a valid directory.")
    if os.environ.get("NEXT_PUBLIC_NON_INTEGRATED_VIEWER") == "true":
        return fhir_bundles, metadata
    else:
        return fhir_bundles


if os.environ.get("NEXT_PUBLIC_NON_INTEGRATED_VIEWER") == "true":
    print("Running non integrated viewer")
    bundle_arr, metadata = convert_files()
    save_sql_insert_fhir(bundle_arr)
    save_sql_insert_metadata(metadata)
else:
    print("Running viewer")
    bundle_arr = convert_files()
    save_sql_insert_fhir(bundle_arr)
