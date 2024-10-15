import json
import os

import requests

URL = "http://orchestration-service:8080"
BASEDIR = os.path.dirname(os.path.abspath(__file__))


def convert_files():
    """
    Convert eICR and RR into FHIR bundles using the FHIR converter.

    :return: A list of fhir bundles
    """
    print("Converting files...")
    subfolders = ["LA"]
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


convert_files()
