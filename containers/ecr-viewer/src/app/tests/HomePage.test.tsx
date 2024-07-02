import { render } from "@testing-library/react";
import HomePage from "@/app/page";
import { any } from "prop-types";

describe("Home Page", () => {
  let container: HTMLElement;
  it("env false value, should not show the homepage", async () => {
    process.env.STANDALONE_VIEWER = "false";
    container = render(await HomePage(any, any)).container;
    expect(container).toContainHTML("Sorry, this page is not available.");
  });
  it("env invalid value, should not show the homepage", async () => {
    process.env.STANDALONE_VIEWER = "foo";
    container = render(await HomePage(any, any)).container;
    expect(container).toContainHTML("Sorry, this page is not available.");
  });
  it("env no value, should not show the homepage", async () => {
    container = render(await HomePage(any, any)).container;
    expect(container).toContainHTML("Sorry, this page is not available.");
  });
  it("env true value, should show the homepage", async () => {
    process.env.STANDALONE_VIEWER = "true";
    container = render(await HomePage(any, any)).container;
    expect(container).not.toContainHTML("Sorry, this page is not available.");
  });
});
