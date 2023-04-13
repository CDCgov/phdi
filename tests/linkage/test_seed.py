from phdi.linkage.seed import convert_to_patient_fhir_resources
import pathlib
import pyarrow.parquet as pq


mpi_test_file_path = (
    pathlib.Path(__file__).parent.parent.parent
    / "tests"
    / "assets"
    / "synthetic_patient_mpi_seed_data.gzip"
)


def test_convert_to_patient_fhir_resources():
    parquet_file = pq.ParquetFile(mpi_test_file_path)
    for row in parquet_file.iter_batches(batch_size=1):
        data = row.to_pylist()[0]
        (iris_id, returned_fhir_resource) = convert_to_patient_fhir_resources(data)
        assert type(returned_fhir_resource) == dict
        assert returned_fhir_resource["resourceType"] == "Patient"
        assert returned_fhir_resource["id"] != ""
        assert iris_id == data["iris_id"]
