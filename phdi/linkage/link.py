import hashlib


def generate_hash_str(linking_identifier: str, salt_str: str) -> str:
    """
    Generate a hash for a given string of concatenated patient information. The hash
    will serve as a "unique" identifier for the patient.

    :param linking_identifier: The concatenation of a patient's name,
        address, and date of birth, delimited by dashes
    :param salt_str: The salt to concatenate onto the end to prevent
        being able to reverse-engineer PII
    :param return: Hash of the linking_identifier string
    """
    hash_obj = hashlib.sha256()
    to_encode = (linking_identifier + salt_str).encode("utf-8")
    hash_obj.update(to_encode)
    return hash_obj.hexdigest()
