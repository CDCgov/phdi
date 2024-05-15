import { render, screen } from "@testing-library/react";
import LabInfo from "@/app/view-data/components/LabInfo";
import userEvent from "@testing-library/user-event";
import React from "react";
import BundleLab from "@/app/tests/assets/BundleLab.json";
import { loadYamlConfig } from "@/app/api/services/utils";
import { Bundle } from "fhir/r4";
import { evaluateLabInfoData } from "@/app/services/labsService";

const mappings = loadYamlConfig();

describe("LabInfo", () => {
  const labinfoOrg = evaluateLabInfoData(
    BundleLab as unknown as Bundle,
    mappings,
  );
  const labInfoJsx = <LabInfo labResults={labinfoOrg} />;

  it("all should be collapsed by default", () => {
    render(labInfoJsx);

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
    render(labInfoJsx);
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
    render(labInfoJsx);
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
    const container = render(labInfoJsx).container;
    expect(container).toMatchSnapshot();
  });
});
