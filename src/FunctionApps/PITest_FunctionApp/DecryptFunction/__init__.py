import base64
import logging
from importlib.resources import files
from pathlib import Path

import azure.functions as func
import pgpy

from .settings import Settings


def decrypt_message(message: bytes, private_key_string: str, password: str) -> bytes:
    logging.info("Decrypting message")
    encrypted_message = pgpy.PGPMessage.from_blob(message)
    decoded_key_string = base64.b64decode(private_key_string)
    pgp_key, _ = pgpy.PGPKey.from_blob(decoded_key_string)
    with pgp_key.unlock(password):
        decrypted = pgp_key.decrypt(encrypted_message).message
    logging.info("Decryption complete")
    return decrypted


def main(inputblob: func.InputStream, outputblob: func.Out[bytes]):

    settings = Settings()
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
