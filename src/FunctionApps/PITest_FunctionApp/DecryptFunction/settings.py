from dataclasses import dataclass
import os


@dataclass
class Settings:
    private_key_password = os.getenv("PRIVATE_KEY_PASSWORD")
    private_key = os.getenv("PRIVATE_KEY")
    azure_storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
