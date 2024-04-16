# Architecture of the Orchestration Service
This document outlines some architectural details that make up the Orchestration Service, as well as defines the acceptable input format for a workflow configuration file.

## Overview and Components
The DIBBs' Orchestration Service provides an automated, config-driven system that allows users to flexibly parameterize and combine the various DIBBs Building Blocks in a single workflow. This service works by combining abstracted functions for each service into a loop that allows the Orchestration Service to sequentially send data to different API endpoints in a standardized way, without ever needing to know specific details about the logic of each service or the data being passed.

### Workflow Configuration Files
A call to the Orchestration Service follows the blueprint plan laid out by a particular workflow configuration file. As the service is entirely config-driven, all the information that the service needs to order, combine, and parameterize each other Building Block it calls is contained in this configuration.

A config file is a JSON dictionary with exactly one key, `workflow`, whose value is a list of "configuration steps" (the single K-V pair is necessary because JSON does not guarantee dictionary key order upon read or write, and steps must be executed in the proper sequence). Each configuration step is a dictionary with the following form:

```
{
    "service": "name-of-service-this-step-represents",
    "endpoint": "specific-endpoint-to-post-to",
    "params": {
        "service-param-1": "value-1"
    }
}
```

The final key of the dictionary, `params`, is entirely optional--some services may require no additional configuration (the `fhir-converter`, for example), in which case the parameter can be wholly excluded from the dictionary. An example of a fully-written config step might look like:

```
{
    "service": "ingestion",
    "endpoint": "/fhir/harmonization/standardization/standardize_dob",
    "params": {
        "dob_format": ""
    }
}
```

The configuration file in its entirety, then, might look like this (as a simple example):

```
{
    "workflow": [
        {
            "service": "fhir_converter",
            "endpoint": "/convert-to-fhir"
        },
        {
            "service": "ingestion",
            "endpoint": "/fhir/harmonization/standardization/standardize_names"
        }
    ]
}
```

### Handlers: Per-Service Abstraction
The Orchestration Service uses a number of abstracted *handler* functions to carry out a given workflow while remaining agnostic of any particular Building Block. For each DIBBs service, we define two separate methods responsible for composing the input to a service and parsing the output of that service. These functions follow the convention of `build_service_name_request` and `unpack_service_name_response`, respectively. Further, each type of function has the same input and output signature across all services:

All request-builder methods take as input:
1. the input message that the user sent for processing (which may have been changed by the output of a previous service--for example, `standardization`),
2. the request object the user initially sent to one of the Orchestration Service's API endpoints, and
3. optionally, the dictionary of parameters specific to the service represented by the request-builder function.
Each builder method returns a single dictionary constituting the request to be sent to that specific service.

All response-unpacking methods take as input a service's HTTP `Response` and return a `ServiceHandlerResponse` Object (discussed below).

All data flowing to and from a service is manipulated by these two handler functions, including any logic to parse a service's return state (such as status code, data validity, and whether the data is fit to pass to the next service in the workflow). The standardization of these input and output signatures also allows the Orchestration Service to communicate with other Building Block APIs without ever needing specific case logic or programming to handle particular data or message types.

### ServiceHandlerResponse Objects
Each service's response-unpacking handler returns an object of type `ServiceHandlerResponse`, which is a custom data class built to contain message content and service-specific logic while maintaining a standardized structure. An instance of a `ServiceResponseHandler` has three properties:

1. `status_code`: The status code of the response the service sent back.
2. `msg_content`: The information content of the service's response. For services like `standardize_[something]`, this will be the updated FHIR bundle, but for a service like `validation` or `message_parser`, this will be a list of validation errors flagged or a dictionary of parsed values.
3. `should_continue`: A boolean flag indicating whether the data in the service's original response is fit to pass to the next Building Block in the APIs loop. Some services (e.g. `validation`) can send back a `200` code (because the service executed correctly) but still find errors in the data, indicating the next service should _not_ be called. The logic that determines whether a service's response data should continue is specific to each service's response-unpacking handler.

Having each response-unpacking handler return one of these objects allows the API loop to remain completely agnostic about data flow and updates, and instead rely on service-specific invocations to work out any details.

### API Loop
The core loop of the Orchestration Service is found in the `call_apis` function of `services.py`. This function iteratively:

* Composes a service request,
* POSTs to the service endpoint,
* Unpacks the service's response, and
* Makes any required data updates to the message being parsed.

These steps are repeated for each service specified in the workflow configuration. The abstraction techniques in the handlers and response objects above allow the `call_apis` loop to only worry about passing data to the right service, at the right URL, with the right parameters. This information is found, respectively, in the user's workflow configuration and the Orchestration Service's environment variables.

## Request Inputs and API Endpoints
Currently, the Orchestration Service can be accessed via several API endpoints, both with and without a connected websocket. Each endpoint (regardless of whether a websocket is or isn't used) performs the same broad functionality, which is executing a workflow on a given message. Valid endpoints include:

* `/process-message`: The general, typical endpoint-to-use when invoking the service. Parameters are supplied through an ordinary HTTP Request body.
* `/process`: Similar to the above, but parameters are supplied through `Form` fields, such as with the Demo UI.
* `/process-message-ws`: Analogous to the `process-message` endpoint, but with an attached websocket.
* `/process-ws`: Analogous to the `process` endpoint, but with an attached websocket.

In most cases, unless using a visual application or a particular UI, you can just send an HTTP request to the `process-message` endpoint, with parameters supplied as part of a normal HTTP Request.

In all cases, the input for an Orchestration Service Request must contain the following five elements:
* `message_type`: The type of message to be processed, such as eCR, eLR, or FHIR.
* `data_type`: The file/storage format of the message, such as eCR, FHIR, zip, or hl7. (Note: while it may seem redundant to have both a `message_type` and a `data_type` field, there are currently some inputs for which multiple combinations of data and message values might be valid. For example, an eCR message might be upplied as an eCR record in XML or as a zip file with RR data.)
* `config_file_name`: The name of a JSON configuration file to use as the workflow template to orchestrate. This file must be stored in either the `default_configs` folder as a pre-configured, out-of-the-box option, or it must have already been uploaded to the `custom_configs` directory.
* `message`: The healthcare data to process.
* `rr_data`: Optionally, any Reportability Response data accompanying the message, if and only if the message is an eCR.