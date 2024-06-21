# Python Upgrade Process

The python upgrade process involves updating the python version in multiple places to ensure that the build runs correctly.

## pyproject.toml

Upgrading pyproject.toml is straightforward, update the python version number to your specified version.

## workflow tests

Update the `TEST_RUNNER_PYTHON_VERSION` to your new python version in all of the `testContainer____.yaml` files.

## Changing requirements.txt

To upgrade python, understanding the current state of the repo is key. Currently as of June 2023, phdi is self-referential because the `requirements.txt` in the containers/\* folder points to the actual phdi pypi project itself. Therefore, when upgrading python, you have to point the requirements.txt to the current branch that has the new version of python. For example, if your branch is named `upgradepython3x`, then your requirements.txt file will have an entry named `phdi @ git+https://github.com/CDCgov/phdi@upgradepython3x`

Once you push these changes into GitHub, you must change the `requirements.txt` file to point to main. Therefore it will be `phdi @ git+https://github.com/CDCgov/phdi@main`

The files that need to be changed are

- containers/alerts/requirements.txt
- containers/ingestion/requirements.txt
- containers/message-parser/requirements.txt
- containers/record-linkage/requirements.txt
- containers/tabulation/requirements.txt
- containers/validation/requirements.txt

## Changing Docker

For each of the Docker files, update the FROM python to your desire version number. Check the Docker website to ensure that the desired version number is supported.

The Docker files that need to be changed are

- containers/alerts/DockerFile
- containers/ingestion/DockerFile
- containers/message-parser/DockerFile
- containers/record-linkage/DockerFile
- containers/tabulation/DockerFile
- containers/validation/DockerFile
