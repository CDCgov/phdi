import { ExpandCollapseButtons } from "@/app/view-data/components/ExpandCollapseButtons";
import { render, screen } from "@testing-library/react";

describe("expand collapse buttons", () => {
  it("should have aria expand true and hidden removed when expand button is clicked", () => {
    render(
      <div>
        <button
          className={"test-button"}
          data-testid={"button"}
          aria-expanded={false}
        ></button>
        <div
          className={"accordion"}
          data-testid={"accordion"}
          hidden={true}
        ></div>
        <ExpandCollapseButtons
          id={"test"}
          buttonSelector={"button"}
          accordionSelector={".accordion"}
        />
      </div>,
    );
    expect(screen.getByText("Expand All")).toBeInTheDocument();

    screen.getByText("Expand All").click();

    expect(screen.getByTestId("button")).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    expect(screen.getByTestId("accordion")).not.toHaveAttribute("hidden");
  });
  it("should have aria expand false and hidden when collapse button is clicked", () => {
    render(
      <div>
        <button
          className={"test-button"}
          data-testid={"button"}
          aria-expanded={true}
        ></button>
        <div className={"accordion"} data-testid={"accordion"}></div>
        <ExpandCollapseButtons
          id={"test"}
          buttonSelector={"button"}
          accordionSelector={".accordion"}
        />
      </div>,
    );
    expect(screen.getByText("Collapse All")).toBeInTheDocument();

    screen.getByText("Collapse All").click();

    expect(screen.getByTestId("button")).toHaveAttribute(
      "aria-expanded",
      "false",
    );
    expect(screen.getByTestId("accordion")).toHaveAttribute("hidden", "true");
  });
});
