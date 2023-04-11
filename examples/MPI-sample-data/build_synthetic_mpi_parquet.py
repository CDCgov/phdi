# This script prepares synthetic patient data to mimic data that will seed the MPI.

import pandas as pd
import random
from random import randint
from string import ascii_letters

random.seed(410)

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
    Adds an "email" column with a synthetic email address for each row of data. The
    email address domains are limited to the most common providers in the US (gmail,
    yahoo, and hotmail).

    :param data: A DataFrame object.
    :return: A DataFrame object with an EMAIL column of synthetic email addresses.
    """
    emails = [
        "".join(random.choice(ascii_letters) for x in range(10))
        for _ in range(len(data))
    ]
    emails = [
        (email + random.choice(["@gmail.com", "@yahoo.com", "@hotmail.com"]))
        for email in emails
    ]

    data["email"] = emails

    return data


def add_phone_numbers(column_name: str, data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a "EMAIL" column with a synthetic phone number for each row of data. The
    phone number area codes are limited to the most common area codes in Los Angeles
    county (213, 310, 424, 661, 818, and 323).

    :param column_name: Column name.
    :param data: A DataFrame object.
    :return: A DataFrame object with a column of synthetic phone numbers.
    """
    phones = ["".join(str(randint(0, 9)) for x in range(7)) for _ in range(len(data))]
    phones = [
        int((random.choice(["213", "310", "424", "661", "818", "323"]) + phone))
        for phone in phones
    ]

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
df.to_parquet(
    "./examples/MPI-sample-data/synthetic_patient_mpi_seed_data.gzip",
    compression="gzip",
)
