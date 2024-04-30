import pathlib

import pyarrow.parquet as pq

from phdi.linkage.seed import adjust_birthdate
from phdi.linkage.seed import convert_to_patient_fhir_resources
from phdi.linkage.seed import extract_given_name

mpi_test_file_path = (
    pathlib.Path(__file__).parent.parent.parent
    / "tests"
    / "assets"
    / "linkage"
    / "synthetic_patient_mpi_seed_data.parquet"
)


def test_convert_to_patient_fhir_resources():
    parquet_file = pq.ParquetFile(mpi_test_file_path)
    for row in parquet_file.iter_batches(batch_size=1):
        data = row.to_pylist()[0]
        (iris_id, returned_fhir_bundle) = convert_to_patient_fhir_resources(data)
        assert isinstance(returned_fhir_bundle, dict)
        assert returned_fhir_bundle["resourceType"] == "Bundle"
        assert returned_fhir_bundle["entry"][0]["resource"]["resourceType"] == "Patient"
        assert returned_fhir_bundle["id"] != ""
        assert iris_id == data["person_id"]
        assert isinstance(returned_fhir_bundle["entry"][0]["resource"]["name"], list)
        assert (
            "urn:uuid:" + returned_fhir_bundle["entry"][0]["resource"]["id"]
            == returned_fhir_bundle["entry"][0]["fullUrl"]
        )
        assert (
            "@" in returned_fhir_bundle["entry"][0]["resource"]["telecom"][2]["value"]
        )


def test_adjust_birthdate():
    # test failure
    data = {"birthdate": None}
    new_birthdate = adjust_birthdate(data)
    assert new_birthdate is None

    # test adjustment
    data = {"birthdate": "26JUL1976:00:00:00.000"}
    new_birthdate = adjust_birthdate(data)
    assert new_birthdate == "1976-07-26"

    # test correctly formatted dates are not adjusted
    data = {"birthdate": "1976-07-26"}
    new_birthdate = adjust_birthdate(data)
    assert new_birthdate == "1976-07-26"


def test_extract_given_name():
    # test all non-null values are included
    data = {"first_name": "John", "middle_name": "Jacob Jingleheimer"}
    given_name = extract_given_name(data)
    assert given_name == ["John", "Jacob", "Jingleheimer"]

    # test null values are excluded
    data = {"first_name": "John", "middle_name": None}
    given_name = extract_given_name(data)
    assert given_name == ["John"]

    # test full null values return null
    data = {"first_name": None, "middle_name": None}
    given_name = extract_given_name(data)
    assert given_name is None
