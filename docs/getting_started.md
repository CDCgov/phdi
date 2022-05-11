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

We use [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/), along with a combination of [HTTP Triggers](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger) and [Blob Triggers](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-blob-trigger) to move data from an SFTP server to a dedicated blob storage, and then to perform additional operations against this data.

The below char summarizes these functions, their purposes, triggers, inputs, and outputs:

| Name            | Language | FunctionApp           | Purpose                                                                                        | Trigger                                 | Input                                                                                                            | Output                                                          | Effect                                                                                                                                      |             |         |         |       |        |        |
| --------------- | -------- | --------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------- | ------- | ----- | ------ | ------ |
| DecryptFunction  | Python   | pitest-python-functionapp    | Pull in encrypted messages from SFTP storage, decrypt, and write to Blob storage.                                    | TBD                                    | TBD                                                                                      | N/A | Successfully decrypted data will be written to blob storage.              |             |         |         |       |        |        |
| IngestFunction  | Python   | pitest-python-functionapp    | Pull in eICR, VXU, and ELR messages from blob storage.  Convert to FHIR format, standardize key fields, and record linkage identifier.                                    | BlobTrigger                                    | N/A - input params not used                                                                                      | N/A | Successfully ingested data will be written to blob storage as well as the FHIR server.              |             |         |         |       |        |        |
| FhirExportFunction | Python   | pitest-python-functionapp    | Export data from the FHIR server     | HttpTrigger        | A blob trigger, operating on files present in the "bronze/raw" directory. Can optionally be passed file contents | N/A                                                             | Data in "pitestdata/bronze/raw" is decrypted, and moved to "pitestdata/bronze/decrypted"                                                    |             |         |         |       |        |        |

## Local Development Environment

The below instructions cover how to setup a development environment for local development of functions

### Hardware

Until we have properly containerized our apps, we will need to rely on informal consensus around hardware. The most common setup on the team is VSCode running on a Mac. It's worth nothing, though, that M1 macs are unable to run the `azure-functions-core-tools` package directly (and even have difficulty running it through Rosetta). Windows-based machines that are running Windows 10/11 Home or higher are viable options as well. However, as the work moves towards containerization, Windows Pro will be necessary in order to run Docker. Each setup will have its own pros and cons, so choose the setup that works best for you, while keeping in mind the tech stack needs, which are defined below.

### Software

#### Overview
The team uses VSCode as its IDE, but other options (e.g. IntelliJ, Eclipse, PyCharm, etc.) can be viable as well. The main drivers behind using VSCode are its integration with Azure, which is a natural byproduct of them both being Microsoft-owned prodcuts, and the amount of documentation that exists to help get the environment setup. The rest of this document will assume that you're using VSCode as your IDE.The project itself is coded primarily in Python.

Lastly, there are some dependencies that the team makes use of in order to test Azure functionality locally, which include [Azurite](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio), [Azure Core Function Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local), and the .NET Core SDK. Azurite is a storage emulator, which will let you mock Azure's different data storage options, such as Tables, Queues, and Blobs. Azure Core Function Tools are the heart of what allows you to develop Azure functionality locally, and the .NET Core SDK is used for some of the functionality you might develop. For example, when building Azure Functions in Java, the .NET framework provides access to bindings (e.g `@BlobTrigger`) that you'll need. 

