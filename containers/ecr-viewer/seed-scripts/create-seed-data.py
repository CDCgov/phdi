import json
import os

import requests

URL = "http://orchestration-service:8080"
BASEDIR = os.path.dirname(os.path.abspath(__file__))


def save_sql_insert(fhir_bundles):
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


def convert_files():
    """
    Convert eICR and RR into FHIR bundles using the FHIR converter.

    :return: A list of fhir bundles
    """
    print("Converting files...")
    fhir_bundles = []
    for folder in os.listdir(os.path.join(BASEDIR, "baseECR")):
        folder_path = os.path.join(BASEDIR, "baseECR", folder)
        if os.path.isdir(folder_path):
            with (
                open(os.path.join(folder_path, "CDA_RR.xml"), "r") as rr_file,
                open(os.path.join(folder_path, "CDA_eICR.xml"), "r") as eicr_file,
            ):
                payload = {
                    "message_type": "ecr",
                    "data_type": "ecr",
                    "config_file_name": "seed-ecr-viewer-config.json",
                    "message": eicr_file.read(),
                    "rr_data": rr_file.read(),
                }

                print(f"{URL}/process-message")
                response = requests.post(f"{URL}/process-message", json=payload)
                if response.status_code == 200:
                    resp_json = response.json()
                    fhir_bundles.append(resp_json["processed_values"]["bundle"])
                    print(f"Converted {folder} successfully.")
                else:
                    print(f"Failed to convert {folder}. Response: {response.text}")
    return fhir_bundles


bundle_arr = convert_files()
save_sql_insert(bundle_arr)
