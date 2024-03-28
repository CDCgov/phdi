import { render, screen } from "@testing-library/react";
import LabInfo from "@/app/view-data/components/LabInfo";
import userEvent from "@testing-library/user-event";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import React from "react";

describe("LabInfo", () => {
  it("should hide all labs when collapse button is clicked", async () => {
    const user = userEvent.setup();

    render(
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
      />,
    );
    await user.click(screen.getByText("Collapse all labs"));

    expect(
      screen.getAllByTestId("accordionButton", { exact: false }),
    ).toHaveAttribute("aria-expanded", "false");
    expect(
      screen.getAllByTestId("accordionItem", { exact: false }),
    ).toHaveAttribute("hidden", "true");
  });
});
