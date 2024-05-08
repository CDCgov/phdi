import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import EcrSummary from "../EcrSummary";

describe("EcrSummary", () => {
  let container: HTMLElement;

  const patientDetails = [
    {
      title: "Patient Name",
      value: "ABEL CASTILLO",
    },
    {
      title: "DOB",
      value: "04/15/2015",
    },
    {
      title: "Patient Address",
      value: "1050 CARPENTER ST\nEDWARDS, CA\n93523-2800, US",
    },
    {
      title: "Patient Contact",
      value: "Home (818)419-5968\nMELLY.C.A.16@GMAIL.COM",
    },
  ];
  const encounterDetails = [
    {
      title: "Facility Name",
      value: "PRM- Palmdale Regional Medical Center",
    },
    {
      title: "Facility Address",
      value: "38600 Medical Center Drive\nPalmdale, CA\n93551, USA",
    },
    {
      title: "Facility Contact",
      value: "(661)382-5000",
    },
    {
      title: "Encounter Date/Time",
      value: "Start: 05/13/2022 7:25 AM UTC\nEnd: 05/13/2022 9:57 AM UTC",
    },
    {
      title: "Encounter Type",
      value: "Emergency",
    },
  ];
  const aboutTheCondition = [
    {
      title: "Reportable Condition",
      value: "Influenza caused by Influenza A virus subtype H5N1 (disorder)",
    },
    {
      title: "RCKMS Rule Summary",
      value: "Cough",
    },
  ];

  beforeAll(() => {
    container = render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        aboutTheCondition={aboutTheCondition}
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
