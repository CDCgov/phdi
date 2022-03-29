# 7. Pull Request Approvals Require All Checks to be Passing

Date: 2022-03-27

## Status

Rejected

## Context and Problem Statement

One of the conditions that must be met before a Pull Request can be merged into `main` is that at least one person review the code. Unfortunately, this condition is not dependent on the checks that are also in place in the repo, and as a result a developer could merge an approved Pull Request, even if the checks are failing.

## Decision Drivers

**Quality -** Developers should be giving their full attention to Pull Requests and making sure that we're all holding each other to the highest standards with our code.  
**Confidence -** Developers should feel confident that when another developer say their code is good to go that that implies a genuine stamp of approval.  
**Trust -** Users of our code should trust it works as intended.

## Considered Options

We could simply require that all status checks pass before allowing merges, a solution that has been submitted as [ADR #8](https://github.com/CDCgov/prime-public-health-data-infrastructure/blob/main/docs/decisions/0008-merging-prs-requires-checks-to-pass.md). This would nullify the need for this ADR as the risk of merging a PR with unsuccessful status checks would no longer exist.

## Decision Outcome

A developer should not approve a Pull Request until all checks have run and returned a successful result. 
