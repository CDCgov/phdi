# This file converts a parquet file of patient data into tuples. Each row of patient
# data is returned a tuple of (iris_id, fhir_bundle)

from phdi.linkage.seed import convert_to_patient_fhir_resources
import pyarrow.parquet as pq
import pyarrow as pa


def convert(bytes):
    buffer = pa.BufferReader(bytes)
    parquet_file = pq.ParquetFile(buffer)
    converted_data = {}
    for row in parquet_file.iter_batches(batch_size=1):
        data = row.to_pylist()[0]
        iris_id, fhir_bundle = convert_to_patient_fhir_resources(data)
        converted_data[iris_id] = fhir_bundle

    return converted_data


# Uncomment for Synapse script
# def read_file(file_path):
#     file_client = DataLakeFileClient(
#         account_url=f"https://{account_name}.dfs.core.windows.net",
#         file_system_name=file_system_name,
#         file_path=file_path,
#         credential=credential,
#     )
#     download = file_client.download_file()
#     bytes = download.readall()
#     return bytes


# bytes_data = read_file(file_path)
# converted_data = convert(bytes_data)
