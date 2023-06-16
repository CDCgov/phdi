# Tutorials: Release Tutorial
This doc will guide you through the release process and the approvals and steps necessary to create a new release and push it into our pypi (LINK HERE) phdi library. 


## Cutting a new release

Cutting a new release is a straightforward process. Make sure to check if the team wants any last changes to make it to the release or have any reservations about creating a new release. 

1. Let the team know you're about to cut a release.
2. Create a new branch, the name does not matter.
3. In the phdi/__init__.py file, update your version number.
4. In the pyproject.toml, update your version number.
5. In the GitHub repository, create a new pull request. The pull request name must have `[RELEASE]` as the beginning of the title.
6. Request for a team member to approve the PR.
7. Click the green "Merge" button (it may be "Squash and Merge")

After the merging is complete and the github workflow is finished, you can observe your new python release on the pypi phdi library site