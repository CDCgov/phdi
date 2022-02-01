import logging

import azure.functions as func
import pgpy
from importlib.resources import files
from pathlib import Path
import logging

from .settings import Settings


def decrypt_message(message: bytes, private_key_string: str, password: str) -> bytes:
    logging.info("Decrypting message")
    encrypted_message = pgpy.PGPMessage.from_blob(message)
    pgp_key, _ = pgpy.PGPKey.from_blob(private_key_string)
    with pgp_key.unlock(password):
        decrypted = pgp_key.decrypt(encrypted_message).message
    logging.info("Decryption complete")
    return decrypted.message


def main(input_blob: func.InputStream, output_blob: func.Out[bytes]):

    settings = Settings()
    logging.info(
        f"Python blob trigger function processed blob \n"
        f"Name: {input_blob.name}\n"
        f"Blob Size: {input_blob.length} bytes"
    )

    logging.info(f"Decrypting {input_blob.name}")
    decrypted_message = decrypt_message(
        input_blob.read(), settings.private_key, settings.private_key_password
    )
    output_blob.set(decrypted_message)
