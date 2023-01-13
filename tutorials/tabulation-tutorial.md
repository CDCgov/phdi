# Tutorials: The Tabulation Module

This guide serves as a tutorial overview of the functionality available in both `phdi.tabulation` and `phdi.fhir.tabulation`. It will cover concepts such as schemas, FHIR data extraction, and writing tabular data.

## Module Overview
A single data platform cannot hope to be all things for all people. Simply put, there are fundamental tradeoffs when choosing any data platform, and it is sometimes helpful to move data from one platform to another in order to accomplish a task more efficiently. The PHDI tabulation modules (consisting of `phdi/tabulation` and `phdi/fhir/tabulation`) seek to address this problem by defining a process by which a customizable, user-defined schema can be used to map data from one datastore into a tabular format. This tabulated data can then be analyzed using a variety of query and data analysis tools.

## Working with Schemas
Data schemas are designed around the FHIR data format, and the first step to extract data to a tabular format is to define a schema. Schemas may be defined as YAML files or as JSON files. Below, we've created a typical example to outline the required structure of a supplied schema. We've described the structure of this schema in more detail below the example.

```yaml
metadata:
  # Parameters that specify metadata applying to all tables in the schema
  results_per_page: 1000
  schema_name: "Schema Name" # Required
tables:
  Patient Information:  # All tables must have a name
    # Properties specific to this table
    resource_type: Patient  # Required
    earliest_updated_datetime: "2020-01-01T00:00:00"
    columns:    # Required for all tables; min info is fhir_path
      Patient ID:
        fhir_path: Patient.id
        invalid_values:
          - null
          - ""
        selection_criteria: first
      First Name:
        fhir_path: Patient.name.given
        invalid_values:
          - null
          - ""
          - "Unknown"
        selection_criteria: first
      Last Name:
        fhir_path: Patient.name.family
        selection_criteria: first
      Phone Number:
        fhir_path: Patient.telecom.where(system = 'phone').value
        selection_criteria: first
  BMI Values:
    resource_type: Observation
    query_params:
      # Parameters used for filtering when querying the FHIR server
      category: http://hl7.org/fhir/ValueSet/observation-category|exam
    columns:
      Base Observation ID:
        fhir_path: Observation.id
        selection_criteria: first
      BMI:
        fhir_path: Observation.value.valueInteger
        selection_criteria: first
      Patient Height:
        fhir_path: Observation.value.valueInteger
        selection_criteria: first
        reference_location: "forward:Observation:hasMember" # Indicates a reference resource
      Patient Weight:
        fhir_path: Observation.value.valueInteger
        selection_criteria: first
        reference_location: "forward:Observation:derivedFrom"
```

**Metadata**: A schema file begins by specifying any metadata that relates to all tables in the schema (since a schema can specify more than one table). The most relevant parameters of this group are `schema_name` and `results_per_page`. `schema_name` is a required parameter and specific to the schema not table(s) within a schema. `results_per_page` specifies how many results the FHIR server should return at a time when using an incremental, paginated search approach (so as to not make memory costs prohibitively high). If this parameter is omitted, the default value of 1000 is used when paginating results.

**Tables**: The next section in the schema file is the `Tables` field, which specifies how many tables the schema holds as well as the properties of those tables. A single schema file can hold as many tables as a user desires, but importantly, even if a schema defines only a single table, the `Tables` field must still exist (it will just have one member element).

**Table Name**: The *table name* defines a table the user wishes to extract data to. The name of the table _must_ be unique within the schema file.

**Table Properties**: Each table in the schema must define one or more properties relating to the table. These properties range from metadata about this specific table to query parameters used to guide the FHIR search results. While the bullets below explain the details of some of the optional parameters that can be used, _all_ tables must define the required property `resource_type`. This field--which **must** match a FHIR resource such as Patient or Observation--defines the **anchor** type of the given table.

An anchor type has two functions:

1) specify which resource type will generate rows in the table (for example, in a table about Patients, we would wish to have one row per patient returned from the FHIR server; in a table about physical exam observations, we would want a table where each observation of a particular category generated one row in the table); importantly, not every resource of this type _has_ to create a row in the table (in the case of resources like Observation which may have fields [`has_member` and `derived_from`] that point to other, non-related resources of the same type), but _no other_ types of resources besides the anchor can generate a row;

2) specify relative paths used when referencing other resource types (see "On Reference Resources" below for more details).

