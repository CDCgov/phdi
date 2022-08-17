import hashlib


def generate_hash_str(linking_identifier: str, salt_str: str) -> str:
    """
    Given a string made of concatenated patient information, generate
    a hash for this string to serve as a "unique" identifier for the
    patient.

    :param linking_identifier: The concatenation of a patient's name,
        address, and date of birth, delimited by dashes
    :param salt_str: The salt to concatenate onto the end to prevent
        being able to reverse-engineer PII
    """
    hash_obj = hashlib.sha256()
    to_encode = (linking_identifier + salt_str).encode("utf-8")
    hash_obj.update(to_encode)
    return hash_obj.hexdigest()
