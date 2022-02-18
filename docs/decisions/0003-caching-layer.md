# 3. Select a caching layer for repetitive lookups

Date: 2022-02-18

## Status

Draft

## Context and Problem Statement

Several data augmentations may end up being somewhat to very repetitive, and a caching layer may help with

- Speeding up repeated actions
- Reducing the cost of external services

## Decision Drivers

- **Simplicity** - We want to be able to reason about the architecture without cluttering things up
- **Performance** - Most of the point of a caching layer is to improve performance for end users
- **Infra/Cost** - Ideally we don't want to manage/maintain additional infrastructure to do this

## Considered Options

1. Azure Cache for Redis
    1. Pros:
        1. **Intended Use Case** - Caching is one of the primary use cases for Redis, as in the name under Azure
        2. **Performance** - Redis is known to be mature and extremely performant in most situations
        3. **Small Instances** - Small instances (250mb cache) are available for relatively cheap
    2. Cons:
        1. **Managed Infra** - Running Redis under Azure involves leaving an instance running

2. Durable Entities (https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-entities?tabs=csharp)
    1. Pros:
        1. **Built-in** - Provides a built in way to add light persistence to function apps
    2. Cons:
        1. **Complex** - Adds a level of complexity when writing and testing cached function apps
        2. **Unproven** - Relatively unproven for our use cache compared to the other options
        3. **Cleanup** - Cleaning up data would be a manual process, and it's not clear how that would work

3. Cosmos DB
    1. Pros:
        1. **Common Drivers** - Can use available drivers for MongoDB and Cassandra
        2. **Serverless Option** - Can be used without running a dedicated server/cluster
        3. **Use Case** - Has the ability to expire keys after a given number of seconds
    2. Cons:
        1. **Performance** - Adds ~300ms to each request for the first command
        2. **Request Pricing** - Priced by performance - a bug in development could get expensive

4. LRU Cache (Python's `functools.cache` decorator)
    1. Pros:
        1. **Simplicity** - It's built into python and can decorate a normal function
        2. **Performance** - The cache is in local memory for the running instance
        3. **Zero Infra** - Requires zero infrastructure, orchestration or anything else
    2. Cons:
        1. **Local/Batch Only** - It clears when the process stops, so it's only helpful for caching within a given run

## Decision Outcome

Put this ADR up for review and see what people think. It largely depends on the actual implementation of whatever we'd like to cache and how we're using it for which phase.
