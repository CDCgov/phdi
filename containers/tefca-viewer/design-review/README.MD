# Design Review Script

A bash script intended to allow designers and members of the team to easily spin up an instance of the TEFCA Viewer on their local machines for UI/UX review. Currently only MacOS is supported.

## Initial Setup

In order to use this script a copy must be downloaded onto your computer from GitHub . To do this follow these instructions.
1. Open the Terminal application.
2. Copy and paste `curl https://raw.githubusercontent.com/CDCgov/phdi/main/containers/tefca-viewer/design-review/design-review.sh -O` into the Terminal prompt and press enter. This command uses the wget program to download a copy the `design-review.sh` file from this directory to the root level of your user directory e.g. `Users/johndoe`.
3. Copy and paste `chmod +x design-review.sh` into Terminal and press enter. This command assigns executable permissions to `design-review.sh` allowing it to be run.


## Usage

Follow these steps to run script and spin up a local instance of the TEFCA Viewer.

1. Ensure you have completed the initial setup instructions.
2. Open the Terminal application.
3. Copy and paste `./design-reivew.sh <MY-BRANCH>` into the Terminal prompt.
4. Replace `<MY-BRANCH>` with the name of the GitHub branch you would like to conduct a review on. For example, `./design-reivew.sh main` will spin up an instance of the TEFCA Viewer based on the current state of the `main` branch of repository.
5. Press enter. The script will now ensure that all required dependencies are installed on your machine, build and run the TEFCA Viewer, and finally navigate to the landing page in your system's default browser. Please note that because certain dependencies may need to be installed the script make take a few minutes the first time it is run.
6. When you are done with your review to shut the TEFCA Viewer down return to Terminal and press enter.