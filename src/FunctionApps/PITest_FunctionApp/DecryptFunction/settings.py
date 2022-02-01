from dataclasses import dataclass
import os


@dataclass
class Settings:
    private_key_password = os.environ["PRIVATE_KEY_PASSWORD"]
    private_key = os.environ["PRIVATE_KEY"]
    azure_storage_connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
