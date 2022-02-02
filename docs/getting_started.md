# Getting Started

Below is a guide for getting started on development of the PRIME PHDI Data Ingestion project. You'll find resources on how to setup a local development environment, how we do deployments, and more.

- [Getting Started](#getting-started)
  - [Architecture](#architecture)
  - [Local Development Environment](#local-development-environment)
    - [Hardware](#hardware)
    - [VSCode](#vscode)
    - [Testing](#testing)
      - [Pre-requisites](#pre-requisites)
      - [A note on files](#a-note-on-files)
      - [Sensitive information](#sensitive-information)
      - [Python](#python)
        - [Development dependencies](#development-dependencies)
        - [What is the VSCode Azure integration actually doing?/](#what-is-the-vscode-azure-integration-actually-doing)
        - [Dependencies](#dependencies)
        - [Testing Python](#testing-python)
  - [Docker container development](#docker-container-development)

## Architecture

As of 2/2/22, the below diagram represents our current high-level system architecture:

![Architecture](architecture.png)

We use [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/), along with a combination of [HTTP Triggers](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger) and [Blob Triggers](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger) to move data from an SFTP server to a dedicated blob storage, and then to perform additional operations against this data.

The below char summarizes these functions, their purposes, triggers, inputs, and outputs:

| Name            | Language | FunctionApp           | Purpose                                                                                        | Trigger                                 | Input                                                                                                            | Output                                                          | Effect                                                                                                                                      |             |         |         |       |        |        |
| --------------- | -------- | --------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------- | ------- | ----- | ------ | ------ |
| GeocodeAddress  | Python   | PHDISmartyStreetsTest | Use the SmartyStreets API to parse and validate a passed-in address and return component parts | HTTP                                    | Address string via an "address" parameter                                                                        | {"input": "{INPUT ADDRESS}", "results": [{ADDRESS_COMPONENTS}]} | N/A                                                                                                                                         |             |         |         |       |        |        |
| IngestFunction  | Python   | pitest-functionapp    | Pull in eICR, VXU, and ELR messages from the VDH SFTP server                                   | HTTP                                    | N/A - input params not used                                                                                      | HTTP Status codes - 200 for success, 500 for failure            | Data is copied from VDH SFTP server to the pitestadtastorage storage account, in the "bronze" container, into a virtual folder called "raw" |             |         |         |       |        |        |
| DecryptFunction | Python   | pitest-functionapp    | Use our team private key to decrypt messages in the "raw" folder and output to "decrypted"     | BlobTrigger on path "bronze/raw"        | A blob trigger, operating on files present in the "bronze/raw" directory. Can optionally be passed file contents | N/A                                                             | Data in "pitestdata/bronze/raw" is decrypted, and moved to "pitestdata/bronze/decrypted"                                                    |             |         |         |       |        |        |
| DSTP            | Kotlin   | TBD                   | Take in HL7 data (flat file or XML), and return a JSON representation of this data             | Currently HTTP, may move to BlobTrigger | HL7 flat file or XML                                                                                             | N/A                                                             | Decrypted HL7 data is parsed and output to a specified directory                                                                            | FunctionApp | Purpose | Trigger | Input | Output | Effect |

## Local Development Environment

The below instructions cover how to setup a development environment for local development of functions

### Hardware

Until we have properly containerized our apps, we will need to rely on informal consensus around hardware. As things stand, the "golden path" involves using VSCode on a Mac. Notably, M1 macs are unable to run the `azure-functions-core-tools` package directly (and even have difficulty running it through Rosetta), so please seek out an alternative machine for now!

### VSCode

High-level we follow the guide [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=python) for how to set up Azure Functions directly for integration with VSCode.

Of course it's possible of course to use alternative means of working with these functions - Intellij or other - but the below at least represents a "golden path" which will make certain operations easier.

### Testing

There are two key tools in testing local azure functions:

1. The Azure extension. After installing this, you can go to `Run->Debug` or hit F5, and the function app will be running on localhost.
2. [Azurite](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio) - this is a locally-running docker container that simulates interactions with blob storage. There is a VSCode integration with this as well called `Azurite` that enables you to start and stop this server.
   1. To use this container, set your connection string to `UseDevelopmentStorage=true`as detailed [here](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio)

#### Pre-requisites

1. Install the latest version of [VSCode](https://code.visualstudio.com/download) (or use `brew install vscode`)
2. cmd+shift+p to bring up the command palette, go to `Extensions: Install Extensions`, and install the `Azure Tools` package
3. Open the `Azure Tools` preferences, and hit "Sign in to Azure". Sign in to your CDC Superuser Account
4. Open the `workspace.xcworkspace`. Accept the prompt that asks if you want to optimize for use with VSCode tools

#### A note on files

Using the direct VSCode integration generates a number of files, the details of which are outlined in the above link. All files within the `.vscode` folder should be checked in. Double check that these do not contain environment variables or paths that are specific to your machine. Also, very importantly, **DO NOT** check in `local.settings.json` , this will contain sensitive information.

#### Sensitive information

We use Azure KeyVault for sensitive information, and the "Configuration" properties of each function to store relevant variables. We tie the two together using [Azure KeyVault References](https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references).

You can easily download the environment variable configuration for a given function app using the azure CLI with:

```bash
cd src/FunctionApps/NAME
func azure functionapp fetch-app-settings pitest-functionapp --output-file local.settings.json
func settings decrypt
```

You can then further customize this file.

#### Python

Microsoft maintains a pretty good guide [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Cazurecli-linux%2Capplication-level) for developing Azure functions with Python. We've followed this guide wherever possible, it's worth a look for reference.

##### Development dependencies

We've added a handful of development-only dependencies at `requirements_dev.txt`. Install these with `source .venv/bin/activate; pip install -r requirements_dev.txt`.

These include:

- [Black](https://black.readthedocs.io/en/stable/) - automatic code formatter that enforces PEP best practices
- [mypy](http://mypy-lang.org/) - enables static typing for python
- [pytest](https://docs.pytest.org/en/6.2.x/) - for easy unit testing

##### What is the VSCode Azure integration actually doing?/

Under the hood, this integration is doing the following:

1. Creates a virtual environment (default path `.venv`) and installing all depedencies called out in `requirements.txt`. You can alternatively do this yourself with `source .venv/bin/activate; pip install -r requirements.txt`.
2. Creates `.vscode/tasks.json`, which make it easier to activate the relevant virtual environment, installs dependencies, and starts a debugging session
3. Creates `.vscode/launch.json`, which makes it so that when you hit F5 / go to `Run->Start Debugging` it runs the tasks from (2) and then attaches to the debugger for your functions when running locally.

##### Dependencies

To add a new dependency, add it to `requirements.txt` if it is critical to run the app, and `requirements_dev.txt` if it helps local development. You can manually install these dependencies using `source .venv/bin/activate; pip install -r requirements.txt` or using the built-in F5 action provided by the Azure extension.

Deploying the function app will result it in automatically installing the dependencies in `requirements.txt`.

##### Testing Python

We use [pytest](https://docs.pytest.org/en/6.2.x/) for the purpose of unit testing functions. All functions should have associated pytest tests. Tests live within a `test` directory that is shared between all python-based apps using the same function app.

Files should be named `test_{name}` and each method should begin with `test_` to ensure it is picked up by the Testing tab.

To run tests, go to the `Test` tab and ensure tests can be located. From there you can run necessary automated tests.

Tests that exercise storage blob-related funcitonality should use [Azurite](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio) , those testing SFTP should use SFTP mocks.

## Docker container development

We hope to move toward using Docker for local development shortly. At the moment we are using the folder-based package layout as described above.
