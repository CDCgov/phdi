import base64
import logging
import sys
import traceback
from typing import Optional

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


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Get the message from the request and decrypt it.

    Args:
        req (func.HttpRequest): the request object.
        Pass the encrypted text in the body of the request.

    Returns:
        func.HttpResponse: the decrypted message
    """
    return main_with_overload(req, None)


def main_with_overload(
    req: func.HttpRequest, settings_overload: Optional[DecryptSettings]
) -> func.HttpResponse:
    """Get the message from the request and decrypt it.

    Args:
        req (func.HttpRequest): the request object.
        Pass the encrypted text in the body of the request.

    Returns:
        func.HttpResponse: the decrypted message
    """
    encrypted_message = req.get_body()
    message_size = sys.getsizeof(encrypted_message)

    settings = settings_overload or DecryptSettings()
    logging.info(f"Decryption function fired. \n" f"Byte Size: {message_size} bytes")

    if not settings.private_key or not settings.private_key_password:
        logging.error("Error 500: No private key or password provided")
        return func.HttpResponse(
            "Server missing required settings",
            status_code=500,
        )

    if not encrypted_message:
        logging.error("Error 400: No message provided in request body")
        return func.HttpResponse(
            "Please pass the encrypted message in the request body",
            status_code=400,
        )
    try:
        decrypted_message = decrypt_message(
            encrypted_message, settings.private_key, settings.private_key_password
        )
        return func.HttpResponse(decrypted_message, mimetype="text/plain")
    except ValueError:
        tb = traceback.format_exc()
        logging.error(f"Decryption failed. Traceback: {tb}")
        return func.HttpResponse(
            "Decryption failed",
            status_code=500,
        )
