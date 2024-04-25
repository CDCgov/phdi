import csv
import json
import os

# Specify the path to your JSON file and the output CSV file
HOME_DIR = "/Users/rob/ersd"  # update to wherever you download json
file = "eRSDv2_specification_bundle.json"
conditions = os.path.join(HOME_DIR, "{0}_conditions.csv".format(file.split(".")[0]))
values = os.path.join(HOME_DIR, "{0}_value_set.csv".format(file.split(".")[0]))


def conditions_to_csv(json_file_path, csv_file_path):
    """_summary_

    Args:
        json_file_path (_type_): _description_
        csv_file_path (_type_): _description_
    """
    # Open the JSON file
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)

        # Open the CSV file for writing
        with open(csv_file_path, mode="w", newline="") as csv_file:
            fieldnames = [
                "id",
                "name",
                "title",
                "status",
                "description",
                "use_context_system",
                "use_context_code",
                "use_context_text",
                "system",
                "version",
                "code",
                "display",
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            # Loop through each entry in the JSON data
            for entry in data["entry"]:
                resource = entry.get("resource", {})
                # Base attributes
                id = resource.get("id", "")

                # Check if id starts with a number
                if id and id[0].isdigit():
                    name = resource.get("name", "")
                    title = resource.get("title", "")
                    status = resource.get("status", "")
                    description = resource.get("description", "")

                    # Extract useContext details
                    use_context = resource.get("useContext", [])
                    use_context_system = ""
                    use_context_code = ""
                    use_context_text = ""
                    if use_context:
                        value_codeable = (
                            use_context[0]
                            .get("valueCodeableConcept", {})
                            .get("coding", [])
                        )
                        if value_codeable:
                            use_context_system = value_codeable[0].get("system", "")
                            use_context_code = value_codeable[0].get("code", "")
                            use_context_text = (
                                use_context[0]
                                .get("valueCodeableConcept", {})
                                .get("text", "")
                            )

                    # Handle compose.include
                    includes = resource.get("compose", {}).get("include", [])
                    for include in includes:
                        system = include.get("system", "")
                        version = include.get("version", "")
                        for concept in include.get("concept", []):
                            writer.writerow(
                                {
                                    "id": id,
                                    "name": name,
                                    "title": title,
                                    "status": status,
                                    "description": description,
                                    "use_context_system": use_context_system,
                                    "use_context_code": use_context_code,
                                    "use_context_text": use_context_text,
                                    "system": system,
                                    "version": version,
                                    "code": concept.get("code", ""),
                                    "display": concept.get("display", ""),
                                }
                            )

                    # Handle expansion.contains
                    contains = resource.get("expansion", {}).get("contains", [])
                    for contain in contains:
                        system = contain.get("system", "")
                        version = contain.get("version", "")
                        writer.writerow(
                            {
                                "id": id,
                                "name": name,
                                "title": title,
                                "status": status,
                                "description": description,
                                "use_context_system": use_context_system,
                                "use_context_code": use_context_code,
                                "use_context_text": use_context_text,
                                "system": system,
                                "version": version,
                                "code": contain.get("code", ""),
                                "display": contain.get("display", ""),
                            }
                        )


def valuesets_to_csv(json_file_path, csv_file_path):
    """_summary_

    Args:
        json_file_path (_type_): _description_
        csv_file_path (_type_): _description_
    """
    # Open the JSON file
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)

        # Open the CSV file for writing
        with open(csv_file_path, mode="w", newline="") as csv_file:
            fieldnames = [
                "id",
                "name",
                "title",
                "status",
                "value_version",
                "publisher",
                "date",
                "use_context_system",
                "use_context_code",
                "system",
                "version",
                "code",
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            # Loop through each entry in the JSON data
            for entry in data["entry"]:
                resource = entry.get("resource", {})
                # Base attributes
                id = resource.get("id", "")

                # Check if id starts with a letter
                if id and id[0].isalpha():
                    name = resource.get("name", "")
                    title = resource.get("title", "")
                    status = resource.get("status", "")
                    version = resource.get("version", "")
                    publisher = resource.get("publisher", "")
                    date = resource.get("date", "")

                    # Handle use context details
                    use_context_system = ""
                    use_context_code = ""
                    if resource.get("useContext"):
                        use_context = resource["useContext"][0]
                        use_context_system = use_context["code"]["system"]
                        use_context_code = use_context["valueCodeableConcept"][
                            "coding"
                        ][0]["code"]

                    # Handle compose.include
                    includes = resource.get("compose", {}).get("include", [])
                    for include in includes:
                        for vs in include.get("valueSet", []):
                            # Extract only the numerical identifier if the
                            # valueSet URL is formatted as expected
                            code = (
                                vs.split("/")[-1]
                                if vs.startswith(
                                    "http://cts.nlm.nih.gov/fhir/ValueSet/"
                                )
                                else vs
                            )
                            writer.writerow(
                                {
                                    "id": id,
                                    "name": name,
                                    "title": title,
                                    "status": status,
                                    "value_version": version,
                                    "publisher": publisher,
                                    "date": date,
                                    "use_context_system": use_context_system,
                                    "use_context_code": use_context_code,
                                    "system": "",
                                    "version": "",
                                    "code": code,
                                }
                            )
                    # Handle expansion.contains
                    contains = resource.get("expansion", {}).get("contains", [])
                    for contain in contains:
                        code = (
                            contain.get("code", "").split("/")[-1]
                            if contain.get("code", "").startswith(
                                "http://cts.nlm.nih.gov/fhir/ValueSet/"
                            )
                            else contain.get("code", "")
                        )
                        writer.writerow(
                            {
                                "id": id,
                                "name": name,
                                "title": title,
                                "status": status,
                                "value_version": version,
                                "publisher": publisher,
                                "date": date,
                                "use_context_system": use_context_system,
                                "use_context_code": use_context_code,
                                "system": contain.get("system", ""),
                                "version": contain.get("version", ""),
                                "code": code,
                            }
                        )


# Call the function to process the JSON and create the CSVs
conditions_to_csv(file, conditions)
valuesets_to_csv(file, values)
