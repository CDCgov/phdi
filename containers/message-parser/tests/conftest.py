import json
import os
from pathlib import Path

import lxml.etree as ET
import pytest
from rich.console import Console
from rich.table import Table
from testcontainers.compose import DockerCompose


@pytest.fixture(scope="session")
def read_json_from_test_assets():
    def _read_json(filename: str) -> dict:
        """
        Reads a JSON file from the test assets directory.
        """
        with open((Path(__file__).parent / "assets" / filename), "r") as file:
            return json.load(file)

    return _read_json


@pytest.fixture(scope="session")
def read_json_from_phdi_test_assets():
    def _read_json(filename: str) -> dict:
        """
        Reads a JSON file from the test assets directory.
        """
        with open(
            (
                Path(__file__).parent.parent.parent.parent
                / "tests"
                / "assets"
                / "general"
                / filename
            ),
            "r",
        ) as file:
            return json.load(file)

    return _read_json


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
            parser = (
                ET.XMLParser()
            )  # Adjust as necessary; removed `remove_blank_text=True` for compatibility
            tree = ET.parse(file, parser)
            return tree

    return _parse_file


@pytest.fixture(scope="session")
def read_schema_from_default_schemas():
    def _read_schema(filename: str) -> dict:
        """
        Reads a JSON schema from the default schemas directory.
        """
        with open(
            (Path(__file__).parent.parent / "app" / "default_schemas" / filename), "r"
        ) as file:
            return json.load(file)

    return _read_schema


@pytest.fixture(scope="session")
def setup(request):
    print("Setting up tests...")
    compose_path = os.path.join(os.path.dirname(__file__), "./integration/")
    compose_file_name = "docker-compose.yaml"
    message_parser = DockerCompose(compose_path, compose_file_name=compose_file_name)
    parser_url = "http://0.0.0.0:8080"

    message_parser.start()
    message_parser.wait_for(parser_url)
    print("Message Parser ready to test!")

    def teardown():
        print("Service logs...\n")
        print(message_parser.get_logs())
        print("Tests finished! Tearing down.")
        message_parser.stop()

    request.addfinalizer(teardown)


@pytest.fixture
def validate_xml():
    def _validate(xml_input: ET.ElementTree) -> bool:
        console = Console()

        # adjust the path to locate the XSD file relative to this conftest.py file
        xsd_path = (
            Path(__file__).parents[1]
            / "schema"
            / "extensions"
            / "SDTC"
            / "infrastructure"
            / "cda"
            / "CDA_SDTC.xsd"
        )

        with open(xsd_path, "rb") as xsd_file:
            xsd_tree = ET.XMLSchema(ET.parse(xsd_file))
            console.print("XSD schema loaded successfully", style="bold green")

        is_valid = xsd_tree.validate(xml_input)

        if is_valid:
            console.print(
                "The XML file is valid according to the XSD schema", style="bold green"
            )
            return True
        else:
            console.print("The XML file is not valid", style="bold red")
            table = Table(
                title="Validation Errors", show_header=True, header_style="bold magenta"
            )
            table.add_column("Line", style="dim", width=6, justify="right")
            table.add_column("Column", style="dim", width=6, justify="right")
            table.add_column("Message", overflow="fold")
            for error in xsd_tree.error_log:
                table.add_row(str(error.line), str(error.column), error.message)
            console.print(table)
            return False

    return _validate
