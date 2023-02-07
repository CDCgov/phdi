# This file builds a dataset of synthetic patient data to simulate incoming fields
# derived from ELR/ECR/ADT data that could be used to link records. Names, addresses,
# and DOBs have been intentionally scrambled and misspelled.

import sqlite3
import pandas as pd
import random
from random import shuffle
import numpy as np

# Set up proportions of scramble


PROPORTION_NO_ERRORS = 0.6
PROPORTION_BAD_FIRST_NAME = 0.1
PROPORTION_BAD_LAST_NAME = 0.05
PROPORTION_NICKNAME = 0.15
PROPORTION_BAD_DOB = 0.05
PROPORTION_BAD_ZIP = 0.05

PROPORTION_MISSING_ADDRESS_LAC = 0.06

# Set seed
seed = 123

# Functions


def scramble_dob(dob: str) -> str:
    """
    Scrambles a date of birth (DOB) that is in the form YYYY-MM-DD. DOBs can be
    scrambled by year (last two digits are swapped), month (two digits are swapped),
    day (digits are swapped), or diff. For diff, the year, month, or day are randomly
    increased or decreased by a value of 1, e.g. 1984 could become 1983 or 1984.

    :param dob: Date of birth string in the format YYYY-MM-DD.
    :return: Scrambled date of birth string in the format YYYY-MM-DD.


    """
    # Randomly select how DOB will be scrambled.
    method = random.choice(["year", "month", "day", "diff"])

    # Swap last two digits of the year
    if method == "year":
        scrambled_dob = dob[:2] + dob[3] + dob[2] + dob[4:]
    # Swap the two digits of the month
    elif method == "month":
        scrambled_dob = dob[:5] + dob[6] + dob[5] + dob[7:]
    # Swap the two digits of the day
    elif method == "day":
        scrambled_dob = dob[:-2] + dob[-1] + dob[-2]
    # Add or subtract 1 from a DOB's year, month, or day value
    elif method == "diff":
        time = random.choice(["year", "month", "day"])
        plus_minus = random.choice([-1, 1])
        if time == "year":
            scrambled_dob = str(int(dob.split("-")[0]) + plus_minus) + dob[4:]
        elif time == "month":
            scrambled_dob = (
                dob[0:5] + str(int(dob.split("-")[1]) + plus_minus).zfill(2) + dob[7:]
            )
        elif time == "day":
            scrambled_dob = dob[0:8] + str(int(dob.split("-")[2]) + plus_minus).zfill(2)
    return scrambled_dob


def scramble_name(name: str) -> str:
    """
    Scrambles a single name by randomly adding an existing letter, removing an
    existing letter, or swapping two existing letters.

    :param name: Name, as a string, to be scrambled.
    :return: Scrambled name, as a string.

    """
    # Randomly select scrambling method
    method = random.choice(["add", "remove", "swap"])
    # Randomly select non-first character in name
    char = random.choice(range(1, len(name)))

    if method == "add":
        scrambled_name = name[0:char] + name[char] + name[char:]
    elif method == "remove":
        scrambled_name = name[0:char] + name[char + 1 :]
    elif method == "swap":
        subset_length = random.choice([3, 4, 5])  # number of characters to swap
        # Make sure subset length can fit in the name
        while subset_length > len(name):
            subset_length -= 1
        while char + subset_length > len(name):
            char -= 1
        subset_chars = list(name[char : char + subset_length])
        random.shuffle(subset_chars)
        scrambled_name = (
            name[:char] + "".join(subset_chars) + name[char + subset_length :]
        )

    return scrambled_name


def scramble_zip(zip: str) -> str:
    """
    Scrambles all digits of a zip code except for the first one.

    :param zip: Zip code containing only numbers, as a string.
    :return: Zip code with the last [1:] digits scrambled.

    """
    zip_list = list(zip[1:])
    shuffle(zip_list)
    scrambled_zip = zip[0] + "".join(zip_list)
    return scrambled_zip


def swap_name_for_nickname(name: str, names_to_nicknames: dict) -> str:
    """
    Swaps in a random, associated nickname for a given name, if the name has any
    associated nicknames, e.g., 'Bill' or 'Will' could be randomly swapped for
    'William' but 'Eddie' could not be because it is not an associated nickname for
    'William'.

    :param name: Single name
    :names_to_nicknames: Dictionary containing first names and their associated
        nicknames.
    :return: Randomly chosen nickname that corresponds to input name. If no nicknames
        correspond to the input name, the original name is returned instead.

    """
    if name.upper() in names_to_nicknames.keys():
        swapped_name = random.choice(names_to_nicknames[name.upper()]).title()
        return swapped_name
    else:
        return name


def add_missing_values(data: pd.DataFrame, missingness: dict) -> pd.DataFrame:
    """
    Randomly changes values in a column to missing (nan).

    :param data: A DataFrame object.
    :param missingness: Dictionary containing the percent missing (as a float) to
        introduce for each column, e.g., "BIRTHDATE": 0.02.
    :return: DataFrame with randomly missing data from the input column.

    """
    for column, perc_missing in missingness.items():
        data[column] = data[column].sample(frac=(1 - perc_missing))
    return data


