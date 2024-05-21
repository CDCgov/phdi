import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import UnavailableInfo from "../../view-data/components/UnavailableInfo";

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
    const reasonForVisitUnavailableData = [
      {
        title: "Reason for Visit",
        value: "",
      },
    ];
    const activeProblemsUnavailableData = [
      {
        title: "Problems List",
        value: "",
      },
    ];
    const immunizationsUnavailableData = [
      {
        title: "Immunization History",
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
    const clinicalNotesData = [
      {
        title: "Miscellaneous Notes",
        value: "",
      },
    ];
    const ecrMetadata = [
      {
        title: "Sender Software",
        value: "",
      },
    ];
    container = render(
      <UnavailableInfo
        demographicsUnavailableData={demographicsUnavailability}
        socialUnavailableData={socialUnavailability}
        encounterUnavailableData={encounterUnavailableData}
        providerUnavailableData={providerUnavailableData}
        reasonForVisitUnavailableData={reasonForVisitUnavailableData}
        activeProblemsUnavailableData={activeProblemsUnavailableData}
        immunizationsUnavailableData={immunizationsUnavailableData}
        vitalUnavailableData={vitalUnavailableData}
        treatmentData={treatmentUnavailableData}
        clinicalNotesData={clinicalNotesData}
        ecrMetadataUnavailableData={ecrMetadata}
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
