import { render, screen } from "@testing-library/react";
import LabInfo from "@/app/view-data/components/LabInfo";
import userEvent from "@testing-library/user-event";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import React from "react";
import { DisplayData } from "@/app/utils";
import { evaluateLabInfoData } from "@/app/labs/utils";
import BundleLabs from "@/app/tests/assets/BundleLabs.json";
import { loadYamlConfig } from "@/app/api/utils";
import { Bundle } from "fhir/r4";

const mappings = loadYamlConfig();

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
  it("all should be collapsed by default", () => {
    render(labInfoJsx());

    screen
      .getAllByTestId("accordionButton", { exact: false })
      .forEach((button) => {
        expect(button).toHaveAttribute("aria-expanded", "false");
      });
    screen
      .getAllByTestId("accordionItem", { exact: false })
      .forEach((accordion) => {
        expect(accordion).not.toBeVisible();
      });
  });
  it("should expand all labs when collapse button is clicked", async () => {
    const user = userEvent.setup();
    render(labInfoJsx());
    const expandButtons = screen.getAllByText("Expand all labs");
    for (const button of expandButtons) {
      await user.click(button);
    }
    screen
      .getAllByTestId("accordionButton", { exact: false })
      .forEach((button) => {
        expect(button).toHaveAttribute("aria-expanded", "true");
      });
    screen
      .getAllByTestId("accordionItem", { exact: false })
      .forEach((accordion) => {
        expect(accordion).toBeVisible();
      });
  });
  it("should hide all labs when collapse button is clicked", async () => {
    const user = userEvent.setup();
    render(labInfoJsx());
    const expandButtons = screen.getAllByText("Expand all labs");
    for (const button of expandButtons) {
      await user.click(button);
    }
    screen
      .getAllByTestId("accordionButton", { exact: false })
      .forEach((button) => {
        expect(button).toHaveAttribute("aria-expanded", "true");
      });
    screen
      .getAllByTestId("accordionItem", { exact: false })
      .forEach((accordion) => {
        expect(accordion).toBeVisible();
      });

    const collapseButtons = screen.getAllByText("Collapse all labs");
    for (const button of collapseButtons) {
      await user.click(button);
    }
    screen
      .getAllByTestId("accordionButton", { exact: false })
      .forEach((button) => {
        expect(button).toHaveAttribute("aria-expanded", "false");
      });
    screen
      .getAllByTestId("accordionItem", { exact: false })
      .forEach((accordion) => {
        expect(accordion).not.toBeVisible();
      });
  });
  it("should match snapshot test", () => {
    const labData = evaluateLabInfoData(
      BundleLabs as unknown as Bundle,
      mappings,
    );
    const labJsx = <LabInfo labResults={labData} />;
    const container = render(labJsx).container;
    expect(container).toMatchSnapshot();
  });
});
