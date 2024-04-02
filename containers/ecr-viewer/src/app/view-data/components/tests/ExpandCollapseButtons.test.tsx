import { ExpandCollapseButtons } from "@/app/view-data/components/ExpandCollapseButtons";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

describe("expand collapse buttons", () => {
  const pageJsx = (hidden: boolean) => (
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
        expandButtonText={"Expand all sections"}
        collapseButtonText={"Collapse all sections"}
      />
    </div>
  );
  it("should have aria expand true and hidden removed when expand button is clicked", async () => {
    const user = userEvent.setup();

    render(pageJsx(true));

    await user.click(screen.getByText("Expand all sections"));

    expect(screen.getByTestId("test-button")).toHaveAttribute(
      "aria-expanded",
      "true",
    );
    expect(screen.getByTestId("accordion")).not.toHaveAttribute("hidden");
  });
  it("should have aria expand false and hidden when collapse button is clicked", async () => {
    const user = userEvent.setup();

    render(pageJsx(false));

    await user.click(screen.getByText("Collapse all sections"));

    expect(screen.getByTestId("test-button")).toHaveAttribute(
      "aria-expanded",
      "false",
    );
    expect(screen.getByTestId("accordion")).toHaveAttribute("hidden", "true");
  });
});
