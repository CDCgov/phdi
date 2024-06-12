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

  Major version releases will reset **MINOR** and **PATCH** versions to 0.
  
* **MINOR** versions introduce new, non-breaking functionality.
  
  Releases with enhancements that do not break backwards compatibility require a minor version update. Common examples of non-breaking changes include:
  * Adding a package, module, or method
  * Adding optional parameters

  Minor version releases _may_ also include fixes.

  Minor versions will reset **PATCH** version to 0.

* **PATCH** versions introduce non-breaking bug fixes.

  Releases that _only_ contain fixes are released as patches.


## PHDI Release Process

### Determine New Version Number
The first step in a release is defining the release's new version number. The previous section describes the different components of Semantic Versioning that should be used in the definition process. In general:

* A release that **breaks existing APIs or function interfaces** should increment the `MAJOR` version and reset the `MINOR` and `PATCH` components to 0.
* A release that **introduces new functionality without breaking an interface** should leave `MAJOR` unchanged, increment `MINOR`, and reset `PATCH` to 0.
* A release that **includes only bug fixes without new functionality** should leave `MAJOR` and `MINOR` unchanged and increment `PATCH`.

### Confirm Release With The Team
Any time a new release needs to go out, you should check with the broader team to see if there's any additional functionality someone wishes to merge into the release. While the merge queue means that most of these changes will automatically be included in the new release so long as they were approved and merged prior to the release PR (see below), checking with others ensures that any required or desired additions make it into the release without needing to repeat the process.

### Create a Release Branch
Once the new version number is defined and all desired functionality is merged into the `main` branch of the github repository, you can safely begin executing the release process. First, create a new branch off of `main` called `release-MAJOR.MINOR.PATCH` (replace each of the SemVer components with the appropriate number in the new release version).

### Update Versioning Files
On the release branch, navigate to the `phdi/__init__.py` file. Replace the version number there with the new release's version number. Then, navigate to the `pyproject.toml` file and do the same thing with the `version` keyword on line 3.

### Open Pull Request
Commit the versioning changes to the branch, then open a new Pull Request for the release. This PR *must* be titled **[RELEASE]-MAJOR.MINOR.PATCH**, including the brackets around "RELEASE" (for example, `[RELEASE]-1.4.4` is a valid PR title, but `RELEASE-1.2.5` is not). Once this PR is approved, you can safely merge it using the merge queue.

### Wait
GitHub Actions will automatically take care of a number of things once the release PR is merged.

* It creates the appropriate containers for the release and publishes their images to the Docker registry
* It deploys the newly updated release to PyPi

If you're going to deploy the new release to AWS (so that it's usable from `dibbs.cloud`, for example), make sure to wait until both of these steps complete. Otherwise, Terraform won't be able to find or pull the new container images for the public services.

### Deploy to AWS
After these steps finish, it's time to send the new release out into the wild. Navigate to the GitHub Actions tab of the `phdi-playground` repo, then click on the `AWS Deployment` option on the left side. Run the deployment from the `main` branch. Congratulations! Once that worklow finishes, the new code is usable at `dibbs.cloud`.