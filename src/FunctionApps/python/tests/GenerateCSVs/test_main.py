import io

from unittest import mock
from config import get_required_config

from GenerateCSVs import main, generate_csvs
from GenerateCSVs.fhir import RECORD_TYPE_VXU, RECORD_TYPE_ELR, RECORD_TYPE_ECR

TEST_ENV = {
    "CONTAINER_URL": "some-url",
    "CSV_INPUT_PREFIX": "input/path/",
    "CSV_OUTPUT_PREFIX": "output/path",
}


@mock.patch("GenerateCSVs.read_bundles_by_type")
@mock.patch.dict("os.environ", TEST_ENV)
def test_generate_csvs(mock_bundle_reader):
    """
    Mock everything to do a test run where we return a single row, of a single col
    with a single record per type
    """

    mock_bundle_reader.return_value = [
        (RECORD_TYPE_VXU, {}),
        (RECORD_TYPE_ECR, {}),
        (RECORD_TYPE_ELR, {}),
    ]

    mock_types_def = {
        RECORD_TYPE_VXU: (["vxucol"], mock.Mock(return_value=["vxurec"])),
        RECORD_TYPE_ELR: (["elrcol"], mock.Mock(return_value=["elrrec"])),
        RECORD_TYPE_ECR: (["ecrcol"], mock.Mock(return_value=["ecrrec"])),
    }

    with mock.patch("GenerateCSVs.RECORD_TYPES", mock_types_def):
        results = generate_csvs(
            get_required_config("CONTAINER_URL"),
            get_required_config("CSV_INPUT_PREFIX"),
        )

    assert len(results) == 3
    assert results[RECORD_TYPE_VXU].getvalue() == "vxucol\r\nvxurec\r\n"
    assert results[RECORD_TYPE_ELR].getvalue() == "elrcol\r\nelrrec\r\n"
    assert results[RECORD_TYPE_ECR].getvalue() == "ecrcol\r\necrrec\r\n"


@mock.patch("GenerateCSVs.write_csvs")
@mock.patch("GenerateCSVs.generate_csvs")
@mock.patch.dict("os.environ", TEST_ENV)
def test_main(mock_generate_csvs, mock_write_csvs):

    generate_return = {
        RECORD_TYPE_VXU: io.StringIO("vxucol\r\nvxurec\r\n"),
        RECORD_TYPE_ELR: io.StringIO("elrcol\r\nelrrec\r\n"),
        RECORD_TYPE_ECR: io.StringIO("ecrcol\r\necrrec\r\n"),
    }

    mock_generate_csvs.return_value = generate_return

    mock_write_csvs.return_value = None

    main(None)

    mock_generate_csvs.assert_called_with("some-url", "input/path/")

    mock_write_csvs.assert_called_with("some-url", "output/path", generate_return)
