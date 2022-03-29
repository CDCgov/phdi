# 8. Merging Pull Requests Requires All Checks to be Passing

Date: 2022-03-27

## Status

Accepted

## Context and Problem Statement

Merging a Pull Request into the `main` branch does not currently require that the status checks we have in place all be passing. As a result a developer could merge an approved Pull Request, even if the checks are failing.

## Decision Drivers

**Quality -** Developers should be giving their full attention to Pull Requests and making sure that we're all holding each other to the highest standards with our code.  
**Confidence -** Developers should feel confident that when another developer say their code is good to go that that implies a genuine stamp of approval.  
**Trust -** Users of our code should trust it works as intended.

## Considered Options

We could require that all status checks pass before a developer approves the PR, a solution that has been submitted as [ADR #7](https://github.com/CDCgov/prime-public-health-data-infrastructure/blob/main/docs/decisions/0007-pr-approval-requires-checks-to-pass.md). This wouldn't necessarily nullify the need for this ADR, but it would provide some extra reassurances that approvals are being handed out dutifully. 

## Decision Outcome

All status checks must pass before a merge can take place, and this is enforced through the repo's settings under branch protection.
