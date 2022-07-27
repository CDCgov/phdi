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
2. Install [pip](https://pip.pypa.io/en/stable/installation/). The python package installer is used to install poetry, and other packages.
3. Install [poetry](https://python-poetry.org/docs/). This is the dependency manager and installer for the internal library. 

First, in your python machine install, or virtual environment, install poetry:
```
pip install poetry
```

In your terminal, navigate to the root project directory and run `poetry install`

#### Testing

To perform unit tests on the SDK library code, navigate to the root project directory, and run:

To run tests (and black, and flake8):
```
poetry run make test
```

If that fails, stating a file cannot be found, you can also try running `poetry run pytest` directly to run the tests.


Foundational libraries used for testing include:
- [pytest](https://docs.pytest.org/en/6.2.x/) - for easy unit testing
- [Black](https://black.readthedocs.io/en/stable/) - automatic code formatter that enforces PEP best practices
- [flake8](https://flake8.pycqa.org/en/latest/) - for code style enforcement

#### Building the docs

We're using [Sphinx](https://www.sphinx-doc.org) to write up external docs, but there's a Make target to help out. To build documentation using Sphinx, run:
```
poetry run make docs
```

This should build a single html file in `docs/_build/singlehtml/index.html`.

#### Extensions

The following VSCode extensions help streamline development in the IDE:

**Python**
The Python extension adds IntelliSense, linting, debugging and other useful tools.

#### Contributing

For more information on contributing code, see [CONTRIBUTING.md](CONTRIBUTING.md).
