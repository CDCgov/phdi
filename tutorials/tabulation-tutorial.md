# Tutorials: The Tabulation Module

This guide serves as a tutorial overview of the functionality available in both `phdi.tabulation` and `phdi.fhir.tabulation`. It will cover concepts such as schemas, FHIR data extraction, and writing tabular data.

## Module Overview
A single data platform cannot hope to be all things for all people. Simply put, there are fundamental tradeoffs when choosing any data platform, and it is sometimes helpful to move data from one platform to another in order to accomplish a task more efficiently. The PHDI tabulation modules seek to address this problem by defining a data export schema and tools that can map data from one datastore into a tabular format. The tabularized data can then be analyzed using a variety of query and data analysis tools.

## Working with Schemas
Data schemas are designed around the FHIR data format, and the first step to extract data to a tabular format is to define a schema. Schemas are defined as YAML files, with the following annotated structure. The annotations are described in more detail below the schema example.

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

**Dataset Name**: Schema files may define one or more datasets to be extracted. Each dataset is a collection of one or more tables. The *dataset name* identifies a dataset and may be used in a directory structure to organize written output.

**Table Name**: The *table name* defines a table to be extracted within the dataset. The table name must be unique in the context of a dataset. *Currently, this must always match a FHIR resource type because it is used as the basis for a FHIR search.*

**Field Name**: The *field name* introduces a field to be extracted within a table. The value of *field name* must be unique in the context of a table, but is not written in the output data. The following properties determine how data will be bextracted for this field.
* **fhir_path**: The *fhir_path* defines where to find data for this field within the source FHIR data. It should be a [FHIRPath](http://hl7.org/fhir/fhirpath.html) expression. In addition to direct field path locations, this may include more complex FHIRPath expressions such as filters and projects to allow more flexibility in field selection.
* **selection_criteria**: This defines the value to select field contents, and primarily applies when response data may have more than one element. However, even single-response fields must popoulate a value here. The options are:
  * **first**: Choose the first element in the FHIRPath response.
  * **last**: Choose the last element in the FHIRPath response.
  * **random**: Choose a random element in the FHIRPath response.
* **new_name**: This defines the name of the field in the target table.

### Loading a Schema from a File
The `load_schema` function loads a schema from a file into an internal format. Several functions outlined elsewhere in the documentation expect the schema (or part of the schema) to be in this format.  This format consists of a `dict` that mirrors the file format described above.

```python
from pathlib import Path
from phdi.tabulation import load_schema

schema = load_schema(Path("example_schema.yaml"))
```

## Extracting Data to a Table
Extracting data from a central datastore to a table can be done in just a few steps. Currently, the central datastore used for extraction is expected to be a FHIR server, and uses FHIR searches to get data to extract. 

### FHIR Extraction Using a Schema
Once you have created a schema file defining the target format for your table, you can extract data from the FHIR server. Fortunately, the schema definition will do most of the work. The schema is used both to perform searches against the FHIR server, and define the target tabular format where the returned data will be written.

The following code may be used to extract FHIR data to a tablular format:

```python
from pathlib import Path
from phdi.cloud.azure import AzureCredentialManager

schema_path = Path("example_schema.yaml")  # Path to a schema config file.
base_output_path = Path(".")               # Path to directory where tables will be written
output_format = "parquet"                  # File format of tables (currently supports parquet or csv)
fhir_url = "https://your_fhir_url"         # The URL for a FHIR server
cred_manager = AzureCredentialManager(fhir_url)

generate_all_tables_in_schema(schema_path, base_output_path,output_format, fhir_url, cred_manager)
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

### Extracting FHIR Data for a Single Table
The extraction function `generate_all_tables_in_schema` described above will process all data according to a schema file. It leverages a more granular function `generate_table` to generate a single dataset of tabular data. It may be useful to use this more granular function rather than generating tables for all datasets listed in the schema.

```python
from pathlib import Path
from phdi.cloud.azure import AzureCredentialManager

schema_path = Path("example_schema.yaml")  # Path to a schema config file.
base_output_path = Path(".")               # Path to directory where tables will be written
output_format = "parquet"                  # File format of tables (currently supports parquet or csv)
fhir_url = "https://your_fhir_url"         # The URL for a FHIR server
cred_manager = AzureCredentialManager(fhir_url)

schema = load_schema(Path("example_schema.yaml"))

generate_table(schema.get("dataset-1"), base_output_path, output_format, fhir_url, cred_manager)
```


### Tabulation for an Individual FHIR Resource
Digging into yet another layer of granularity, it may be useful to tabularize a single row of data, given a single FHIR resource, and a dataset schema. This is possible by using the `apply_schema_to_resource` function.  The following example demonstrates how a FHIR resource might be transformed into a tabular form.

It's important to note here that `apply_schema_to_resource` does not write to an output file like `generate_all_tables_in_schema` and `generate_table`. Instead it returns a `dict` that will be described in more detail below.

```python
from phdi.fhir.tabulation import apply_schema_to_resource

patient_schema = { "Patient": {
    "Patient ID": {
      "fhir_path": "Patient.id",
      "selection_criteria": "first",
      "new_name": "patient_id"
    },
    "First Name": {
      "fhir_path": "Patient.name.given",
      "selection_criteria": "first",
      "new_name": "first_name"
    },
    "Last Name": {
      "fhir_path": "Patient.name.family",
      "selection_criteria": "first",
      "new_name": "last_name"
    }
  }
}

resource = {
  "resourceType": "Patient",
  "id": "patient-id",
  "name": {
    "given": ["Ashlee", "Ann"],
    "family": "Smith"
  }
}

apply_schema_to_resource(resource, patient_schema)
```

## Working with Tabular Data
Some of the functions described in the previous section (`generate_all_tables_in_schema`, `generate_table`) will write tabular data to a file after generating it. However, `apply_schema_to_resource` formats returns tabular data as a `dict` without persisting it. Luckily, there are functions to work with tabular data, allowing for both writing and summarizing tabular file formats.

### Writing Tabular Data
Internally, tabular data is represented as a `dict` where each key is a column name, and each value is a data value for that column. These `dict`s can be compiled into a `list` to represent multiple rows of data. The `write_table` function will write a `list` of `dict`s to a file.

```python
from pathlib import Path
from phdi.tabulation import write_table

data = [{'patient_id': 'id1', 'first_name': 'Ashlee', 'last_name': 'Smith'},
{'patient_id': 'id2', 'first_name': 'Bert', 'last_name': 'Smith'}
]
output_file_name = Path("output/my-parquet-file.parquet") # Path to directory where tables will be written

parquet_file = write_table(data, Path(output_file_name), "parquet")
parquet_file.close() # When working with Parquet files, the function returns a file writer that can be used multiple times.  This must be closed when writing is complete.
```

### Getting Information from Written Data
You can also see information about the schemas stored in an output directory after the data is written.

```python
from phdi.tabulation import print_schema_summary

print_schema_summary("output")
```