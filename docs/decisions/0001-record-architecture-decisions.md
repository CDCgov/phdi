# 1. Record architecture decisions

Date: 2022-02-07

## Status

Proposed

## Context and Problem Statement

We need to record the architectural and technical decisions made on this project. We should do this when:

- We're making a large decision that will impact future direction of the project
- There is or might be disagreement in the team about a path forward
- We have a need to record such a decision for our future selves and our successors.

## Decision Drivers

- Serve as a reminder of past decisions and our reasons behind them
- Make it easier to change decisions later by documeting the state of the world that held when we wrote them down
- Documenting these decisions for the future benefit of ourselves and future teammates.

## Considered Options

- Not recording decisions
  - Pros: Easy
  - Cons: not helpful for the above goals
- Using Google Docs
  - Pros: more accessible
  - Cons: Less closely tied to the code

## Decision Outcome

We will use Architecture Decision Records, as [described by Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions).

To start with, we'll use this procedure to make a new decision record:

1. create new documents in this folder by copying `template.md`
2. Increment the name of the file by a single number
3. If you need to store supporting files such as images, create a folder named after the record and reference that
4. Discuss your change with the team, and upon agreement with your proposed direction, change `Status` from `Proposed` to `Accepted`.

## Appendix

See Michael Nygard's article, linked above.