def add_copies(data: pd.DataFrame, num_copies: int) -> pd.DataFrame:
    """
    Adds duplicate rows to a DataFrame.

    :param data: A DataFrame object.
    :param num_copies: The number of duplicate rows to add for each existing row.
    :return: A DataFrame object with duplicate rows.

    """
    data_with_copies = pd.DataFrame(np.repeat(data.values, num_copies, axis=0))
    data_with_copies.columns = data.columns

    return data_with_copies


def scramble_data(
    source_data: pd.DataFrame, seed: int, names_to_nicknames: dict, missingness: dict
) -> pd.DataFrame:
    """
    Scrambles a dataset including names, dates of birth, and zip codes. This function
    assumes the dataset contains the following columns:
    - BIRTHDATE
    - ZIP
    - FIRST (for first name)
    - LAST (for last name)
    - Id

    :param source_data: DataFrame object.
    :param seed: Seed.
    :names_to_nicknames: Dictionary containing first names and their associated
        nicknames.
    :missingness: Dictionary containing the percent missing (as a float) to
        introduce for each column, e.g., "BIRTHDATE": 0.02.
    :return: DataFrame object that has been scrambled.

    """

    source_data["ZIP"] = source_data["ZIP"].astype(str).str.split(".").str[0]

    # Introduce missingness
    source_data = add_missing_values(source_data, missingness)

    source_data_with_copies = add_copies(source_data, num_copies=3)

    good_data = source_data_with_copies.sample(
        frac=PROPORTION_NO_ERRORS, random_state=seed
    )

    # Scramble DOB in subsample
    bad_dob = source_data_with_copies.sample(frac=PROPORTION_BAD_DOB, random_state=seed)
    bad_dob["BIRTHDATE"] = bad_dob["BIRTHDATE"].apply(lambda x: scramble_dob(x))
    bad_dob["bad_dob"] = 1

    # Scramble zip in subsample
    bad_zip = source_data_with_copies.sample(frac=PROPORTION_BAD_ZIP, random_state=seed)
    bad_zip["bad_zip"] = 1
    bad_zip["ZIP"] = bad_zip["ZIP"].apply(lambda x: scramble_zip(x))

    # Assign nicknames in subsample
    bad_name_nickname = source_data_with_copies.sample(
        frac=PROPORTION_NICKNAME, random_state=seed
    )
    bad_name_nickname["bad_name_nickname"] = 1
    bad_name_nickname["FIRST"] = bad_name_nickname["FIRST"].apply(
        lambda x: swap_name_for_nickname(x, names_to_nicknames)
    )

    # Scramble first names in subsample
    bad_name_scramble_first = source_data_with_copies.sample(
        frac=PROPORTION_BAD_FIRST_NAME, random_state=seed
    )
    bad_name_scramble_first["bad_name_scramble_first"] = 1
    bad_name_scramble_first["FIRST"] = bad_name_scramble_first["FIRST"].apply(
        lambda x: scramble_name(x)
    )
    bad_name_scramble_first["FIRST4"] = bad_name_scramble_first["FIRST"].str[0:4]

    # Scramble last names in subsample
    bad_name_scramble_last = source_data_with_copies.sample(
        frac=PROPORTION_BAD_LAST_NAME, random_state=seed
    )
    bad_name_scramble_last["bad_name_scramble_last"] = 1
    bad_name_scramble_first["LAST"] = bad_name_scramble_last["LAST"].apply(
        lambda x: scramble_name(x)
    )
    bad_name_scramble_last["LAST4"] = bad_name_scramble_last["LAST"].str[0:4]

    # Compile data
    data = pd.concat(
        [
            good_data,
            bad_dob,
            bad_zip,
            bad_name_scramble_first,
            bad_name_scramble_last,
            bad_name_nickname,
        ],
        ignore_index=True,
    ).sort_values(by="Id")
    data = data.fillna(0)

    # Count number of true matches per Id
    data["num_matches"] = data.groupby("Id")["Id"].transform("count")

    return data


# Get nicknames
names_to_nicknames = {}
with open("./phdi/harmonization/phdi_nicknames.csv", "r") as fp:
    for line in fp:
        if line.strip() != "":
            name, nicks = line.strip().split(":", 1)
            names_to_nicknames[name] = nicks.split(",")

# Intialize LAC-specific missingness
lac_missingness = {"ADDRESS": PROPORTION_MISSING_ADDRESS_LAC}

# Get source data
conn = sqlite3.connect("./examples/MPI-sample-data/synthetic_patient_mpi_db")
df = pd.read_sql_query("SELECT * from synthetic_patient_mpi", conn)
conn.commit()
conn.close()


source_data = df.copy()

scrambled_data = scramble_data(
    source_data,
    seed=123,
    names_to_nicknames=names_to_nicknames,
    missingness=lac_missingness,
)
scrambled_data.to_csv(
    "./examples/Record-Linkage-sample-data/sample_record_linkage_data_scrambled.csv",
    index=False,
)
