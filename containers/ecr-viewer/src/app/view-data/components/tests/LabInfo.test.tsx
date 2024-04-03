import { render, screen } from "@testing-library/react";
import LabInfo from "@/app/view-data/components/LabInfo";
import userEvent from "@testing-library/user-event";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import React from "react";
import { DisplayData } from "@/app/utils";

describe("LabInfo", () => {
  const labinfoOrg: DisplayData[] = [
    {
      title: "Lab Name",
      value: "Org1",
    },
    {
      title: "Lab Name",
      value: "Org2",
    },
  ];
  const labInfoJsx = () => (
    <LabInfo
      labResults={[
        {
          diagnosticReportDataElements: [
            <AccordionLabResults
              key={"blah"}
              title={"ph of urine strip"}
              abnormalTag={false}
              content={[<div key={"1"}>5</div>]}
            />,
          ],
          organizationDisplayData: [labinfoOrg[0]],
        },
        {
          diagnosticReportDataElements: [
            <AccordionLabResults
              key={"blah2"}
              title={"ph of saliva"}
              abnormalTag={false}
              content={[<div key={"2"}>7</div>]}
            />,
          ],
          organizationDisplayData: [labinfoOrg[1]],
        },
      ]}
    />
  );
  it("should hide all labs when collapse button is clicked", async () => {
    const user = userEvent.setup();

    render(labInfoJsx());
    const collapseButtons = screen.getAllByText("Collapse all labs");
    collapseButtons.forEach(async (button) => {
      console.log(button);
      await user.click(button);
    });
    screen.debug();
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
    const collapseButtons = screen.getAllByText("Collapse all labs");
    collapseButtons.forEach(async (button) => {
      await user.click(button);
    });
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
