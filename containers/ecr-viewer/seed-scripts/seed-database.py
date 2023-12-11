import psycopg2
import json

# import os

print("we're running the seed")

connection = psycopg2.connect(
    database="ecr_viewer_db",
    user="postgres",
    password="pw",
    host="localhost",
    port=5432,
)

# connection = psycopg2.connect(
#     database=os.environ.get("POSTGRES_DB"),
#     user=os.environ.get("POSTGRES_USER"),
#     password=os.environ.get("POSTGRES_PW"),
#     host=os.environ.get("DATABASE_CONNECTION"),
#     port=os.environ.get("DATABASE_PORT"),
# )

cursor = connection.cursor()

with open("example_eicr_with_rr_data_with_person.json", "r") as file:
    fhir_data = json.load(file)

uuid = fhir_data["entry"][0]["resource"]["id"]
print(uuid)

try:
    query = (
        "INSERT INTO fhir (ecr_id, data) VALUES (%s, %s) ON CONFLICT (ecr_id) DO "
        "NOTHING"
    )
    cursor.execute(query, (uuid, json.dumps(fhir_data)))
    connection.commit()
    print("Data inserted successfully")
except psycopg2.Error as e:
    print("An error occurred:", e)
finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
