# Design Review Script

A bash script intended to allow designers and members of the team to easily spin up an instance of the eCR Viewer on their local machines for UI/UX review. Currently only MacOS is supported.

## Initial Setup

In order to use this script a copy must be downloaded onto your computer from GitHub. To do this follow these instructions.
1. Open the Terminal application.
2. Copy and paste the following command into the Terminal prompt and press enter.
```
curl https://raw.githubusercontent.com/CDCgov/phdi/main/containers/ecr-viewer/design-review/design-review.sh -O && chmod +x design-review.sh
```
- The first command uses the wget program to download a copy the `design-review.sh` file from this directory to the root level of your user directory e.g. `Users/johndoe`.
- The second command (`chmod +x design-review.sh`) assigns executable permissions to `design-review.sh` allowing it to be run.


## Usage

Follow these steps to run script and spin up a local instance of the eCR Viewer.

1. Ensure you have completed the initial setup instructions.
2. Open the Terminal application.
3. Copy and paste `./design-review.sh <MY-BRANCH> <IS_NON_INTEGRATED> <CONVERT_SEED_DATA>` into the Terminal prompt.
4. Replace `<MY-BRANCH>` with the name of the GitHub branch you would like to conduct a review on. 
    - For example, `./design-review.sh main` will spin up an instance of the eCR Viewer based on the current state of the `main` branch of repository.
5. Replace `<IS_NON_INTEGRATED>` with either `true` or `false`. 
    - Setting it to `true` will show the non-integrated version of the eCR Viewer, while setting it to `false` will show the integrated version. Default value is `true`.
    - If any other text is used for this second argument, an error message will be displayed: `Invalid value for IS_NON_INTEGRATED. It must be 'true' or 'false'`.
6. Replace `<CONVERT_SEED_DATA>` with either `true` or `false`. 
    - `true`: Runs the FHIR conversion process on the available seed data. Use this option when new sample eCRs have been added to the repository. Without running the converter, the new eCRs will not be viewable in the eCR Viewer.
    - `false` (default): Skips the FHIR conversion step, which can save time. Use this option when no new seed data has been added.
    - If any other text is used for this second argument, an error message will be displayed: `Invalid value for CONVERT_SEED_DATA. It must be 'true' or 'false'`.
7. Press enter. The script will now ensure that all required dependencies are installed on your machine, build and run the eCR Viewer, and finally navigate to the landing page in your system's default browser. Please note that because certain dependencies may need to be installed the script make take a few minutes the first time it is run on a machine. Additionally, depending on what needs to be installed you may be prompted at points during installation of dependencies to provide a password or click through some installation screens.
    - Note: If the landing page of the eCR Viewer displays `Something went wrong!`, try reloading the page to resolve the error.
7. When you are done with your review to shut the eCR Viewer down return to Terminal and press enter.
