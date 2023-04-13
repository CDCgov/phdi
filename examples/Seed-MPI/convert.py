# This file converts a parquet file of patient data into tuples. Each row of patient
# data is returned a tuple of (iris_id, patient_resource)
import sys
from phdi.linkage.seed import convert_to_patient_fhir_resources
import pyarrow.parquet as pq


def convert():
    file_path = sys.argv[1]
    parquet_file = pq.ParquetFile(file_path)
    for row in parquet_file.iter_batches(batch_size=1):
        data = row.to_pylist()[0]
        iris_id, patient_resource = convert_to_patient_fhir_resources(data)


if __name__ == "__main__":
    convert()
