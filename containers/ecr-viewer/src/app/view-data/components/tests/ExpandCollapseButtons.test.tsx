import { ExpandCollapseButtons } from "@/app/view-data/components/ExpandCollapseButtons";
import { render, screen } from "@testing-library/react";

describe("expand collapse buttons", () => {
  const exampleDisplay = (hidden: boolean) => (
    <div>
      <button
        className={"test-button"}
        data-testid={"test-button"}
        aria-expanded={!hidden}
      />
      <div className={"accordion"} data-testid={"accordion"} hidden={hidden} />
      <ExpandCollapseButtons
        id={"test"}
        buttonSelector={"button"}
        accordionSelector={".accordion"}
      />
    </div>
  );
  it("should have aria expand true and hidden removed when expand button is clicked", () => {
    render(exampleDisplay(true));

    screen.getByText("Expand all sections").click();

    expect(screen.getByTestId("test-button")).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    expect(screen.getByTestId("accordion")).not.toHaveAttribute("hidden");
  });
  it("should have aria expand false and hidden when collapse button is clicked", () => {
    render(exampleDisplay(false));

    screen.getByText("Collapse all sections").click();

    expect(screen.getByTestId("test-button")).toHaveAttribute(
      "aria-expanded",
      "false",
    );
    expect(screen.getByTestId("accordion")).toHaveAttribute("hidden", "true");
  });
});
