# Tutorials: The Cloud Module
This guide serves as a tutorial overview of the functionality available in both `phdi.cloud` and `phdi.fhir.cloud` packages. It covers concepts such as credential managers, cloud storage, and FHIR export file downloads.

## The Basics: Cloud Managers and Clients
The goal of the `phdi.cloud` and `phdi.fhir.cloud` modules is to provide a cloud platform-agnostic way to interact with common cloud services that have similar, but differing implementations across cloud providers. Doing so provides a way for users of other building blocks who need to leverage general cloud functionality to do so in a cloud platform-agnostic way. 

For example, the `phdi.fhir.transport` module requires an authorized user/service to make requests to the FHIR API. Authentication may happen different ways on different platforms, but since the related FHIR transport functions make use of a common credential management interface, the functions can support connections with Azure credentials, GCP credentials, etc.

### Credential Managers
The generic (cloud-agnostic) class representing a credential manager is specified by the `BaseCredentialManager` class. It provides the following methods:
```
BaseCredentialManager:
    get_access_token()
        '''
        Returns an access token using the managed credentials
        '''
    
    get_credential_object()
        '''
        Returns a cloud-specific credential object
        '''
```

### Cloud Storage
The generic class representing a connection to cloud-based object storage is specified by the `BaseCloudContainerConnection` class.
```
BaseCloudContainerConnection:
    upload_object()
        '''
        Uploads content to storage
        '''
    
    download_object()
        '''
        Downloads an object from storage
        '''

    list_containers()
        '''
        List containers for this connection.
        '''
    
    list_objects()
        '''
        List objects within a container.
        '''
```

## FHIR Export Download
Azure FHIR server places files full of FHIR resources in blob storage during [FHIR bulk data exports](http://hl7.org/fhir/uv/bulkdata/export/index.html). To make it easier to download these files, you can directly use the completed export job's status. FHIR export and related poll responses are described more detail in the [transport tutorial](transport-tutorial.md).

```python
from phdi.fhir.transport import export_from_fhir_server
from phdi.fhir.cloud.azure import download_from_fhir_export_response

url = "https://some_fhir_url"
cred_manager = AzureCredentialManager(url)

export_response = export_from_fhir_server(cred_manager, url, export_scope="Patient", since="2022-01-01T00:00:00Z", resource_type="Patient,Observation")

file_iter = download_from_fhir_export_response(export_response, cred_manager)

# Read the beginning of each downloaded file
for resource_type, file_stream in file_iter:
    print(f"The beginning content for a {resource_type} export file is: {file_stream.read(50)}")
```

## Common Uses
Listed below are several example use cases for employing the cloud module.

### Object Uploads
In order to upload objects, you will need both a credential manager and storage connection that are specific to the cloud implementation you need to use.  However, once those objects are created, you can interact with them in the same way.

```python
from phdi.cloud.azure import AzureCredentialManager, AzureCloudConnectionManager

storage_account_url = "https://my-storage.blob.storage.azure.net"
cred_manager = AzureCredentialManager(storage_account_url)

storage_connection = AzureCloudContainerConnection(storage_account_url, cred_manager)

storage_connection.upload_object("my-container", "some/location/filename.txt", message="Hello world!")
```

### Object Downloads
Downloading from cloud storage works similarly.

```python
from phdi.cloud.azure import AzureCredentialManager, AzureCloudConnectionManager

storage_account_url = "https://my-storage.blob.storage.azure.net"
container = "my-container"
file_location = "some/location"
filename = "filename.txt"
cred_manager = AzureCredentialManager(storage_account_url)

storage_connection = AzureCloudContainerConnection(storage_account_url, cred_manager)

object_contents = storage_connection.download_object("my-container", f"{file_location}/{filename}")

print(f"Blob contents: {object_contents}")
```

### Listing contents
You can also retrieve a list of files in a storage container, or folder.

```python
from phdi.cloud.azure import AzureCredentialManager, AzureCloudConnectionManager

storage_account_url = "https://my-storage.blob.storage.azure.net"
container = "my-container"
file_location = "some/location"
cred_manager = AzureCredentialManager(storage_account_url)

storage_connection = AzureCloudContainerConnection(storage_account_url, cred_manager)

container_listing = storage_connection.list_containers()

file_listing = storage_connection.list_objects(container, prefix=file_location)

print(f"The following containers exist in {storage_account_url}: {container_listing}")

print(f"The following objects exist in {storage_account_url}, in {container}/{file_location}: {file_listing}")
```
