import { render, screen } from "@testing-library/react";
import LabInfo from "@/app/view-data/components/LabInfo";
import userEvent from "@testing-library/user-event";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import React from "react";

describe("LabInfo", () => {
  const labInfoJsx = () => (
    <LabInfo
      labInfo={[]}
      labResults={[
        <AccordionLabResults
          title={"ph of urine strip"}
          abnormalTag={false}
          content={[<div>5</div>]}
        />,
        <AccordionLabResults
          title={"ph of saliva"}
          abnormalTag={false}
          content={[<div>7</div>]}
        />,
      ]}
    />
  );
  it("should hide all labs when collapse button is clicked", async () => {
    const user = userEvent.setup();

    render(labInfoJsx());

    await user.click(screen.getByText("Collapse all labs"));

    screen
      .getAllByTestId("accordionButton", { exact: false })
      .forEach((button) => {
        expect(button).toHaveAttribute("aria-expanded", "false");
      });
    screen
      .getAllByTestId("accordionItem", { exact: false })
      .forEach((accordion) => {
        expect(accordion).toHaveAttribute("hidden", "true");
      });
  });
  it("should hide all labs when collapse button is clicked", async () => {
    const user = userEvent.setup();

    render(labInfoJsx());
    await user.click(screen.getByText("Collapse all labs"));
    screen
      .getAllByTestId("accordionButton", { exact: false })
      .forEach((button) => {
        expect(button).toHaveAttribute("aria-expanded", "false");
      });
    screen
      .getAllByTestId("accordionItem", { exact: false })
      .forEach((accordion) => {
        expect(accordion).toHaveAttribute("hidden", "true");
      });

    await user.click(screen.getByText("Expand all labs"));
    screen
      .getAllByTestId("accordionButton", { exact: false })
      .forEach((button) => {
        expect(button).toHaveAttribute("aria-expanded", "true");
      });
    screen
      .getAllByTestId("accordionItem", { exact: false })
      .forEach((accordion) => {
        expect(accordion).not.toHaveAttribute("hidden");
      });
  });
});