A couple other property fields of interest are:

* `earliest_updated_datetime`: A field used by the FHIR server to filter returned results by a given time window. If the value `2020-01-01T00:00:00` is supplied, for example, the returned results will consist only of resources created or updated on or after January 1 of 2020.
* `query_params`: A field holding metadata values that that filter the resources we'd like to receive based upon specific criteria for elements within that resource. In our example, we want only Observation resources that have a `category` element value of `exam` (rather than, say `laboratory`).

Once metadata is specified, the properties for a given table must also include the `columns` field, which describes the columns to-be-created in the output table using another set of keys and values. Within the `columns` dictionary, a table must have one or more **field names**.

**Field Name**: A *field name* defines a column of values that will exist in the table (such as as Patient First Name or Vaccine Administration Date). The value of *field name* must be unique in the context of a table, since it will serve as a column header in the output. The following properties determine how data will be extracted for this field.
* **fhir_path**: The *fhir_path* defines where to find data for this field within the source FHIR data, i.e. it is the "dot notation" path that must be followed to find the requested data value in a given FHIR resource. It should be a [FHIRPath](http://hl7.org/fhir/fhirpath.html) expression. In addition to direct field path locations, this may include more complex FHIRPath expressions such as filters (see the `Phone Number` example) to allow more flexibility in field selection.
* **invalid_values**: A list specifying the values that are considered to be invalid for purposes of extracting and tabulating this field. A tabulated row containing one or more invalid values (which are determined per-column) is removed from the data prior to writing to output. Each invalid value should occur on its own bulleted line as shown above. Invalid values may include all data types as well as `null` (for `None`/`null` values) and "" for empty values.
* **selection_criteria**: This defines the value to select field contents, and primarily applies when response data may have more than one element. However, even single-response fields must popoulate a value here. The options are:
  * **first**: Choose the first element in the FHIRPath response.
  * **last**: Choose the last element in the FHIRPath response.
  * **random**: Choose a random element in the FHIRPath response.
  * **all**: Use all of the elements in the FHIRPath response, if the value is a list (such as if multiple racial/ethnic identities are specified).
* **reference_location**: For resources which reference/are referenced by an anchor type, the path that shows how the two resources are connected. See "On Reference Resources" below for more details about this optional property.

### On Reference Resources
For many types of queries and data tables, the data needed to extract a value will be contained directly within the anchor resource type. These kinds of queries are simple to compose and simple to tabulate, since the value can be pulled directly from the result resource. However, in other cases, the logic of where to find an appropriate value is more complicated, especially if the value is contained not in an anchor resource, but in a _reference resource_. There are two kinds of reference resources:

* **forward references** are resources that an anchor resource points to using information contained in the anchor resource. For example, Patient resources have the FHIR field `generalPractitioner`, which holds a reference to a Practitioner resource.
* **reverse references** are resources that point to an anchor resource using information contained in the reference, rather than the anchor. For example, many patients have an annual physical exam administered by their general practitioner to evaluate the state of their health. Information about these physical exams, however, is not found on the Patient resource itself. Rather, there are Observation resources whose category is `exam` that will contain a field `subject`, which is a reference to a Patient resource. Because of the backwards-pointing nature of this relationship, reverse references can have a many-to-one relationship with the anchor resource they reference.

The `reference_location` field in the schema, if present for a particular column, indicates that the value requested for this column must be found using reference resources of one kind or the other. **All** `reference_location` values must begin with either `forward` or `reverse` to indicate the directionality of the relationship, and rather than using dot-notation as in the FHIR path, colons are instead used to separate the parts of the reference path. For example, to access the reference to a patient's General Practitioner using a FHIR path, we would write `Patient.generalPractitioner`. To specify that we want to _reference_ the element at this location, we would write `forward:Patient:generalPractitioner`.

The presence of both a `fhir_path` field and `reference_location` field may seem confusing at first, but the following guideline is helpful to differentiate them: `reference_location`s indicate which resource to use for value extraction (by means of indicating how to find such a resource), and `fhir_paths` indicate how to access the desired value (FHIR element) from the resource to-use, once it's found.

### Loading a Schema from a File
The `load_schema` function loads a schema from a file into an internal format. Several functions outlined elsewhere in the documentation expect the schema (or part of the schema) to be in this format.  This format consists of a `dict` that mirrors the file format described above.

```python
from pathlib import Path
from phdi.tabulation import load_schema

schema = load_schema(Path("example_schema.yaml"))
```

## Extracting Data to a Table
The process of collecting, extracting, and tabulating results follows the steps below:
1. Build queries for the FHIR server. Based on the given schema, a number of "search URLs" are constructed that match the specification of a FHIR server search API. This construction is automatic, requiring only a properly formatted schema to be supplied by the user. The search URLs include information on the desired resources, as well as any filters to be applied to returned data.
2. Query the FHIR server using the API. The constructed queries are sent to the FHIR server, which processes each query sequentially using pagination. Results are returned to the program, which collects all information across pages of search results into a data structure.
3. Tabulate the result data. The responses from the FHIR server are fed into a two-part tabulation algorithm that applies the user's schema to the data while also creating appropriate reference mappings between related resources (see "On Resource References" above for more detail). This procedure creates, for each table in the schema, a list of lists denoting the rows and columns of the data, with appropriate values for each column extracted from the resource results found by the FHIR server.
4. Write the results. Each table is finally output to a user-specified destination in one of several supported file formats.

### Generating Query Strings and Search URLs
Once you have created a schema file defining the target format for your table, the first step in extracting data from the FHIR server is the creation of search URLs which will be used to query the server. When working with available functionality at the building block level, this part of the tabulation process is automatic and operates using only the schema during the call to `extract_data_from_schema`. However, in some cases, it might be desirable to manually generate search URLs, such as during an interactive query session.

The code below outlines how this can be done, using the schema defined at the top of this tutorial as an example:

```python
from pathlib import Path
from phdi.tabulation import load_schema
from phdi.fhir.tabulation import _generate_search_urls

schema = load_schema(Path("example_schema.yaml"))
search_urls = _generate_search_urls(schema)
print(search_urls)
>>> dict({
    "Patient Information": "Patient&_count=1000&_since=2020-01-01T00:00:00",
    "BMI Values": "Patient&_count=1000&_since=2020-01-01T00:00:00&_include=Observation:hasMember&_include=Observation:derivedFrom"
})
```

The result is given back as one search URL per table in the schema, containing all of the search criteria required by a user in the schema. 

### Extracting Data from the FHIR Server
Once the search URLs are built, we can make an API call to the FHIR Server with them to extract our desired data. It is theoretically possible to treat any persistent data store as the source from which to extract, but the PHDI library treats a FHIR server as the centralized data repository. This process, too, is relatively schema-driven and can run largely outside manual interaction from a user.

```python
from pathlib import Path
from phdi.tabulation import load_schema
from phdi.fhir.tabulation import extract_data_from_schema
from phdi.cloud.azure import AzureCredentialManager

schema = load_schema(Path("example_schema.yaml"))
fhir_url = "https://your_fhir_url"
cred_manager = AzureCredentialManager(fhir_url)

results = extract_data_from_schema(schema, fhir_url, cred_manager)
print(results)
>>> dict({
    "Patients": [
        {
            "fullURL": "some-url-1",
            "resource": {...some-fhir-resource-1...}
        },
        {
            "fullURL": "some-url-2",
            "resource": {...some-fhir-resource-2...}
        },
        ...
    ],
    "BMI Values": [
        {
            "fullURL": "some-url-9",
            "resource": {...some-fhir-resource-9...}
        },
        {
            "fullURL": "some-url-27",
            "resource": {...some-fhir-resource-27...}
        },
        ...
    ]
})
```

Here, the results contain a dictionary mapping the name of each table in the schema to a list of bundle entries (not resources!) pulled from the results of the FHIR server. Results are returned as bundle entries rather than resources due to the way the incremental FHIR search that operates inside the `extract_data_from_schema` function combines results across pages of data.

While the above example shows how to make API calls for all search URLs and all tables, in some cases (again, such as an interactive session) we may only wish to make a query for a single table. This is possible by leveraging the functions that are called in a loop within `extract_data_from_schema`:

```python
from pathlib import Path
from phdi.tabulation import load_schema
from phdi.fhir.tabulation import _generate_search_urls, extract_data_from_fhir_search
from phdi.cloud.azure import AzureCredentialManager

schema = load_schema(Path("example_schema.yaml"))
fhir_url = "https://your_fhir_url"
cred_manager = AzureCredentialManager(fhir_url)

search_urls = _generate_search_urls(schema)
query_of_interest = search_urls["Patients"]
results = extract_data_from_fhir_search(query_of_interest, cred_manager)
```

### Tabulating Results
Once results are extracted from the FHIR server, we need to put them into an organized, ordered arrangement for downstream processing. This is where the tabulation algorithm comes in. Tabulation seeks to transform the list of bundle entries and result resources into a list of lists denoting desired values in a columnar format. Importantly, while search URL generaiton and data extraction can be run against all tables in the schema with a single function, the tabulation procedure must be executed _per table_. Furthermore, unlike in the previous two cases, where a user can replicate the functionality of creating search URLs or making their own API calls to the FHIR server, granular replication of this procedure is _not_ recommended due to its complexity. Invoking the function is simple, but the underlying mechanics of connecting resources to their references and extracting the desired values is not. Interested readers should consult the documentation in the code proper.

The example below shows a simple invocation of tabulation:

```python
from pathlib import Path
from phdi.tabulation import load_schema
from phdi.fhir.tabulation import tabulate_data
from phdi.cloud.azure import AzureCredentialManager

schema = load_schema(Path("example_schema.yaml"))
fhir_url = "https://your_fhir_url"
cred_manager = AzureCredentialManager(fhir_url)

results = extract_data_from_schema(schema, fhir_url, cred_manager)

tabulated_results = {}
for table_name, data in results.items():
    tabulated_results[table_name] = tabulate_data(data, schema, table_name)
print(tabulated_results)
>>> dict({
    "Patients": [
        ["Patient ID", "First Name", "Last Name", "Phone Number"],
        ["id-1", "John", "Doe", None],
        [...]
    ],
    "BMI Values": [
        ["Base Observation ID", "BMI", "Patient Height", "Patient Weight"],
        ["obs-1", 34.8, 66, 197],
        [...]
    ]
})
```

For each set of tabulated values, the first entry is a list of the headers of the columns in the table (taken directly from the supplied schema). Each subsequent element in the list of lists denotes one row of the table.

### Writing Tabular Data
Data that has been tabulated is now ready for writing to its output destination. This is the final step of the extraction and tabulation process. The building blocks currently support writing to three destination types: CSV files, Parquet files, and writing the data to a SQLite database file. All of these can be accessed using the same function with appropriate parameter settings:

```python
from pathlib import Path
from phdi.tabulation import load_schema, write_data
from phdi.fhir.tabulation import tabulate_data
from phdi.cloud.azure import AzureCredentialManager

schema = load_schema(Path("example_schema.yaml"))
fhir_url = "https://your_fhir_url"
cred_manager = AzureCredentialManager(fhir_url)

results = extract_data_from_schema(schema, fhir_url, cred_manager)
table_of_interest = "Patients"
tabulated_results = tabulate_data(results[table_of_interest], schema, table_of_interest)

# Write the file as a CSV
output_type = "csv"
output_dir = "/"
filename = "my_csv.csv"
write_data(tabulated_results, output_dir, output_type, filename)

# Write as a SQLite DB connection
output_type = "sql"
output_dir = "/"
db_file = "my_db.db"
db_tablename = "patients"
write_data(tabulated_results, output_dir, output_type, db_file=db_file, db_tablename=db_tablename)
```

### Performing Extract and Tabulate In One Function
While it is possible to perform the component steps of collection, extraction, tabulation, and writing individually, for convenience and a streamlined approach, we have provided a building block to carry out the procedure for all tables in a given schema with minimal input from a user. The wrapper function handles all of the component steps and automatically passes the inputs and outputs to the appropriate calls.

```python
from pathlib import Path
from phdi.fhir.tabulation import generate_tables
from phdi.cloud.azure import AzureCredentialManager

fhir_url = "https://your_fhir_url"
cred_manager = AzureCredentialManager(fhir_url)

schema_path = Path("example_schema.yaml")
output_params = {
    "Patients": {
        "output_type": "csv",
        "directory": "/",
        "filename": "example.csv"
    },
    "BMI Values": {
        "output_type": "parquet",
        "directory": "/",
        "filename": "example.parquet"
    }
}

generate_tables(schema_path, output_params, fhir_url, cred_manager)
```

For each table specified in the schema, the corresponding set of write parameters will be used to determine the write mechanism employed. When the process executes and completes, the requested data will be available in the requested form at the specified directory location.