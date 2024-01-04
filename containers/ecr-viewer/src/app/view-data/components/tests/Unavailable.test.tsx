import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import UnavailableInfo from "../UnavailableInfo";

describe("UnavailableInfo", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const socialUnavailability = [
      {
        title: "Travel History",
        value: "",
      },
      {
        title: "Pregnancy Status",
        value: "",
      },
      {
        title: "Alcohol Use",
        value: "",
      },
      {
        title: "Sexual Orientation",
        value: "",
      },
      {
        title: "Gender Identity",
        value: "",
      },
    ];
    const encounterUnavailableData = [
      {
        title: "Facility Address",
        value: "",
      },
    ];
    const providerUnavailableData = [
      {
        title: "Provider Name",
        value: "",
      },
    ];
    container = render(
      <UnavailableInfo
        socialUnavailableData={socialUnavailability}
        encounterUnavailableData={encounterUnavailableData}
        providerUnavailableData={providerUnavailableData}
      />,
    ).container;
  });
  it("should match snapshot", () => {
    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    expect(await axe(container)).toHaveNoViolations();
  });
});
