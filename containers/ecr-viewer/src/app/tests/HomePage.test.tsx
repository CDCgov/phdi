import { render, screen } from "@testing-library/react";
import HomePage from "@/app/page";
import {
  getTotalEcrCount,
  listEcrData,
} from "@/app/api/services/listEcrDataService";

jest.mock("../../app/api/services/listEcrDataService");
jest.mock("../components/EcrPaginationWrapper");

describe("Home Page", () => {
  afterEach(() => {
    delete process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER;
    jest.clearAllMocks();
  });
  it("env false value, should not show the homepage", async () => {
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER = "false";
    render(await HomePage({ searchParams: {} }));
    expect(
      screen.getByText("Sorry, this page is not available."),
    ).toBeInTheDocument();
  });
  it("env invalid value, should not show the homepage", async () => {
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER = "foo";
    render(await HomePage({ searchParams: {} }));
    expect(
      screen.getByText("Sorry, this page is not available."),
    ).toBeInTheDocument();
  });
  it("env no value, should not show the homepage", async () => {
    render(await HomePage({ searchParams: {} }));
    expect(
      screen.getByText("Sorry, this page is not available."),
    ).toBeInTheDocument();
  });
  it("env true value, should show the homepage", async () => {
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER = "true";
    const mockData = [{ id: 1, name: "Test Ecr" }];
    (listEcrData as jest.Mock).mockResolvedValue(mockData);
    render(await HomePage({ searchParams: {} }));
    expect(getTotalEcrCount).toHaveBeenCalled();
    expect(
      screen.queryByText("Sorry, this page is not available"),
    ).not.toBeInTheDocument();
  });
});
