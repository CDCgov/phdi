# Welcome!
Thank you for your interest in contributing to the Public Health Data Infrastructure (PHDI) project, part of the CDC's Pandemic-Ready Interoperability Modernization Effort (PRIME), a multi-year collaboration between CDC and the U.S. Digital Service (USDS) to strengthen data quality and information technology systems in state and local health departments. There are many ways to contribute, including writing tutorials or blog posts, improving the documentation, submitting bug reports and feature requests, and writing code for PRIME itself.

Before contributing, we encourage you to also read our [LICENSE](LICENSE.md),
[README](README.md), and
[code-of-conduct](code-of-conduct.md)
files, also found in this repository. If you have any questions not
answered in this repository, feel free to [contact us](mailto:prime@cdc.gov).

## Public domain
This project is in the public domain within the United States, and we waive copyright and
related rights in the work worldwide through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
All contributions to this project will be released under the CC0 dedication. By 
submitting a pull request or issue, you are agreeing to comply with this waiver 
of copyright interest and acknowledge that you have no expectation of payment, 
unless pursuant to an existing contract or agreement.

## Bug reports

If you think you found a bug in PHDI, search our [issues list](https://github.com/CDCgov/phdi/issues) in case someone has opened a similar issue. We'll close duplicate issues to help keep our backlog neat and tidy.

It's very helpful if you can prepare a reproduction of the bug. In other words, provide a small test case that we can run to confirm your bug. This makes it easier to find and fix the problem. 

## Feature requests

If you find yourself wishing for a new feature on PHDI, you're probably not alone. 

Open an issue on our [issues list](https://github.com/CDCgov/phdi/issues) that describes the feature you'd like to see, why you want it, and how it should work. Please try to be as descriptive as possible. We can't guarantee that we'll be able to develop a requested feature, but we'll do our best to give it the care and consideration it deserves.

## Contributing code and documentation changes

If you want to contribute a new feature or a bug fix, we ask that you follow a few guidelines. We have a dedicated team of engineers and support staff that works on this project on a daily basis, and following these steps ensures new pieces are interoperable, with no duplicated effort.

* Before you get started, look for an issue you want to work on. Please make sure this issue is not currently assigned to someone else. If there's no existing issue for your idea, please open one. We use the `good first issue` label to mark the problems we think are suitable for new contributors, so that's a good place to start.
* Once you select an issue, please discuss your idea for the fix or implementation in the comments for that issue. It's possible that someone else may have a plan for the issue that the team has discussed, or that there's context you should know before starting implementation. There are often several ways to fix a problem, and it's essential to find the right approach before spending time on a pull request (PR) that can't be merged.
* Once we've discussed your approach and everything looks good, we'll give you formal approval to begin development. Please don't start your development work before you get approval. We don't want you to waste your time on an issue if someone is already hard at work on it, or if there's something else in the way!

### Fork and clone the repository

You need to fork the main code or documentation repository and clone it to your local machine. See
[github help page](https://help.github.com/articles/fork-a-repo) for help. 

Create a branch for your work. 

If you need to base your work on someone else's branch, talk to the branch owner.  

### Coding your changes

As you code, please make sure you add proper comments, documentation, and unit tests. PHDI adheres to strict quality guidelines, regardless of whether a contributing engineer is on the team or external. Please also ensure that you thoroughly test your changes on your local machine before submitting.

#### Commenting guidelines
Commenting is an important part of writing code other people can easily understand (including your future self!). While each developer has a unique style when it comes to writing comments, we have a few guidelines that govern the project, outlined below.

**Function-level comments**

We use [Sphinx](https://www.sphinx-doc.org) to automatically generate html documentation for the PHDI library and rely heavily on function-level documentation to support the automatic generation. The [Sphinx Docstring](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) documentation describes the basic format that Sphinx requires. The following pieces are expected for all PHDI public functions:
```
"""
Basic description of how the function operates

:param myparam: Parameter descriptions for each function parameter.
...
:raises ExceptionType: Exception description for each raised exception.
"""
```

The `type` and `rtype` declarations are _not_ used, as they are inferred by Sphinx from the method signature. The `return` declarations are not used either. Any clarifying information about return value shouuld be placed in the basic description.

The [VS Code Extensions](#extensions) section below outlines how the autoDocstring extension can be used to streamline docstring creation in the VS Code IDE.

**Line-level comments**

Commenting brings the need to balance succinctness with verbosity, and clarity with maintainability. Sometimes striking this balance is more of an art than a science. In general, contributors should feel empowered to strike this balance as they see fit. However, in the interest of quality and consistency, we strive for a few principles when adding line-level comments:
* *Self-documenting code is best*: Use clear, descriptive, and precise names for modules, variables, and functions; write code that speaks for itself.
* *Consider refactoring*: Modularizing and other restructuring can lead to self-documenting code. Clear, cleanly structured code is better than adding comments to explain poorly written or confusing code.
* *Comments should add clarity*: Good comments can add information that can't be easily read or inferred, summarize functionality provided by a block of code, or add context to explain non-idiomatic code. Avoid restating information that's already in function-level comments, or can be easily obtained from within the code itself.  

### How to set up your local environment to contribute to our code

#### Hardware

Supported hardware for PHDI tools includes:
* Linux
* Windows 10/11
* Mac (Intel or Apple silicone)
#### Software

##### Overview
This document will assume that you're using VSCode as your IDE, but other options (e.g., IntelliJ, Eclipse, PyCharm) can be used as well.

##### Installation

1. Install [Python 3.9+](https://www.python.org/downloads/). Earlier versions aren't currently supported.
2. Install [pip](https://pip.pypa.io/en/stable/installation/). The python package installer is used to install poetry and other packages.
3. Install [poetry](https://python-poetry.org/docs/). This is the dependency manager and installer for the internal library. 

First, in your python machine install, or virtual environment, install poetry:
```
pip install poetry
```

In your terminal, navigate to the root project directory and run `poetry install`

##### Testing

To perform unit tests on the SDK library code, navigate to the root project directory and run:

To run tests (and black, and flake8):
```
poetry run make test
```

If that fails, stating a file cannot be found, you can also try running `poetry run pytest` directly to run the tests.

If you're running the SDK library in a virtual environment (in which you've run `poetry install` to install all dependencies), you can also simply activate the environment, navigate to `phdi/tests/`, and run `pytest`.


Foundational libraries used for testing include:
- [pytest](https://docs.pytest.org/en/6.2.x/) - for easy unit testing
- [Black](https://black.readthedocs.io/en/stable/) - automatic code formatter that enforces PEP best practices
- [flake8](https://flake8.pycqa.org/en/latest/) - for code style enforcement

##### Evaluating code coverage

We use `coverage.py` to monitor our test suite's coverage of our code. To evaluate coverage, simply prepend `coverage run -m` before the command you typically use to run the tests (i.e., `coverage run -m pytest` if using the SDK from within a virtual environment). This generates a file `.coverage` in the `tests/` directory, which contains the results of the coverage run. To view a summary of these statistics, run `coverage report`. 

You can also create an HTML-formatted and -tagged report by running `coverage html`, which creates a folder `htmlcov` inside the `tests/` directory. Opening the `index.html` file inside this directory will take you to a browser view of the coverage report and identify which (if any) code statements were not executed in the test run.

More information can be found in the documentation for [coverage](https://coverage.readthedocs.io/en/6.4.4/).

##### Note on coverage of Abstract Classes

In several places in the `phdi` library, we use Python's `AbstractBaseClass` to define a broad concept that will have other, more specific (i.e., vendor-specific, as with the `SmartyGeocodeClient`) implementations elsewhere. While some methods within an `AbstractBaseClass` will have implementations and/or docstrings, others will not, with the implementation being left to an inheriting class. In these cases, abstract methods and properties should be tagged with the inline decorator `# pragma: no cover` so that non-implemented functions don't count as "missed" lines in the trace evaluation for coverage statistics (since they can't be instantiated and run on their own). 

See the [coverage.py docs](https://coverage.readthedocs.io/en/coverage-5.2.1/excluding.html) for more information.

##### Code coverage guidelines

We recognize there's a lot of human judgment when it comes to writing test cases. It's impossible to plan for every scenario in which a function might be used or think of every error that an input data type might cause. To ensure the repository is as robust as reasonably possible, we've developed the following principles around writing tests and code coverage.

1. **We strive for 85% repository coverage at all times.** There's no magic number when it comes to assessing coverage quality. A high coverage percentage doesn't actually guarantee high-quality testing, and focusing too much on getting a coverage number as close to 100% as possible could lead to a false sense of security as well as wasted time and effort. At the same time, it's important we ensure that our tools are tested in a robust way. A coverage statistic of 85% strikes a balance between fixating on the coverage percent and keeping tests robust and accountable.

2. **Any public-facing functions should include at least one test case.** If a user can call function, we want that function to have documented test coverage. Ideally, functions should have multiple tests (see below), but at a minimum, any public function should have at least one. For private or helper functions, discretion is given to the developer, but the principles below might suggest test cases for those, too.

3. **Broadly speaking, tests should address, at a minimum, three areas: the most-likely scenarios, the most complex scenarios, and the most painful failure scenarios.** It's not practical to write tests for every permutation of inputs and results, but we can anticipate the types of use cases that are most likely to come up. Ideally, a function should have one or more tests that demonstrate success and/or failure in its most common use-case(s). Additionally, functions that have complex interactions—whether with their parameters, internal logic, dependencies, etc.—should have tests addressing the robustness of that logic in the face of multiple settings or interactions (for example, a function which accepts 6 configurable parameters might have tests of that function with 4 or even 5 permutations of parameter settings). Finally, if a piece of code could generate a particularly painful result for a user if it were to break, that code should have tests in place around how those issues are handled.

The points above are our goals when it comes to testing and code coverage; they're principles we're always striving to uphold. Below, we've listed some of the more practical, actionable kinds of tests that stem from these principles. We believe that **specific tests should exist to cover, as much as possible, the following cases:**

* _Sucess and failure cases:_ Functions should have one or more tests showing that the function performs its intended job successfully, as well as one or more tests showing how the function handles a failure case or a case where processing isn't possible.
* _All input and output data types:_ Functions should have one or more tests showing, for each possible input or output data type, how the function performs when it receives or creates that data type. 
* _Explicitly raised exceptions:_ If an exception is raised in the body code of a function, even if it's a conditional exception, one or more tests should exist showing that exception being raised.
* _Edge cases (within reason):_ If a function might deal with edge cases in its processing (an empty list or dictionary parameter, for example), one or more tests should exist showing how the function behaves under those conditions.

We recognize that overlap exists between these categories—for example, a test might validate both a failure case, an edge case, and an exception case by providing an empty dictionary as an input parameter. These points are intended as guidelines for the types of tests that should be written holistically to assess a function's robustness. How these principles are put into practical tests is up to the individual developer.

##### Building the docs

We're using [Sphinx](https://www.sphinx-doc.org) to write up external docs, but there's a Make target to help out. To build documentation using Sphinx, run:
```
poetry run make docs
```

This should build a single html file in `docs/_build/singlehtml/index.html`.

##### Extensions

The following VSCode extensions help streamline development in the IDE:

**Python**
The Python extension adds IntelliSense, linting, debugging, and other useful tools.

**Jupyter**
Jupyter extension pack includes renderers and other useful tools for working with Jupyter notebooks.

**autoDocstring**
This extension provides code snippet templates to generate initial docstring content automatically.

##### VS Code Settings

The following VS Code settings help enforce team coding conventions
```
"autoDocstring.docstringFormat": "sphinx-notypes",
"editor.formatOnSave": true,
"editor.rulers": [ 88 ],
"python.formatting.provider": "black",
"python.linting.flake8Enabled": true,
```

### Submitting your changes

Once your changes and tests are ready to submit for review:

1. **Test your changes**

    Run the full local test suite to make sure that nothing is broken.

2. **Rebase your changes**

    Update your local repository with the most recent code from the principal repository, and rebase your branch on top of the latest `main` branch. We prefer your initial changes to be squashed into a single commit. Later, if we ask you to make changes, add the changes as separate commits. This makes the changes easier to review.  

3. **Submit a PR**

    Push your local changes to your forked copy of the repository and [submit a PR](https://help.github.com/articles/using-pull-requests). In the PR, please follow the template provided.

    All PRs must have at least one approval. Please tag several engineers for review; you can see which engineers are most active by checking the repository's commit history. 
    
    Note that you shouldn't squash your commit at the end of the review process. Instead, you should do it when the pull request is [integrated
    via GitHub](https://github.com/blog/2141-squash-your-commits). 

### Reviewer responsibilities
A good code review considers many aspects of the PR:
- Will the code work, and will it work in the **long term**?
- Is the code understandable and readable? Is documentation needed? 
- What are the security implications of the PR?
- Does the PR contain sensitive information like secret keys or passwords? Can these be logged? 

Submitters should help reviewers by calling out how these considerations are met in comments on the review. 


## Credit
This document is a mashup of contributor documents from the CDC, ElasticSearch, SimpleReport, and ReportStream. 
