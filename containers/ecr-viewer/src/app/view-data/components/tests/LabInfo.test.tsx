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
              organizationId="abcd"
            />,
          ],
          organizationDisplayData: [labinfoOrg[0]],
          organizationId: "abcd",
        },
        {
          diagnosticReportDataElements: [
            <AccordionLabResults
              key={"blah2"}
              title={"ph of saliva"}
              abnormalTag={false}
              content={[<div key={"2"}>7</div>]}
              organizationId="efgh"
            />,
          ],
          organizationDisplayData: [labinfoOrg[1]],
          organizationId: "efgh",
        },
      ]}
    />
  );
  it("should hide all labs when collapse button is clicked", async () => {
    render(labInfoJsx());
    const collapseButtons = screen.getAllByText("Collapse all labs");
    for (const button of collapseButtons) {
      await userEvent.click(button);
    }
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
    for (const button of collapseButtons) {
      await userEvent.click(button);
    }
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

    const expandButtons = screen.getAllByText("Expand all labs");
    for (const button of expandButtons) {
      await userEvent.click(button);
    }
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
