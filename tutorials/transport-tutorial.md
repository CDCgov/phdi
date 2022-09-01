# Tutorials: The Transport Module

This guide serves as a tutorial overview of the functionality available in both `phdi.transport` and `phdi.fhir.transport`. It will cover concepts such as basic http requests, requests to the core [FHIR API](https://hl7.org/fhir/http.html), and requests related to [FHIR Bulk Data Export](http://hl7.org/fhir/uv/bulkdata/export/index.html).

## Module Overview
The transport module functions handle communication and interaction with external components. The PHDI base transport module `phdi.transport` includes connectivity with HTTP servers, and the FHIR transport module `phdi.fhir.transport` contains functions to support FHIR server interactions including saving and retrieving data as well as performing bulk export requests.

## HTTP Requests
The `phdi.transport` module contains a useful wrapper function that can be used to make basic HTTP requests. It provides a simple way to execute HTTP `GET` and `POST` requests that are protected by retry logic, and allows the user to specify their own request headers and data content. 

The return value is a requests.Response() object 


```python
from phdi.transport import http_request_with_retry

url = "https://some_api_url/service"

response = http_request_with_retry(url, retry_count=3, request_type="GET", allowed_methods=["GET"], headers={"Authorization": "Bearer some-token"})

print(f"The response received is: {response.content}")
```

## FHIR Requests
The `phdi.fhir.transport` module contains functions that can be used to make calls into the FHIR API. 

### Request with Automatic Reauthentication
At its core is the `http_request_with_reauth` function, which seamlessly handles reauthorization when an _access\_token_, used to authenticate against the FHIR server, expires. This function can be used directly in much the same way as `http_request_with_retry`, but also accepts an instance of a `BaseCredentialManager` described in more detail in the [Cloud Tutorial](cloud-tutorial.md).

The `http_request_with_reauth` function serves as the foundation for convenience methods described in the following sections, but is also available for general purpose use.

### FHIR GET Requests
There is a special helper method for running FHIR HTTP GET requests, to search ([_search_](https://hl7.org/fhir/http.html#search)) and retrieve ([_read_](https://hl7.org/fhir/http.html#read), [_vread_](https://hl7.org/fhir/http.html#vread)) data in the FHIR server.

```python
from phdi.fhir.transport

url = "https://some_fhir_url"
cred_manager = AzureCredentialManager(url)

response = fhir_server_get(url, cred_manager=cred_manager)

print(f"The response received is: {response.json()}")
```


### FHIR Bundle Uploads
When converting source data from HL7, CCDA or some other format to FHIR using the [conversion module](conversion-tutorial.md), the resulting FHIR resources are wrapped
in a bundle that can be directly submitted to the FHIR server using the `upload_bundle_to_fhir_server` function.

```python
from phdi.fhir.transport

data = {
    "resourceType": "Bundle",
    "type": "batch",
    "entry": [
        {
            "resource": {
                "resourceType": "Patient",
                "id": "some-id"
            },
            "request": {
                "method": "PUT",
                "url": "Patient/some-id"
            }
        }
    ]
}
    
cred_manager = AzureCredentialManager(url)
url = "https://some_fhir_url"

response = upload_bundle_to_fhir_server(data, cred_manager=cred_manager, fhir_url=url)

print(f"The response received is: {response.json()}")
```

### FHIR Bulk Exports
For exporting a large amount of FHIR data, [FHIR's bulk export](http://hl7.org/fhir/uv/bulkdata/export/index.html) specification provides an efficient way to excute long-running export jobs.  A few functions are available to support FHIR bulk exports, described below.

First off, you can synchronously execute a full FHIR export using the `phdi.fhir.transport` module. An example script appears below.

```python
from phdi.fhir.transport import export_from_fhir_server

url = "https://some_fhir_url"
cred_manager = AzureCredentialManager(url)

export_response = export_from_fhir_server(cred_manager, url, export_scope="Patient", since="2022-01-01T00:00:00Z", resource_type="Patient,Observation")

print(f"Export response: {export_response.json()}")
```

The response is, again, a `Response` object as defined by the `requests` package. The response content should match expected response content outlined in the FHIR bulk export specification linked above.
 