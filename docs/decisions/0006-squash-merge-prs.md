# 6. Squash Merge Pull Requests

Date: 2022-03-27

## Status

Accepted

## Context and Problem Statement

For any given bug or feature of average complexity that a developer is working on, there is a high probability that the developer will commit their code several times. As a result, when that code is ready to be merged the branch will have several commits, and thus commit messages, which can pollute the history for the `main` branch.

## Decision Drivers

**Readability -** A user should be able to view the history of the `main` branch and get a sense of what was added to the project at any given step without being inundated with commit messages like "fixing typo".  
**Simplicity -** Achieving the desired outcome should take as little effort on the part of the developer, and impacting their natural workflow as minimally, as possible.
**Conformity -** Other projects within the PRIME umbrella are taking this same approach, which provides some cohesion across product teams. 

## Considered Options

Two alternative solutions are:

1. The Status Quo - Continue doing what has been done up to this point, which is to allow the full history of any branch to be included in the `main` branch during merging.
  - Pros: Doesn't require any change in our current behavior.  
  - Cons: Pollutes the `main` branch's commit history making it harder to read.  
2. The Amend Approach - Ask developers to use `git commit --amend` to continuously update the initial commit for any given branch.  
  - Pros: Minimizes the number of commit messages for any given branch, keeping the `main` branch's history clean and readable.  
  - Cons: Makes it harder for developers to revert back to any other state other than the previous state, potentially complicating their workflow.

## Decision Outcome

When merging a Pull Request, the "Squash and merge" option must be selected instead of "Merge pull request", which can be done by clicking the down arrow next to the "Merge pull request" button.
