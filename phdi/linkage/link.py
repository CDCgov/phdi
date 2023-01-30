import hashlib
import pandas as pd
from typing import List, Dict


def generate_hash_str(linking_identifier: str, salt_str: str) -> str:
    """
    Generates a hash for a given string of concatenated patient information. The hash
    serves as a "unique" identifier for the patient.

    :param linking_identifier: The value to be hashed.  For example, the concatenation
      of a patient's name, address, and date of birth, delimited by dashes.
    :param salt_str: The salt to use with the hash. This is intended to prevent
      reverse engineering of the PII used to create the hash.
    :return: The hash of the linking_identifier string.
    """
    hash_obj = hashlib.sha256()
    to_encode = (linking_identifier + salt_str).encode("utf-8")
    hash_obj.update(to_encode)
    return hash_obj.hexdigest()


def block_parquet_data(path: str, blocks: List) -> Dict:
    """
    Generates dictionary of blocked data where each key is a block and each value is a
    distinct list of lists containing the data for a given block.

    :param path: Path to parquet file containing data that needs to be linked.
    :param blocks: List of columns to be used in blocks.
    :return: A dictionary of with the keys as the blocks and the values as the data
    within each block, stored as a list of lists.
    """
    data = pd.read_parquet(path, engine="pyarrow")
    blocked_data = dict(tuple(data.groupby(blocks)))

    return blocked_data
