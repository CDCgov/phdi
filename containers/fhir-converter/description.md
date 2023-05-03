# Getting started with the PHDI FHIR Conversion Service

This service relies on Microsoft's FHIR converter to convert messages.

If you plan to run the service via Docker, you can skip to [Running with Docker](#Running-with-docker-(recommended-for-production)). This container will automatically use the Microsoft FHIR converter without need for additional installation.

If you plan to run the service locally via Python, you'll need to install both the Microsoft FHIR Converter CLI and run the PHDI FHIR Converter service. Read on for installation instructions for both.

## Microsoft FHIR Converter CLI Installation Guide
This document provides a guide for installing the [Microsoft FHIR Converter](https://github.com/microsoft/FHIR-Converter) as a Command Line Interface (CLI) tool on Windows, MacOS, and Linux systems, as well as a brief introduction to using the converter.

### Using the .NET Framework
We will use the .NET SDK to build the FHIR Converter from source code. If you have already installed a .NET SDK, skip to [Download and Build the FHIR Converter](#download-and-build-the-fhir-converter), otherwise follow the steps below to install it on your system.

To check if a .NET SDK is installed, try running `dotnet --list-sdks`. You should see an output message that lists the .NET SDK version you have installed, as well as where it's located. It should look something like the following, but note that the version number and filepath will differ depending on which operating system you use and when you installed the .NET SDK.

```
6.0.40 [C:\Program Files\dotnet\sdk]
```

If you see a message like `Command 'dotnet' not found` (MacOS and Linux) or `The term 'dotnet' is not recognized as the name of a cmdlet, function, script file, or operable program` (Windows), then .NET has not been installed. Additionally, if running `dotnet --list-sdks` does not produce any output, then you likely have the .NET runtime installed, but not the SDK. In either event, you should follow the instructions below to install the SDK.

### Install the .NET SDK
The instructions for installing the .NET SDK will differ depending on whether you're using Windows, MacOS, or Linux. MacOS and Linux users will utilize the command line to install the software, while Windows users should use the installer. Instructions for both approaches are below.

#### MacOS and Linux

##### Download the .NET Install Script
Run `wget https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh` to download the .NET installation script from Microsoft.
From the directory containing the `dotnet-install.sh` file, run `sh ./dotnet-install.sh` to execute the script and install .NET. By default, this script installs the .NET SDK, which is perfect for our needs.

_Note: Bash is required to run the script. If you are using a different shell, such as zsh, it is recommend to switch to using Bash._

##### Add .NET to the PATH Environment Variable
Finally, permanently add .NET to you `PATH` variable by running `echo 'export PATH="$PATH:$HOME/.dotnet"' >> ~/.bashrc`.

##### Confirm the Installation
Restart your shell with `exec $SHELL` and then run `dotnet`. If you get a response that looks like what is shown below, then .NET was installed successfully.

```bash
Usage: dotnet [options]
Usage: dotnet [path-to-application]

Options:  
  -h|--help         Display help.  
  --info            Display .NET Core information.  
  --list-sdks       Display the installed SDKs.  
  --list-runtimes   Display the installed runtimes.  

path-to-application:  
  The path to an application .dll file to execute.  
```

#### Windows

##### Install the .NET SDK
Navigate to [https://dotnet.microsoft.com/en-us/download](https://dotnet.microsoft.com/en-us/download) and click on the "Download .NET SDK x64" button. Note that the label may read slightly differently if you're using a 32-bit operating system. Clicking this button will download a file with a name similar to `dotnet-sdk-6.0.400-win-x64.exe`, but note that the name of your file may differ if a new version of the SDK has been released. **The most important thing is to ensure that the file is for the dotnet-sdk and for Windows.**

Open this file and follow the instructions that are presented to you. If you're asked if you should allow this program to make changes to your machine, select yes. Once the installer is finished, you'll be presented with a screen that summarizes what was installed and where it was saved. The default location should be "C:\Program Files\dotnet\". Open File Explorer, navigate to the installation location (C:\Program Files\dotnet), open the "sdk" folder, and confirm that a folder exists with the .NET SDK version as its name.

##### Add .NET to the PATH Environment Variable
Open your Start Menu and type "Environment Variables" into the search bar. Select "Edit environment variables for your account" from the list of options that appear. In the top section labeled "User variables", click the variable called "Path" and then click the "Edit..." button. A new screen will pop up, and you should click the "New" button on the right-hand side. In the text box that is highlighted, enter "C:\Program Files\dotnet" (without the quotes). Hit enter, click "OK" to close the Path screen, and then click "OK" to close the Environment Variables screen.

##### Confirm the Installation
Open Powershell and run `dotnet`. If you get a response that looks like when is shown below, then .Net was installed successfully.

```bash
Usage: dotnet [options]
Usage: dotnet [path-to-application]

Options:  
  -h|--help         Display help.  
  --info            Display .NET Core information.  
  --list-sdks       Display the installed SDKs.  
  --list-runtimes   Display the installed runtimes.  

path-to-application:  
  The path to an application .dll file to execute.  
```

### Download and Build the FHIR Converter

#### Get Microsoft FHIR Converter
Using whichever command line tool you are comfortable with (Powershell on Windows, or Terminal on Linux and MacOS), download the FHIR Converter source code from Github with the following command.

```bash
git clone https://github.com/microsoft/FHIR-Converter
```

This will install the most recent version of the tool. However, if you'd like to use a specific version, you can use a command like this one that specifically downloads the 5.0.4 release (most recent at the time of writing). 
`git clone https://github.com/microsoft/FHIR-Converter.git --branch v5.0.4 --single-branch`

#### Build the FHIR Converter Tool
Navigate to the directory that was just created with the `git clone` command, which should be a directory named "FHIR-Converter" inside of your current directory, and run `dotnet build`.

_Note: If you're using Windows, it's important to perform this action using Powershell instead of a tool like Git Bash. Due to Windows' use of the `\` as its filepath seperator, other terminals can misinterpret the instructions and fail when trying to access directories._

### Using the Microsoft FHIR Converter

Two examples have been provided below of using the FHIR Converter via the `dotnet run` function. Please note that `--` is used to deliminate between arguments that should be passed to `dotnet` as opposed arguments that `dotnet` should be pass to the application, in this case the FHIR Converter, that it is  being used to run. Additionaly, the `-p` option is only required when not calling `dotnet run` from the `FHIR-Converter/src/Health.Fhir.Liquid.Converter.Tool/` directory. For additional information on `dotnet run` please refer to [this documentation from Microsoft](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-run).

#### Message in File to FHIR
The following command can be used to convert a message from a file to FHIR.
`dotnet run convert -p path-to-Microsoft.Health.Fhir.Liquid.Converter.Tool/ -- -d path-to-template subdirectory-for-message-type -r root-template -n path-to-file-to-be-converted -f path-to-output`

#### Covert Message Content Directory to FHIR
The following command can be used to convert the contents of a message provided directly as a string to FHIR.
`dotnet run convert -p path-to-Microsoft.Health.Fhir.Liquid.Converter.Tool/ -- -d path-to-template subdirectory-for-message-type -r root-template -c message-content -f path-to-output`

_Note: The use of `--` in the command is to separate the command line parameters that are passed to .NET vs those that are passed to the FHIR Converter_

#### Using an Alias
To avoid the need for typing `dotnet run convert -p path-to-Microsoft.Health.Fhir.Liquid.Converter.Tool/ -- ` every time you'd like to convert HL7, it is recommended that you create an alias. Instructions for creating an alias on Windows, MacOS, and Linux can be found [here](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/set-alias?view=powershell-7.2), [here](https://wpbeaches.com/make-an-alias-in-bash-or-zsh-shell-in-macos-with-terminal/), and [here](https://www.geeksforgeeks.org/alias-command-in-linux-with-examples/), respectively.


## Running the PHDI FHIR Conversion Service

Once the Microsoft FHIR converter is installed, the FHIR conversion service can be run using Docker (or any other OCI container runtime e.g., Podman), or directly from the Python source code.

### Running with Docker (Recommended for production)

To run the FHIR conversion service with Docker follow these steps.
1. Confirm that you have Docker installed by running `docker -v`. If you do not see a response similar to what is shown below, follow [these instructions](https://docs.docker.com/get-docker/) to install Docker.
```
❯ docker -v
Docker version 20.10.21, build baeda1f
``` 
2. Download a copy of the Docker image from the PHDI repository by running `docker pull ghcr.io/cdcgov/phdi/fhir-converter:main`.
3. Run the service with ` docker run -p 8080:8080 ghcr.io/cdcgov/phdi/fhir-converter:main`.

Congratulations, the ingestion service should now be running on `localhost:8080`!

### Running from Python Source Code
For local development, it may be preferred to run the service directly from Python. To do so, follow the steps below.

1. Ensure that both Git and Python 3.10 or higher are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/fhir-converter/`.
4. Make a fresh virtual environment with `python -m venv .venv`.
5. Activate the virtual environment with `source .venv/bin/activate` (MacOS and Linux), `venv\Scripts\activate` (Windows Command Prompt), or `.venv\Scripts\Activate.ps1` (Windows PowerShell).
5. Install all of the Python dependencies for the ingestion service with `pip install -r requirements.txt` into your virtual environment.
6. Run the FHIR Converter on `localhost:8080` with `python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`. 

### Building the Docker Image

To build the Docker image for the FHIR conversion service from source code instead of downloading it from the PHDI repository, follow these steps.
1. Ensure that both [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and [Docker](https://docs.docker.com/get-docker/) are installed.
2. Clone the PHDI repository with `git clone https://github.com/CDCgov/phdi`.
3. Navigate to `/phdi/containers/fhir-converter/`.
4. Run `docker build -t fhir-converter .`.
5. Run the service with `docker run -p 8080:8080 fhir-converter`.