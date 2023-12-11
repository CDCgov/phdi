import psycopg2
import json

connection = psycopg2.connect(
    database="ecr_viewer_db",
    user="postgres",
    password="pw",
    host="localhost",
    port=5432,
)

cursor = connection.cursor()

with open("example_eicr_with_rr_data_with_person.json", "r") as file:
    fhir_data = json.load(file)

try:
    query = "INSERT INTO fhir (ecr_id, data) VALUES (%s, %s)"
    cursor.execute(query, ("123456", json.dumps(fhir_data)))
    connection.commit()
    print("Data inserted successfully")
except psycopg2.Error as e:
    print("An error occurred:", e)
finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
