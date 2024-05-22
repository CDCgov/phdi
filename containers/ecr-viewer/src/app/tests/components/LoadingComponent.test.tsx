import React from "react";
import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import { EcrLoadingSkeleton } from "@/app/view-data/components/LoadingComponent";

describe("Snapshot test for EcrLoadingSkeleton", () => {
  let container: HTMLElement;

  beforeAll(() => {
    const mockIntersectionObserver = jest.fn();
    mockIntersectionObserver.mockReturnValue({
      observe: () => null,
      unobserve: () => null,
      disconnect: () => null,
    });
    window.IntersectionObserver = mockIntersectionObserver;

    container = render(<EcrLoadingSkeleton />).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
