import os
from pathlib import Path

import lxml.etree as ET
import pytest


def pytest_configure():
    """Add Trigger Code Reference service URL"""
    os.environ["TRIGGER_CODE_REFERENCE_URL"] = (
        "http://trigger-code-reference-service:8080"
    )


@pytest.fixture(scope="session")
def read_file_from_test_assets():
    def _read_file(filename: str) -> str:
        """
        Reads a file from the test assets directory.
        """
        with open((Path(__file__).parent / "assets" / filename), "r") as file:
            return file.read()

    return _read_file


@pytest.fixture(scope="session")
def parse_file_from_test_assets():
    def _parse_file(filename: str) -> ET.ElementTree:
        """
        Parses a file from the assets directory into an ElementTree.
        """
        with open((Path(__file__).parent / "assets" / filename), "r") as file:
            parser = ET.XMLParser()
            tree = ET.parse(file, parser)
            return tree

    return _parse_file