#### Installation
1. Install the latest version of [VSCode](https://code.visualstudio.com/download) (or use `brew install vscode`).
2. Install the [Azure Core Function Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local), but be sure to install the 3.x version, and not 4.x. 4.x does not work with all Azure functionality as well as one might hope.
3. Install the [.NET Core SDK 3.1](https://dotnet.microsoft.com/en-us/download/dotnet/3.1). Versions 5.0 and 6.0 do not seem to work well with the 3.x Azure Core Function Tools.
4. Install [Python 3.9.x](https://www.python.org/downloads/).  As of this writing, this is the highest Python version supported by Azure Funcation Apps.
5. Install [Azure CLI Tools](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).  These tools are essential to work with various aspects of the Azure cloud. 
In the next section, "Developing Azure Locally", we'll go over which Extensions you need to install, including the Azurite Extension, in order to begin developing Azure functionality.

### Developing Azure Locally

At a high level, we follow the guide [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code) for how to set up Azure Functions directly for integration with VSCode. As mentioned previously, it's possible to use alternative means of working with these functions, but this represents the path that we have found to be well documented and to make certain operations easier. To get started with developing Azure functionality in VSCode efficiently, you first need to install some useful extensions.

#### Extensions

If you prefer to minimize what gets installed on your machine, you can install each of the following extensions, which should provide the functionality that you need.

**Azure CLI Tools**  
These are the tools for developing and running commands for the Azure CLI, which is what's needed when you want to run your Azure Functions locally. 

**Azure Account**  
This is the extension used to sign into Azure and manage your subscription. Be sure to sign in to your CDC Superuser Account once you've installed this extension.

**Azure Functions**  
This is the core extension needed to build the Azure Functions locally.

**Azure Resources**  
This extension isn't explictly necessary, but can be helpful to view and manage Azure resources.

**Azurite**  
This is another core extension to install as it allows you to mock Azure's data storage tools like Tables, Queues, and Blobs so that you can store and access data locally as if you were engaging with those tools. There are other ways to install Azurite, such as with `npm` or Docker, but working with it through the extension works as well. If you'd like to install this via Docker or npm, you can see the installation instructions [here](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=npm).

If you'd prefer to minimize the amount of things you need to install yourself, you can install a single extension, which will provide all of those listed above plus more.

**Azure Tools**  
This extension installs 12 different extensions, which include the five listed above as well as Docker, Azure App Service, Azure Resource Manager, Azure Databases, Azure Storage, Azure Pipelines, and Azure Virtual Machines. If you find yourself needing these extensions, or believe you'll need them in the future, then installing this one extension could be worth it.

_Note: At various points in your project, VS Code may ask you if you want to optimize for use with the tools. If so, be sure to click yes to optimize._

#### Testing

Before diving into the specifics of working with Python, it's worth covering how testing Azure Functionality in VS Code in general works, which is outlined below.

* As long as you have the Azure Functions extension installed (as described above), then you can either click the `Run -> Debug` button (the one that looks like the sideways triangle with the bug) or press `F5` to run the Function.  
* The second thing you'll need implemented is the Azurite storage extension described above. If you've installed this through the VS Code extension, then you can start the container by clicking one of the three buttons in the bottom-right tray of VS Code, which will saying "Azurite Table Service", "Azurite Queue Service", or "Azurite Blob Service". If you've installed Azurite using npm or Docker, use [the documentation](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=npm) to work through how to start the service.  
* To use this container, set your connection string to `UseDevelopmentStorage=true`as detailed [here](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio).

#### Python

Microsoft maintains a pretty good guide [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Cazurecli-linux%2Capplication-level) for developing Azure functions with Python. We've followed this guide wherever possible, it's worth a look for reference.

##### Development Dependencies

We've added a handful of development-only dependencies at `requirements_dev.txt`. Install these with `source .venv/bin/activate; pip install -r requirements_dev.txt`.

These include:

- [Black](https://black.readthedocs.io/en/stable/) - automatic code formatter that enforces PEP best practices
- [mypy](http://mypy-lang.org/) - enables static typing for python
- [pytest](https://docs.pytest.org/en/6.2.x/) - for easy unit testing
- [flake8](https://flake8.pycqa.org/en/latest/) - for code style enforcement

##### What is the VSCode Azure Integration Actually Doing?

Under the hood, this integration is doing the following:

1. Creates a virtual environment (default path `.venv`) and installing all depedencies called out in `requirements.txt`. You can alternatively do this yourself with `source .venv/bin/activate; pip install -r requirements.txt`.
2. Creates `.vscode/tasks.json`, which make it easier to activate the relevant virtual environment, installs dependencies, and starts a debugging session
3. Creates `.vscode/launch.json`, which makes it so that when you hit F5 / go to `Run->Start Debugging` it runs the tasks from (2) and then attaches to the debugger for your functions when running locally.

##### Dependencies

To add a new dependency, add it to `requirements.txt` if it is critical to run the app, and `requirements_dev.txt` if it helps local development. You can manually install these dependencies using `source .venv/bin/activate; pip install -r requirements.txt` or using the built-in F5 action provided by the Azure extension.

Deploying the function app will result in it automatically installing the dependencies in `requirements.txt`.

##### Testing Python

We use [pytest](https://docs.pytest.org/en/6.2.x/) for the purpose of unit testing functions. All functions should have associated pytest tests. Tests live within a `test` directory that is shared between all python-based apps using the same function app.

Files should be named `test_{name}` and each method should begin with `test_` to ensure it is picked up by the Testing tab.

To run tests, go to the `Test` tab and ensure tests can be located. From there you can run necessary automated tests.

Tests that exercise storage blob-related funcitonality should use [Azurite](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=visual-studio) , those testing SFTP should use SFTP mocks.

#### Pushing to Github
##### A Note on Files

Using the direct VSCode integration generates a number of files, the details of which are outlined in the above link. All files within the `.vscode` folder should be checked in. Double check that these do not contain environment variables or paths that are specific to your machine. Also, very importantly, **DO NOT** check in `local.settings.json` , this will contain sensitive information.

##### Sensitive Information

We use Azure KeyVault for sensitive information, and the "Configuration" properties of each function to store relevant variables. We tie the two together using [Azure KeyVault References](https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references).

You can easily download the environment variable configuration for a given function app using the azure CLI with:

```bash
cd src/FunctionApps/NAME
func azure functionapp fetch-app-settings pitest-python-functionapp --output-file local.settings.json
func settings decrypt
```

You can then further customize this file.


## Docker Container Development

We hope to move toward using Docker for local development shortly. At the moment we are using the folder-based package layout as described above.
