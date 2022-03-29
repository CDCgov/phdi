# 5. ADR Version Control

Date: 2022-03-27

## Status

Proposed

## Context and Problem Statement

As this project moves forward, more people will join the team and new information/insights will be identified, both of which will lead to changes in decisions the team has made and recorded in an ADR previously. As a result, these new decisions will need to be recorded and prior decisions will need to be deprecated. Readers of the codebase should be able to understand when and why a decision changed and what the latest thought process is.

## Decision Drivers

**Transparency -** While Git provides easy means of accessing historical versions of a file, the history of decisions become hidden in a way if we choose to simply update an ADR instead of creating a new one.  
**Immutability -** ADRs, as they were originally proposed, are to be immutable documents, meaning once they're accepted or rejected, the only field that should change is `Status`, and this should only be done to reflect that an ADR has been deprecated or superseded.

## Considered Options

An alternative approach would be to treat the ADR as a mutable document, with each version of that document, captured by Git's version control, as the immutable version of the ADR. Instead of having multiple files that pertain to a decision in its various forms, there is one decision record that has history baked into it. All of the fields, especially `Status` and `Date`, are mutable and should reflect the most recent decision information. The benefits here are that users are not required to peruse through all of the ADRs ensuring that they've found the most recent ADR for the decision of interest.

## Decision Outcome

When a previous ADR becomes outdated and a new decision supersedes it, a new ADR is created that describes all of the pertinent information related to that decision, and the ADR that is being superseded is updated to reflect which ADR supersedes it. This is done by changing the `Status` to `Deprecated` and the text `Amended by ADR #<x>`, where `<x>` is the number of the ADR being added. Any Pull Request that implements an ADR that supersedes another must include both the changes for the new ADR, as well as the changes to the superseded ADR.
