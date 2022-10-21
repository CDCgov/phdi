# PHDI Release Documentation

## Release Methodology: Semantic Versioning
API documentation is published automatically with Sphinx and hosted via GitHub pages. PHDI updates are released to the Python Package Index (PyPI) according to the guidelines set out in [Semantic Versioning 2.0.0](https://semver.org/) with each release's version following the pattern of MAJOR.MINOR.PATCH. The following core tenets describe when each element of a release's version would be updated.

* **MAJOR** versions introduce breaking changes.

  A breaking change breaks backwards-compatibility with previous released versions. In other words, a breaking change is something that may cause a client's implementation to stop working when upgrading from a previous version. Common examples of breaking changes include:
  * Deleting a package or public functions/methods
  * Deleting public function parameters
  * Changing a function name
  * Changing the name or order of required parameters
  * Adding new required parameters
  * Removing, restricting or changing functionality offered by a public function

  Major version releases _may_ also include non-breaking enhancements and fixes.
  
* **MINOR** versions introduce new, non-breaking functionality.
  
  Releases with enhancements that do not break backwards compatibility require a minor version update. Common examples of non-breaking changes include:
  * Adding a package, module, or method
  * Adding optional parameters

  Minor version releases _may_ also include fixes.

* **PATCH** versions introduce non-breaking bug fixes.

  Releases that _only_ contain fixes are released as patches.


## PHDI Release Process

### Define a Target Version
The very first step in a release is defining a version number to release to. The previous section describes the release versioning scheme, and should be used to assign the version number for the next release. Your release will have the following parts:
* `MAJOR`: The major version number for the release. Major versions will reset `MINOR` and `PATCH` versions to 0.
* `MINOR`: The minor version number. Minor versions will reset `PATCH` version to 0.
* `PATCH`: The patch version number.

The values identified will be referenced in the sections below.

### Major Version Release Process
In order to support patching old major version releases without forcing users to upgrade, new major versions involve creating a release branch. The following steps should be followed when a breaking change is merged into `main`, requiring a new major version.

First, in GitHub, create a new branch representing the **old/existing major version**. The new branch should be based on the commit prior to the breaking change that triggers a new version. The naming convention for the new branch is `vMAJOR` where `MAJOR` is the current major version, prior to introducing the breaking change. 

* `MAJOR` is the major version number of the **old/existing major version**
* `COMMIT-HASH` is the commit hash of the commit prior to the breaking merge commit (if the breaking commit has not been merged to `main` and can just specify `main`)


### PyPI Release
#### Authenticating with PyPI
PHDI recommends that users authenticate with PyPI using an API token. To download a token, log in to PyPI and access [project settings](https://pypi.org/manage/project/phdi/settings/). Select "Create a token for phdi" and create a phdi-specific token. Save the token you just created to a file named `.pypitoken` in your project directory. When publishing to PyPI as described later in this section, this API token will be used to authenticate.

#### Prepare to Publish
The steps below depend on defining a full version number using semantic versioning. See the release methodology section above for help assigning a version to your project.

The correct release version should be set both in `pyproject.toml` and `phdi/__init__.py`. When you are ready to release, set the version, commit, and merge the change to the `main` branch.

Once project artifacts above are updated with your version number, tag the commit with a release tag. To assign the release tag, you may execute the following commands:

```bash
git checkout COMMIT-HASH
git tag -a -m "Version MAJOR.MINOR.PATCH" vMAJOR.MINOR.PATCH

```

Next, create a release for the new vertion in GitHub. To create a new release, follow the steps outlined in GitHub's [release creation process](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

The following values should be used:
* Choose a tag: `vMAJOR.MINOR.PATCH` previously created using the commands above
* Release title: `vMAJOR.MINOR.PATCH`
  * `MAJOR`, `MINOR`, and `PATCH` should be replaced with the corresponding major, minor and patch version numbers for the new release.

#### Publishing to PyPI
Once the version has been set, and the release has been defined, you are ready to publish the new version to PyPI. 

To publish to PyPI, run the following command. NOTE: you will need a valid PyPI user with [authentication set up](#authenticating-with-pypi) as described above for this to work!

```bash
poetry publish --build --username __token__ --password `cat .pypitoken`
```

Congratulations! The project is now published!