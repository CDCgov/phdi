import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import EcrSummary, {
  numConditionsText,
} from "../../view-data/components/EcrSummary";

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
      value: (
        <div className={"p-list"}>
          {[
            "Influenza caused by Influenza A virus subtype H5N1 (disorder)",
          ].map((displayName) => (
            <p key={displayName}>{displayName}</p>
          ))}
        </div>
      ),
    },
    {
      title: "RCKMS Rule Summary",
      value: "Cough",
    },
  ];

  const relevantClinical = [
    {
      title: "Relevant Clinical",
      value: "Cough",
    },
  ];

  const relevantLabs = [
    {
      title: "Relevant Labs",
      value: "Covid 19",
    },
  ];

  beforeAll(() => {
    container = render(
      <EcrSummary
        patientDetails={patientDetails}
        encounterDetails={encounterDetails}
        aboutTheCondition={aboutTheCondition}
        relevantClinical={relevantClinical}
        relevantLabs={relevantLabs}
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

describe("numConditionsText", () => {
  const createConditionDetails = (conditions: any[]) => [
    {
      title: "Reportable Condition",
      value: (
        <div className={"p-list"}>
          {conditions.map((displayName: string) => (
            <p key={displayName}>{displayName}</p>
          ))}
        </div>
      ),
    },
    {
      title: "RCKMS Rule Summary",
      value: "Cough",
    },
  ];

  it("Given 0 reportable conditions, should return 0 REPORTABLE CONDITIONS", () => {
    const conditionDetails = createConditionDetails([]);
    const result = numConditionsText(conditionDetails);
    expect(result).toEqual("0 CONDITIONS FOUND");
  });
  it("Given 1 reportable condition, should return 1 REPORTABLE CONDITION", () => {
    const conditionDetails = createConditionDetails(["Influenza"]);
    const result = numConditionsText(conditionDetails);
    expect(result).toEqual("1 CONDITION FOUND");
  });
  it("Given n reportable conditions, should return n REPORTABLE CONDITIONS", () => {
    const conditionDetails = createConditionDetails([
      "Influenza",
      "COVID-19",
      "Measles",
    ]);
    const result = numConditionsText(conditionDetails);
    expect(result).toEqual("3 CONDITIONS FOUND");
  });
});
