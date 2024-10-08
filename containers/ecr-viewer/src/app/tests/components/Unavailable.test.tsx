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
        title: "Encounter Date/Time",
        value: "",
      },
      {
        title: "Encounter Type",
        value: "",
      },
      {
        title: "Encounter ID",
        value: "",
      },
    ];
    const facilityUnavailableData = [
      {
        title: "Facility Name",
        value: "",
      },
      {
        title: "Facility Address",
        value: "",
      },
      {
        title: "Facility Contact Address",
        value: "",
      },
      {
        title: "Facility Type",
        value: "",
      },
      {
        title: "Facility ID",
        value: "",
      },
    ];
    const providerUnavailableData = [
      {
        title: "Provider Facility Name",
        value: "",
      },
      {
        title: "Provider Facility Address",
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
        title: "EHR Software Name",
        value: "",
      },
      {
        title: "Custodian Contact",
        value: "",
      },
    ];
    container = render(
      <UnavailableInfo
        demographicsUnavailableData={demographicsUnavailability}
        socialUnavailableData={socialUnavailability}
        encounterUnavailableData={encounterUnavailableData}
        facilityUnavailableData={facilityUnavailableData}
        providerUnavailableData={providerUnavailableData}
        symptomsProblemsUnavailableData={[
          ...reasonForVisitUnavailableData,
          ...activeProblemsUnavailableData,
        ]}
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
