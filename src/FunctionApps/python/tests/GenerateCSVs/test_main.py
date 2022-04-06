from unittest import mock

from GenerateCSVs import generate_csvs
from GenerateCSVs.fhir import RECORD_TYPE_VXU, RECORD_TYPE_ELR, RECORD_TYPE_ECR


@mock.patch("GenerateCSVs.read_bundles_by_type")
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
        results = generate_csvs()

    assert len(results) == 3
    assert results[RECORD_TYPE_VXU].getvalue() == "vxucol\r\nvxurec\r\n"
    assert results[RECORD_TYPE_ELR].getvalue() == "elrcol\r\nelrrec\r\n"
    assert results[RECORD_TYPE_ECR].getvalue() == "ecrcol\r\necrrec\r\n"
