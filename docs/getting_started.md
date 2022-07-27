# Getting Started

Below is a guide for using the PHDI SDK. You'll find resources on how to setup a local PHDI environment, make contributions to the project, and more.

- [Getting Started](#getting-started)
  - [Local Development Environment](#local-development-environment)
    - [Hardware](#hardware)
    - [Software](#software)
      - [Overview](#overview)
      - [Installation](#installation)
      - [Extensions](#extensions)
      - [Testing](#testing)
      - [Contributing](#contributing)


## Local Development Environment

The below instructions cover how to setup a development environment for local development of functions

### Hardware

Supported hardware for PHDI tools includes:
* Linux
* Windows 10/11
* Mac (Intel or Apple silicone)
### Software

#### Overview
The core development team uses VSCode as its IDE, but other options (e.g. IntelliJ, Eclipse, PyCharm, etc.) can be viable as well. The rest of this document will assume that you're using VSCode as your IDE. The project itself is coded primarily in Python.

#### Installation
1. Install [Python 3.9+](https://www.python.org/downloads/). Earlier versions are not currently supported.
2. Install [pip](https://pip.pypa.io/en/stable/installation/). The python package installer is 
3. Install [poetry](https://python-poetry.org/docs/). This is the dependency manager for the internal library. 

##### Development Dependencies

In your terminal, navigate to the `src/lib/phdi` directory and run `poetry install`

Foundational  include:

- [Black](https://black.readthedocs.io/en/stable/) - automatic code formatter that enforces PEP best practices
- [mypy](http://mypy-lang.org/) - enables static typing for python
- [pytest](https://docs.pytest.org/en/6.2.x/) - for easy unit testing
- [flake8](https://flake8.pycqa.org/en/latest/) - for code style enforcement

#### Extensions

The following VSCode extensions help streamline development in the IDE:

**Python**
The Python extension adds IntelliSense, linting, debugging and other useful tools.

#### Testing

To perform unit tests on the SDK library code, navigate to the root project directory, and run:
```
pytest
```

#### Contributing

For more information on contributing code, see [CONTRIBUTING.md](CONTRIBUTING.md).
