from dataclasses import dataclass
import os


@dataclass
class Settings:
    private_key_password = os.getenv("PrivateKeyPassword")
    private_key = os.getenv("PrivateKey")
    azure_storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
