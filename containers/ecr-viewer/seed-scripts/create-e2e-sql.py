import json
import os

import requests

BASEDIR = os.path.dirname(os.path.abspath(__file__))
URL = "http://orchestration-service:8080"


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
            query = f"""WITH inserted_data AS (
    INSERT INTO ecr_data (
        eICR_ID, patient_name_last, patient_name_first, patient_birth_date, data_source, report_date
    ) VALUES (
        '{ecr_id}', '{last_name}', '{first_name}', '{birth_date}', '{data_source}', {'NULL' if report_date is None else f"'{report_date}'"}
    )
    ON CONFLICT (eICR_ID) DO NOTHING
    RETURNING eICR_ID
), inserted_condition AS (
    INSERT INTO ecr_rr_conditions (uuid, eICR_ID, condition)
    VALUES (uuid_generate_v4(), (SELECT eICR_ID FROM inserted_data), '{reportable_condition}')
    RETURNING uuid
)
INSERT INTO ecr_rr_rule_summaries (uuid, ecr_rr_conditions_id, rule_summary)
VALUES (uuid_generate_v4(), (SELECT uuid FROM inserted_condition), '{rule_summary}')
RETURNING (SELECT eICR_ID FROM inserted_data);"""
            output_file.write(query)


def convert_files():
    """
    Convert eICR and RR into FHIR bundles using the FHIR converter.

    :return: A list of fhir bundles
    """
    print("Converting files...")
    fhir_bundles = []
    metadata = []
    folder_path = os.path.join(BASEDIR, "baseECR", "cypress")
    if os.path.isdir(folder_path):
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder)

            # Check if it's a directory
            if os.path.isdir(subfolder_path):
                with (
                    open(os.path.join(subfolder_path, "CDA_RR.xml"), "r") as rr_file,
                    open(
                        os.path.join(subfolder_path, "CDA_eICR.xml"), "r"
                    ) as eicr_file,
                ):
                    payload = {
                        "message_type": "ecr",
                        "data_type": "ecr",
                        "config_file_name": "create-seed-sql.json",
                        "message": eicr_file.read(),
                        "rr_data": rr_file.read(),
                    }

                    print(f"{URL}/process-message")
                    response = requests.post(f"{URL}/process-message", json=payload)
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
                                    os.path.join(folder_path, "bundle.json"), "w"
                                ) as fhir_file:
                                    json.dump(
                                        response["stamped_ecr"]["extended_bundle"],
                                        fhir_file,
                                        indent=4,
                                    )
                            if "message_parser_values" in response:
                                metadata.append(
                                    response["message_parser_values"]["parsed_values"]
                                )
                        print("Converted successfully.")
                    else:
                        print(f"Failed to convert. Response: {response.text}")
        return fhir_bundles, metadata


bundle_arr, metadata = convert_files()
save_sql_insert_fhir(bundle_arr)
save_sql_insert_metadata(metadata)
