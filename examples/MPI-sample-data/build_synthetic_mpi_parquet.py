# This script prepares synthetic patient data to mimic data that will seed the MPI.

import pandas as pd
import random
from faker import Faker

random.seed(410)
Faker.seed(414)

df = pd.read_csv(
    # locally stored file of synthetic LAC synthea data; user must change
    "~/20230106_LAC_10000_123_456/csv/patients.csv",
    usecols=[
        "Id",
        "BIRTHDATE",
        "FIRST",
        "LAST",
        "GENDER",
        "ADDRESS",
        "CITY",
        "STATE",
        "COUNTY",
        "ZIP",
        "SSN",
    ],
)


def add_emails(data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds an "email" column with a synthetic email address for each row of data.

    :param data: A DataFrame object.
    :return: A DataFrame object with an EMAIL column of synthetic email addresses.
    """
    fake = Faker()
    emails = [fake.email() for _ in range(len(data))]
    data["email"] = emails

    return data


def add_phone_numbers(column_name: str, data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a "phone" column with a synthetic phone number for each row of data.

    :param column_name: Column name.
    :param data: A DataFrame object.
    :return: A DataFrame object with a column of synthetic phone numbers.
    """
    fake = Faker()
    phones = [fake["en_US"].phone_number() for _ in range(len(data))]
    data[f"{column_name}"] = phones

    return data


# Add "Middle Name"
df["middle_name"] = "Middle"

# Add "MRN"
df["mrn"] = df["SSN"]
df["ssn"] = "123-456-7890"

# Add synthetic emails
df = add_emails(data=df)

# Add home phone numbers
df = add_phone_numbers(column_name="home_phone", data=df)

# Add cell phone numbers
df = add_phone_numbers(column_name="cell_phone", data=df)

# Add email
df = add_emails(data=df)

# Rename columns
df.rename(
    columns={
        "BIRTHDATE": "birthdate",
        "FIRST": "first_name",
        "LAST": "last_name",
        "GENDER": "sex",
        "ADDRESS": "address",
        "CITY": "city",
        "STATE": "state",
        "ZIP": "zip",
        "Id": "iris_id",
    },
    inplace=True,
)

df = df[
    [
        "iris_id",
        "birthdate",
        "ssn",
        "mrn",
        "first_name",
        "middle_name",
        "last_name",
        "sex",
        "address",
        "city",
        "state",
        "zip",
        "email",
        "home_phone",
        "cell_phone",
    ]
]

# Save
df.to_parquet("./examples/MPI-sample-data/synthetic_patient_mpi_seed_data.parquet")

# Save smaller sample for tests
df = df.head(10)
df.to_parquet("./tests/assets/synthetic_patient_mpi_seed_data.parquet")
