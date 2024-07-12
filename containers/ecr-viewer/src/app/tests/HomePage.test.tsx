import { render, waitFor } from "@testing-library/react";
import HomePage from "@/app/page";
import { any } from "prop-types";
import { listEcrData } from "@/app/api/services/listEcrDataService";

jest.mock("../../app/api/services/listEcrDataService");

describe("Home Page", () => {
  let container: HTMLElement;
  afterEach(() => {
    delete process.env.STANDALONE_VIEWER;
    jest.clearAllMocks();
  });
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
    const mockData = [{ id: 1, name: "Test Ecr" }];
    (listEcrData as jest.Mock).mockResolvedValue(mockData);
    container = render(await HomePage(mockData)).container;
    await waitFor(() => {
      expect(listEcrData).toHaveBeenCalled();
      expect(container).not.toContainHTML("Sorry, this page is not available.");
    });
  });
});
