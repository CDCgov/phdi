# Tutorials: The Tabulation Module

This guide serves as a tutorial overview of the functionality available in both `phdi.tabulation` and `phdi.fhir.tabulation`. It will cover concepts such as tabulation schemas, FHIR data extraction, and writing tabular data.

## Module Overview
A single data platform cannot hope to be all things for all people. Simply put, there are fundamental tradeoffs when choosing any data platform, and it may sometimes be necessary to move data from one platform to another in order to accomplish a task more efficiently. The PHDI tabulation modules seek to address this problem by defining a data export schema and tools that can map data from one datastore into a tabular format. The tabularized data can then be analyzed using a variety of query and data analysis tools.

## Extracting Data to a Table
Extracting data from a central datastore to a table can be done in just a few steps. Currently, the central datastore used for extraction is expected to be a FHIR server, and uses FHIR searches to get data to extract. 

### FHIR Data Tabulation Schemas
Data schemas are built around the FHIR specifiction, and The first step to extract data to a tabular format is to define a schema. Schemas are defined as YAML files, with the following structure. The sameple structure below is annotated, and each annotation header is described in more detail below.

```yaml
# Dataset Name
dataset_1:
  # Table Name
  Patient:
    # Field Name
    Patient ID:
      # FHIRPath, relative to resource type
      fhir_path: Patient.id
      # Selection criteria
      selection_criteria: first
      # New field name
      new_name: patient_id
    # ... There may be multiple fields per resource type
  # ... There may be multiple resources per dataset
# ... There may be multiple datasets

```

**Dataset Name**: Schema files may define multiple datasets to be extracted. Each dataset is a collection of one or more tables. The *dataset name* identifies a dataset and may be used when writing output.

**Table Name**: This defines a table to be extracted within the dataset. The table name must be unique in the context of a dataset. *Currently, this must always name a FHIR resource type, and is used as the basis for a FHIR search.*

**Field Name**: The field name introduces a field to be extracted within a table. The value of *field name* must be unique in the context of a table, but is not used in the data output.

* **fhir_path**: This defines where the field is located within source FHIR data.  The value for this follows the [FHIRPath](http://hl7.org/fhir/fhirpath.html) standard. In addition to direct field paths, this may include more complex FHIRPath expressions such as filters and projects to allow more flexibility in field selection.
* **selection_criteria**: This defines which value to select for the field contents when the response may have more than one element.  The options are:
  * **first**: Choose the first element in the FHIRPath response.
  * **last**: Choose the last element in the FHIRPath response.
  * **random**: Choose a random element in the FHIRPath response.
* **new_name**: This defines the name of the field in the target table.

### FHIR Extraction using a Tabulation Schema
Once you have a schema defining the target format for your table, you are ready to extract data from the FHIR server. Fortunately, the schema definition will do most of the work. The schema is used both to perform the appropriate searches against the FHIR server, and define the target tabular format where the returned data will be written.

The following code may be used to extract FHIR data to a tablular format:

```python
from pathlib import Path
from phdi.cloud.azure import AzureCredentialManager

schema_path = "example_schema.yaml"  # Path to a schema config file.
base_output_path = "."                    # Path to directory where tables will be written
output_format = "parquet"            # File format of tables (currently supports parquet or csv)
fhir_url = "https://your_fhir_url"           # The URL for a FHIR server
cred_manager = AzureCredentialManager(fhir_url)

generate_all_tables_in_schema(Path(schema_path), Path(base_output_path),output_format, fhir_url, cred_manager)
```

The command above may take a while to complete as it needs to compile all of the data you requested and write it to files at the specified `base_output_path`.  The resulting folder structure will look like this:

```
+ base_output_path: root path
 \
  + dataset_1: A dataset folder is created for each dataset defined in the schema. 
  | \
  |  + Patient.parquet: The fields listed in the input schema will define the columns in this tabular file.
  |  | 
  |  + ... Additional tables in this dataset produce more files in this directory ...
  |
  + ... Additional datasets in the schema produce more dataset subdirectories ...

```


