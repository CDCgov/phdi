import { render } from "@testing-library/react";
import { axe } from "jest-axe";
import ClinicalInfo from "../ClinicalInfo";
import { returnProceduresTable } from "@/app/utils";

describe("Encounter", () => {
  let container: HTMLElement;

  beforeAll(() => {
    const clinicalNotes = [
      {
        title: "Miscellaneous Notes",
        value: "<paragraph>This patient was only recently discharged for a recurrent GI bleed as described</paragraph>",
      }
    ];
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
    ];
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
        clinicalNotes={clinicalNotes}
        activeProblemsDetails={[]}
        vitalData={vitalData}
        treatmentData={treatmentData}
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
