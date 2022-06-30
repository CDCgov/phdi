# 9. Implement Semantic Versioning

Date: 2022-06-28

## Status

Accepted

## Context and Problem Statement

As the PHDI building blocks software continues to develop, documenting the versions that the software goes through will become increasingly important. Users will need to be able to track released versions of the software to ensure that they're using the correct version for their use cases, as well as to identify when updating the library could break their current functionality. Knowledge of their version number also allows users to receive proper support in the event they experience a software problem. Similarly, developers need to be able to document introductions of new features and bug fixes in existing features. Software versioning allows both groups to avoid confusion around the state of the PHDI building blocks library. This ADR documents the rationale for adopting a versioning system overall, as well as explores options for what the most suitable versioning system for PHDI is.

## Decision Drivers

* **Consistency**: Adopting a versioning system facilitates informed use and conversation about the software. Users are able to employ identically-versioned instances of the software in the same fashion, regardless of the machine on which the software is running. Moreover, establishing a versioning system makes it easier for users to obtain help when using the software, whether they're filing bug reports about a particular version or chatting with a developer or other support personnel about a problem. Thus, a good versioning system will allow users and developers alike to communicate information about bugfixes while also ensuring that major or minor functionality present in one version of the software is present in any other similarly-versioned instance.
* **Interpretability**: A user's ability to understand when upgrading their software might break functionality is a key driver in the decision to adopt a versioning system. The adopted versioning should clearly convey information about when functionality or features of the library change, as well as the magnitude of the impact those changes might have on a user's workflow.

## Considered Options

1. **Name Versioning**
  - Defined as versioning that uses names of objects in some category to take the place of major versions of the software.
  - Examples: NATO alphabet for air traffic codes; Apple's use of large felines (and now desert environments) for operating systems
  - Pros:
    * Each name is highly memorable and clearly differentiates large versions being discussed
    * Names should achieve some degree of consistency
  - Cons:
    * Unrelated names do not convey information about major or minor features, or bug fixes, that may be present in the software
    * Doesn't allow for small changes, such as bug fixes, without tooling an entirely new name; or, even worse, small fixes are released without changing the name, which could lead to the software running inconsistently despite the version ostensibly being the same.
2. **Date-of-release Versioning**
  - Defined as versioning marked simply by the standard date on which the version was released
  - Examples: Anaconda package manager
  - Pros:
    * Achieves consistency by being precise about the exact version achieved, which makes discussing or using a version straightforward
  - Cons:
    * Prone to "version verbosity" that becomes hard to separate from one another--did that bug fix patch come out on the 16th or the 17th?
    * No clear relationship between aspects of the version numbers that are changing and what's changing in the software--in fact, it may artificially create the notion that there's a predefined monthly major release schedule
    * Impossible for users to tell at a glance whether a given version upgrade will break their existing functionality
3. **Sequential Number Versioning**
- Defined as versioning that begins with "1" and increments the count with each successive software push
- Examples: Not really any that work out in the wild
- Pros:
  * Largely the same as date-of-release versioning without the drawback of an imposed / artificial schedule
- Cons:
  * Also susceptible to version verbosity, as with date versioning
  * The optics of a massively large number for a version number (i.e. 427) could reduce confidence in our ability to make correct software the first time
  * Creates the temptation to not increment the version number to avoid the above problem, which then eliminates consistency as well
4. **Semantic Versioning**
- Defined as versioning of the form A.B.C. _A_ corresponds to the "major release" number and documents the addition, alteration, or removal of features sufficient to break the existing API. _B_ corresponds to the "minor release" number and documents the addition or removal of features which _do not_ break the existing API. _C_ corresponds to the "patch version" and documents the bug fixes that have been applied to the software.
- Examples: All of Google's internal and external software platforms; the R kernel
- Pros:
  * Achieves transparency by clearly delineating when an aspect of the software changes, as well as showing what that aspect was
  * Achieves consistency by separating out breaking vs non-breaking API changes
  * Achieves interpretability by adding a "patch version" to MAJOR.MINOR versioning schemes, which conveys whether particular bugs have been fixed or not
  * Well-documented, formally used process that reduces ambiguity on the developer side, to the extent that many major software developers around the world use it
  * Optics around version numbers make intuitive sense to users; in other words, they should "feel natural" in a world where things like e.g. operating system numbers are of the form 14.12.21, which allows developers to create lots of changes and alter the version number without creating the feeling of an unstably changing software platform
- Cons:
  * May require careful consideration and discussion around whether a change has actually "broken" the existing API
  * Bug fix / patch number can sometimes be treated as a "catch all" bucket and wind up spiraling to large numbers like sequential number versioning

## Decision Outcome

We are adopting Semantic Versioning to document the PHDI building blocks library's development. It is robust, standardized, and well-documented with precise protocols for when things change and what those changes should be. It will achieve both decision drivers and provide additional clarity for both users and developers.

## Appendix

The full specification for Semantic Versioning can be found (here)[https://semver.org/]
