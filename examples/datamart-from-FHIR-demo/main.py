from pathlib import Path
from phdi_building_blocks.schemas import (
    make_schema_tables,
    load_schema,
    print_schema_summary,
)

# Set required parameters
schema_path = "example_schema.yaml"  # Path to a schema config file.
output_path = "example_schema"  # Path to directory where files will be written
output_format = "parquet"  # File format of tables
fhir_url = "your_fhir_url"  # The URL for a FHIR server
access_token = "your_access_token"  # Access token for authentication with FHIR server.

# Make Schema
schema_path = Path(schema_path)
output_path = Path(output_path)
make_schema_tables(schema_path, output_path, output_format, fhir_url, access_token)

# Display Schema Summary
schema = load_schema(schema_path)
print_schema_summary(output_path, display_head=True)
