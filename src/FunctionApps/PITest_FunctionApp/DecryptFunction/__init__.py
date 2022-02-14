import base64
import logging

import azure.functions as func
import pgpy

from .settings import DecryptSettings


def decrypt_message(message: bytes, private_key_string: str, password: str) -> bytes:
    """Decrypt a message using a specified private key in base64 encoded format.

    Args:
        message (bytes): the message, as byte string
        private_key_string (str): the private string in base64 encoded format
        password (str): the password for the private key

    Returns:
        bytes: the decrypted version of the message
    """
    logging.info("Decrypting message")
    encrypted_message = pgpy.PGPMessage.from_blob(message)
    decoded_key_string = base64.b64decode(private_key_string)
    pgp_key, _ = pgpy.PGPKey.from_blob(decoded_key_string)
    with pgp_key.unlock(password):
        decrypted = pgp_key.decrypt(encrypted_message).message
    logging.info("Decryption complete")
    return decrypted


def main(inputblob: func.InputStream, outputblob: func.Out[bytes]):
    """Decrypt a message at the specified input path and place it in the specified output path

    Args:
        inputblob (func.InputStream): the input blob (path matches pattern in function.json) - passed automatically by Azure
        outputblob (func.Out[bytes]): the output blob (path matches pattern in function.json) - file deposited here on completion
    """  # noqa: E501

    settings = DecryptSettings()
    logging.info(
        f"Python blob trigger function processed blob \n"
        f"Name: {inputblob.name}\n"
        f"Blob Size: {inputblob.length} bytes"
    )

    logging.info(f"Decrypting {inputblob.name}")
    decrypted_message = decrypt_message(
        inputblob.read(), settings.private_key, settings.private_key_password
    )
    outputblob.set(decrypted_message)
