import React from "react";
import { render, within } from "@testing-library/react";
import { axe } from "jest-axe";
import ClinicalInfo from "../ClinicalInfo";
import { loadYamlConfig } from "@/app/api/fhir-data/utils";
import { evaluateClinicalData } from "../../../utils";

describe("Snapshot test for Vital Signs (Clinical Info section)", () => {
  let container: HTMLElement;
  beforeAll(() => {
    const vitalData = [
      {
        title: "Vitals",
        value: `Height: 65 inches\n\nWeight: 150 Lbs\n\nBody Mass Index (BMI): 25`,
      },
      {
        title: "Facility Name",
        value: "PRM- Palmdale Regional Medical Center",
      },
      {
        title: "Facility Type",
        value: "Healthcare Provider",
      },
    ];
    container = render(
      <ClinicalInfo
        activeProblemsDetails={[]}
        vitalData={vitalData}
        reasonForVisitDetails={[]}
        immunizationsDetails={[]}
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

describe("Check that Clinical Info components render given FHIR bundle", () => {
  const fhirBundleClinicalInfo = require("../../../tests/assets/BundleClinicalInfo.json");
  const mappings = loadYamlConfig();
  const testClinicalData = evaluateClinicalData(
    fhirBundleClinicalInfo,
    mappings,
  );

  const testImmunizationsData =
    testClinicalData.immunizationsDetails.availableData;
  const testActiveProblemsData =
    testClinicalData.activeProblemsDetails.availableData;
  const testVitalSignsData = testClinicalData.vitalData.availableData;
  const testReasonForVisitData =
    testClinicalData.reasonForVisitDetails.availableData;

  test("eCR Viewer renders immunization table given FHIR bundle with immunization info", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={testImmunizationsData}
        reasonForVisitDetails={[]}
        activeProblemsDetails={[]}
        vitalData={[]}
      />,
    );

    // Ensure that Immunizations Section renders
    const expectedImmunizationsElement = clinicalInfo.getByTestId(
      "immunization-history",
    );
    expect(expectedImmunizationsElement).toBeInTheDocument();

    // Ensure only one table (Immunization History) is rendering
    const expectedTable = clinicalInfo.getAllByTestId("table");
    expect(expectedTable[0]).toBeInTheDocument();
    expect(expectedTable.length).toEqual(1);
  });

  test("eCR Viewer renders active problems table given FHIR bundle with active problems info", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={[]}
        reasonForVisitDetails={[]}
        activeProblemsDetails={testActiveProblemsData}
        vitalData={[]}
      />,
    );

    const expectedActiveProblemsElement =
      clinicalInfo.getByTestId("active-problems");
    expect(expectedActiveProblemsElement).toBeInTheDocument();

    // Ensure only one table (Active Problems) is rendering
    const expectedTable = clinicalInfo.getAllByTestId("table");
    expect(expectedTable[0]).toBeInTheDocument();
    expect(expectedTable.length).toEqual(1);
  });

  test("eCR Viewer renders vital signs given FHIR bundle with vital signs info", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={[]}
        reasonForVisitDetails={[]}
        activeProblemsDetails={[]}
        vitalData={testVitalSignsData}
      />,
    );

    const expectedVitalSignsElement = clinicalInfo.getByTestId("vital-signs");
    expect(expectedVitalSignsElement).toBeInTheDocument();
  });

  test("eCR Viewer renders reason for visit given FHIR bundle with reason for visit info", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={[]}
        reasonForVisitDetails={testReasonForVisitData}
        activeProblemsDetails={[]}
        vitalData={[]}
      />,
    );

    const expectedReasonForVisitElement =
      clinicalInfo.getByTestId("reason-for-visit");
    expect(expectedReasonForVisitElement).toBeInTheDocument();
  });

  test("eCR Viewer renders all Clinical Info sections", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={testImmunizationsData}
        reasonForVisitDetails={testReasonForVisitData}
        activeProblemsDetails={testActiveProblemsData}
        vitalData={testVitalSignsData}
      />,
    );

    const expectedImmunizationsElement = clinicalInfo.getByTestId(
      "immunization-history",
    );
    expect(expectedImmunizationsElement).toBeInTheDocument();

    const expectedActiveProblemsElement =
      clinicalInfo.getByTestId("active-problems");
    expect(expectedActiveProblemsElement).toBeInTheDocument();

    // Ensure the two tables (Immunization History & Active Problems) are rendering
    const expectedTable = clinicalInfo.getAllByTestId("table");
    expect(expectedTable[0]).toBeInTheDocument();
    expect(expectedTable.length).toEqual(2);

    const expectedVitalSignsElement = clinicalInfo.getByTestId("vital-signs");
    expect(expectedVitalSignsElement).toBeInTheDocument();

    const expectedReasonForVisitElement =
      clinicalInfo.getByTestId("reason-for-visit");
    expect(expectedReasonForVisitElement).toBeInTheDocument();
  });
});
