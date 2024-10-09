import { render, screen } from "@testing-library/react";
import { axe } from "jest-axe";
import EcrSummary, {
  ConditionSummary,
} from "../../view-data/components/EcrSummary";

describe("EcrSummary", () => {
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
      title: "Sex",
      value: "male",
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
  const covidConditionDetails: ConditionSummary[] = [
    {
      title: "Influenza caused by Influenza A virus subtype H5N1 (disorder)",
      snomed: "test-snomed-123",
      conditionDetails: [
        {
          title: "RCKMS Rule Summary",
          value: "covid summary",
        },
      ],
      clinicalDetails: [
        {
          title: "Relevant Clinical",
          value: "covid clinical",
        },
      ],
      labDetails: [
        {
          title: "Relevant Labs",
          value: "covid lab",
        },
      ],
    },
  ];
  const hepConditionDetails: ConditionSummary[] = [
    {
      title: "Hep C",
      snomed: "test-snomed-456",
      conditionDetails: [
        {
          title: "RCKMS Rule Summary",
          value: "hep c summary",
        },
      ],
      clinicalDetails: [
        {
          title: "Relevant Clinical",
          value: "hep c clinical",
        },
      ],
      labDetails: [
        {
          title: "Relevant Labs",
          value: "hep c lab",
        },
      ],
    },
  ];

  beforeAll(() => {});
  it("should match snapshot", () => {
    const { container } = render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        conditionSummary={covidConditionDetails}
      />,
    );

    expect(container).toMatchSnapshot();
  });
  it("should pass accessibility test", async () => {
    const { container } = render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        conditionSummary={covidConditionDetails}
      />,
    );

    expect(await axe(container)).toHaveNoViolations();
  });
  it("should open the condition details when there is one", () => {
    render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        conditionSummary={covidConditionDetails}
      />,
    );

    expect(screen.getByText("covid summary")).toBeVisible();
  });
  it("should open the condition when the snomed matches", () => {
    render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        conditionSummary={[...covidConditionDetails, ...hepConditionDetails]}
        snomed={"test-snomed-456"}
      />,
    );

    expect(screen.getByText("hep c summary")).toBeVisible();
  });
  it("should open no condition details when there is many and no match", () => {
    render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        conditionSummary={[...covidConditionDetails, ...hepConditionDetails]}
      />,
    );

    expect(screen.getByText("hep c summary")).not.toBeVisible();
    expect(screen.getByText("covid summary")).not.toBeVisible();
  });
  it("should show 0 reportable conditions tag", () => {
    render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        conditionSummary={[]}
      />,
    );

    expect(screen.getByText("0 CONDITIONS FOUND"));
  });
  it("should show 1 reportable condition tag", () => {
    render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        conditionSummary={covidConditionDetails}
      />,
    );

    expect(screen.getByText("1 CONDITION FOUND"));
  });
  it("should show 2 reportable conditions tag", () => {
    render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        conditionSummary={[...covidConditionDetails, ...hepConditionDetails]}
      />,
    );

    expect(screen.getByText("2 CONDITIONS FOUND"));
  });
});
