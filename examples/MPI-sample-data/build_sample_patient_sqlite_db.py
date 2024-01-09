# This script prepares synthetic patient data and loads it into a sqlite db that will
# be used for testing record linkage algorithms.
import sqlite3

import pandas as pd

df = pd.read_csv(
    # locally stord file of synthetic LAC synthea data; user must change
    "~/20230106_LAC_10000_123_456/csv/patients.csv",
    usecols=[
        "Id",
        "BIRTHDATE",
        "FIRST",
        "LAST",
        "SUFFIX",
        "MAIDEN",
        "RACE",
        "ETHNICITY",
        "GENDER",
        "ADDRESS",
        "CITY",
        "STATE",
        "COUNTY",
        "ZIP",
        "SSN",
    ],
)

# Transformations for LAC
df["FIRST4"] = df["FIRST"].str[0:4]
df["LAST4"] = df["LAST"].str[0:4]
df["ADDRESS4"] = df["ADDRESS"].str.replace(" ", "").str[0:4]

# Set up SQLite connection
tablename = "synthetic_patient_mpi"
columns = ", ".join(col for col in df.columns)
conn = sqlite3.connect("~/examples/MPI-sample-data/synthetic_patient_mpi_db")

conn.execute(
    f"""
          CREATE TABLE IF NOT EXISTS {tablename}
          ({columns})"""
)
df.to_sql(tablename, conn, if_exists="replace", index=False)

conn.commit()
conn.close()
