# Playwright.md

The TEFCA Query Connector uses Playwright Test as its end-to-end testing framework. Playwright is a browser-based testing library that enables tests to run against a variety of different browsers under a variety of different conditions. To manage this suite, Playwright creates some helpful files (and commands) that can be used to tweak its configuration.

## Config and Directories
Playwright's configuration is managed by the file `playwright.config.ts`. This file has information on which browsers to test against, configuration options for those browsers, optional mobile browser ports, retry and other utility options, and a dev webserver. Changing this file will make global changes to Playwright's operations.

By default, Playwright will look for end to end tests in `src/app/tests/e2e`.

## Github Workflow Action
Playwright also creates and manages its own Github Actions workflow, located in `.github/workflows/playwright.yml`. This file can be changed to modify Playwright's behavior in Github.

## Testing Commands and Demos
Playwright provides a number of different ways of executing end to end tests. From the `tefca-viewer/` directory, you can run several commands:

  `npx playwright test`
    Runs the end-to-end tests.

  `npx playwright test --ui`
    Starts the interactive UI mode.

  `npx playwright test --project=chromium`
    Runs the tests only on Desktop Chrome.

  `npx playwright test example`
    Runs the tests in a specific file.

  `npx playwright test --debug`
    Runs the tests in debug mode.

  `npx playwright codegen`
    Auto generate tests with Codegen.

After running a test set on your local, you can also additionally type `npx playwright show-report` to view an HTML report page of different test statuses and results.

An example end to end test spec can be found in `src/app/tests/e2e/example.spec.ts`.

A suite of end to end tests for a sample application called "Todo App" can be found in `/tests-examples/demo-todo-app.spec.ts`.