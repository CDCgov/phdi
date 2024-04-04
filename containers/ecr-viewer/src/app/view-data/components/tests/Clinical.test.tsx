import React from "react";
import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import ClinicalInfo, { TableEntry } from "../ClinicalInfo";
import { loadYamlConfig } from "@/app/api/utils";
import { returnProceduresTable, evaluateClinicalData } from "@/app/utils";
import { Procedure } from "fhir/r4";

describe("Snapshot test for Vital Signs/Encounter (Clinical Info section)", () => {
  let container: HTMLElement;

  beforeAll(() => {
    const proceduresArray = [
      {
        id: "b40f0081-4052-4971-3f3b-e3d9f5e1e44d",
        code: {
          coding: [
            {
              code: "0241U",
              system: "http://www.ama-assn.org/go/cpt",
              display:
                "HC INFECTIOUS DISEASE PATHOGEN SPECIFIC RNA SARS-COV-2/INF A&B/RSV UPPER RESP SPEC DETECTED OR NOT",
            },
          ],
        },
        meta: {
          source: ["ecr"],
          profile: [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure",
          ],
        },
        reason: [
          {
            display: "Struck by nonvenomous lizards, sequela",
            reference: "e436d9b7-6b4e-f553-0314-5a388d15e02e",
          },
        ],
        status: "completed",
        subject: {
          reference: "Patient/5360b569-1354-4ece-b6a1-58b0946fc861",
        },
        identifier: [
          {
            value: "2884257^",
            system: "urn:oid:1.2.840.114350.1.13.502.3.7.1.1988.1",
          },
        ],
        resourceType: "Procedure",
        performedDateTime: "06/24/2022",
      },
      {
        id: "b40f0081-4052-4971-3f3b-e3d9f5e1e44d",
        code: {
          coding: [
            {
              code: "86308",
              system: "http://www.ama-assn.org/go/cpt",
              display: "HC HETEROPHILE ANTIBODIES SCREENING",
            },
          ],
        },
        meta: {
          source: ["ecr"],
          profile: [
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure",
          ],
        },
        reason: [
          {
            display:
              "Routine general medical examination at a health care facility",
            reference: "7cda2e3e-5d91-428f-8abe-517846d4749e",
          },
        ],
        status: "completed",
        subject: {
          reference: "Patient/5360b569-1354-4ece-b6a1-58b0946fc861",
        },
        identifier: [
          {
            value: "2884257^",
            system: "urn:oid:1.2.840.114350.1.13.502.3.7.1.1988.1",
          },
        ],
        resourceType: "Procedure",
        performedDateTime: "06/16/2022",
      },
    ] as unknown as Procedure[];
    const mappings = {
      procedures: "Bundle.entry.resource.where(resourceType='Procedure')",
      procedureName: "Procedure.code.coding.first().display",
      procedureDate: "Procedure.performedDateTime",
      procedureReason: "Procedure.reason.display",
    };
    const treatmentData = [
      {
        title: "Procedures",
        value: returnProceduresTable(proceduresArray, mappings),
      },
    ];
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
        clinicalNotes={[]}
        activeProblemsDetails={[]}
        vitalData={vitalData}
        reasonForVisitDetails={[]}
        immunizationsDetails={[]}
        treatmentData={treatmentData}
        planOfTreatment={[]}
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

describe("Snapshot test for Clinical Notes", () => {
  it("should match snapshot for non table notes", async () => {
    const clinicalNotes = [
      {
        title: "Miscellaneous Notes",
        value: (
          <p>
            This patient was only recently discharged for a recurrent GI bleed
            as described
          </p>
        ),
      },
    ];
    let { container } = render(
      <ClinicalInfo
        clinicalNotes={clinicalNotes}
        activeProblemsDetails={[]}
        vitalData={[]}
        reasonForVisitDetails={[]}
        immunizationsDetails={[]}
        treatmentData={[]}
        planOfTreatment={[]}
      />,
    );
    expect(container).toMatchSnapshot();
    expect(await axe(container)).toHaveNoViolations();
  });
  it("should match snapshot for table notes", async () => {
    const clinicalNotes = [
      {
        title: "Miscellaneous Notes",
        value: (
          <table>
            <thead>
              <tr>
                <th>Active Problems</th>
                <th>Noted Date</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Parkinson's syndrome</td>
                <td>7/25/22</td>
              </tr>
              <tr>
                <td>Essential hypertension</td>
                <td>7/21/22</td>
              </tr>
            </tbody>
          </table>
        ),
      },
    ];
    let { container } = render(
      <ClinicalInfo
        clinicalNotes={clinicalNotes}
        activeProblemsDetails={[]}
        vitalData={[]}
        reasonForVisitDetails={[]}
        immunizationsDetails={[]}
        treatmentData={[]}
        planOfTreatment={[]}
      />,
    );
    expect(container).toMatchSnapshot();
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
  const testTreatmentData = testClinicalData.treatmentData.availableData;

  const testPlanOfTreatment: {
    value: TableEntry[] | undefined;
  }[] = [
    {
      value: [
        {
          Name: "PCR SARS-CoV-2 and Influenza A/B",
          Type: "Lab",
          Priority: "Routine",
          AssociatedDiagnoses: "",
          DateTime: "12/07/2021 4:16 PM CST",
          OrderSchedule: "",
        },
        {
          Name: "Drugs Of Abuse Comprehensive Screen, Ur",
          Type: "Lab",
          Priority: "STAT",
          AssociatedDiagnoses: "",
          DateTime: "12/23/2022 11:13 AM PST",
          OrderSchedule: "",
        },
      ],
    },
  ];

  test("eCR Viewer renders immunization table given FHIR bundle with immunization info", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={testImmunizationsData}
        reasonForVisitDetails={[]}
        activeProblemsDetails={[]}
        vitalData={[]}
        treatmentData={[]}
        clinicalNotes={[]}
        planOfTreatment={[]}
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
        treatmentData={[]}
        clinicalNotes={[]}
        planOfTreatment={[]}
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
        treatmentData={[]}
        clinicalNotes={[]}
        planOfTreatment={[]}
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
        treatmentData={[]}
        clinicalNotes={[]}
        planOfTreatment={[]}
      />,
    );

    const expectedReasonForVisitElement =
      clinicalInfo.getByTestId("reason-for-visit");
    expect(expectedReasonForVisitElement).toBeInTheDocument();
  });

  test("eCR Viewer renders treatment data given FHIR bundle with treatment data info", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={[]}
        reasonForVisitDetails={[]}
        activeProblemsDetails={[]}
        vitalData={[]}
        treatmentData={testTreatmentData}
        clinicalNotes={[]}
        planOfTreatment={[]}
      />,
    );

    const expectedTreatmentElement =
      clinicalInfo.getByTestId("treatment-details");
    expect(expectedTreatmentElement).toBeInTheDocument();

    // Ensure only one table (Treatment) is rendering
    const expectedTable = clinicalInfo.getAllByTestId("table");
    expect(expectedTable[0]).toBeInTheDocument();
    expect(expectedTable.length).toEqual(1);
  });

  test("eCR Viewer renders treatment data given plan of treatment", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={[]}
        reasonForVisitDetails={[]}
        activeProblemsDetails={[]}
        vitalData={[]}
        treatmentData={[]}
        clinicalNotes={[]}
        planOfTreatment={testPlanOfTreatment}
      />,
    );

    const expectedTreatmentElement = clinicalInfo.getByText("Pending Results");
    expect(expectedTreatmentElement).toBeInTheDocument();

    // Ensure only one table (Treatment) is rendering
    const expectedTable = clinicalInfo.getAllByTestId("table");
    expect(expectedTable[0]).toBeInTheDocument();
    expect(expectedTable.length).toEqual(1);
  });

  test("eCR Viewer renders all Clinical Info sections", () => {
    const clinicalInfo = render(
      <ClinicalInfo
        immunizationsDetails={testImmunizationsData}
        reasonForVisitDetails={testReasonForVisitData}
        activeProblemsDetails={testActiveProblemsData}
        vitalData={testVitalSignsData}
        treatmentData={testTreatmentData}
        clinicalNotes={[]}
        planOfTreatment={testPlanOfTreatment}
      />,
    );

    const expectedImmunizationsElement = clinicalInfo.getByTestId(
      "immunization-history",
    );
    expect(expectedImmunizationsElement).toBeInTheDocument();

    const expectedActiveProblemsElement =
      clinicalInfo.getByTestId("active-problems");
    expect(expectedActiveProblemsElement).toBeInTheDocument();

    const expectedTreatmentElement =
      clinicalInfo.getByTestId("treatment-details");
    expect(expectedTreatmentElement).toBeInTheDocument();

    // Ensure the three tables (Immunization History & Active Problems & Treatment) are rendering
    const expectedTable = clinicalInfo.getAllByTestId("table");
    expect(expectedTable[0]).toBeInTheDocument();
    expect(expectedTable.length).toEqual(4);

    const expectedVitalSignsElement = clinicalInfo.getByTestId("vital-signs");
    expect(expectedVitalSignsElement).toBeInTheDocument();

    const expectedReasonForVisitElement =
      clinicalInfo.getByTestId("reason-for-visit");
    expect(expectedReasonForVisitElement).toBeInTheDocument();
  });
});
