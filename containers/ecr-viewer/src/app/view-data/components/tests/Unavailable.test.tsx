import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import UnavailableInfo from "../UnavailableInfo";

describe("UnavailableInfo", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const demographicsUnavailability = [
      {
        title: "Tribal Affiliation",
        value: "",
      },
      {
        title: "Preffered Language",
        value: "",
      },
    ];
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
    const clinicalUnavailableData = [
      {
        title: "Reason for Visit",
        value: "",
      },
    ];
    const activeProblemsUnavailableData = [
      {
        title: "foo",
        value: "",
      },
    ];
    const vitalUnavailableData = [
      {
        title: "Vitals",
        value: "",
      },
    ];
    const treatmentUnavailableData = [
      {
        title: "Procedures",
        value: "",
      },
    ];
    container = render(
      <UnavailableInfo
        demographicsUnavailableData={demographicsUnavailability}
        socialUnavailableData={socialUnavailability}
        encounterUnavailableData={encounterUnavailableData}
        providerUnavailableData={providerUnavailableData}
        activeProblemsUnavailableData={activeProblemsUnavailableData}
        vitalUnavailableData={vitalUnavailableData}
        treatmentData={treatmentUnavailableData}
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
