import psycopg2
import json
import os

connection = psycopg2.connect(
    database=os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PW"),
    host=os.environ.get("DATABASE_CONNECTION"),
    port=os.environ.get("DATABASE_PORT"),
)

cursor = connection.cursor()

directory = "./fhir_data"
data = {}

for filename in os.listdir(directory):
    full_path = os.path.join(directory, filename)
    if os.path.isfile(full_path):
        print(full_path)  # This prints the file name
        with open(full_path, "r") as file:
            fhir_data = json.load(file)
            uuid = fhir_data["entry"][0]["resource"]["id"]
            data[uuid] = fhir_data

try:
    query = (
        "INSERT INTO fhir (ecr_id, data) VALUES (%s, %s) ON CONFLICT (ecr_id) DO "
        "NOTHING"
    )
    for uuid, fhir_data in data.items():
        cursor.execute(query, (uuid, json.dumps(fhir_data)))
    connection.commit()
    print("Data inserted successfully")
except psycopg2.Error as e:
    print("An error occurred:", e)
finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
