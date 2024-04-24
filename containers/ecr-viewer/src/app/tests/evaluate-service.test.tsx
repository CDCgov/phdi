import { evaluate } from "fhirpath";
import {
  evaluateReference,
  evaluateTable,
  evaluateValue,
} from "@/app/evaluate-service";
import {
  evaluateObservationTable,
  evaluateDiagnosticReportData,
  evaluateLabOrganizationData,
  combineOrgAndReportData,
  ResultObject,
  evaluateLabInfoData,
  LabReport,
} from "@/app/labs/utils";
import BundleWithMiscNotes from "@/app/tests/assets/BundleMiscNotes.json";
import { Bundle } from "fhir/r4";
import BundleWithPatient from "@/app/tests/assets/BundlePatient.json";
import BundleLabsFinal from "@/app/tests/assets/BundleLabsFinal.json"; // TODO LAB: Rename
import { loadYamlConfig } from "@/app/api/utils";
import { render, screen } from "@testing-library/react";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import { ColumnInfoInput, PathMappings } from "@/app/utils";
import userEvent from "@testing-library/user-event";

const mappings = loadYamlConfig();

describe("Evaluate Reference", () => {
  it("should return undefined if resource not found", () => {
    const actual = evaluateReference(
      BundleWithMiscNotes as unknown as Bundle,
      mappings,
      "Observation/1234",
    );

    expect(actual).toBeUndefined();
  });
  it("should return the resource if the resource is available", () => {
    const actual = evaluateReference(
      BundleWithPatient as unknown as Bundle,
      mappings,
      "Patient/6b6b3c4c-4884-4a96-b6ab-c46406839cea",
    );

    expect(actual.id).toEqual("6b6b3c4c-4884-4a96-b6ab-c46406839cea");
    expect(actual.resourceType).toEqual("Patient");
  });
});

describe("Evaluate Diagnostic Report", () => {
  it("should evaluate diagnostic report title", () => {
    const report = evaluate(BundleLabsFinal, mappings["diagnosticReports"])[0];
    const actual = evaluateDiagnosticReportData(
      report,
      BundleLabsFinal as unknown as Bundle,
      mappings,
    );
    const actualDisplay = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={[<>{actual}</>]}
        organizationId="test"
      />
    );

    expect(actualDisplay.props.title).toContain(
      "STOOL PATHOGENS, NAAT, 12 TO 25 TARGETS",
    );
  });
  it("should evaluate diagnostic report results", () => {
    const report = evaluate(BundleLabsFinal, mappings["diagnosticReports"])[0];
    const actual = evaluateDiagnosticReportData(
      report,
      BundleLabsFinal as unknown as Bundle,
      mappings,
    );
    const actualDisplay = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={[<>{actual}</>]}
        organizationId="test"
      />
    );

    render(actualDisplay.props.content);

    expect(screen.getByText("Campylobacter, NAAT")).toBeInTheDocument();
    expect(screen.getAllByText("Not Detected")).not.toBeEmpty();
  });
  it("the table should not appear when there are no results", () => {
    const diagnosticReport = {
      resource: {
        resourceType: "DiagnosticReport",
        code: {
          coding: [
            {
              display: "Drugs Of Abuse Comprehensive Screen, Ur",
            },
          ],
        },
      },
    };
    const actual = evaluateObservationTable(
      diagnosticReport as unknown as LabReport,
      null as unknown as Bundle,
      mappings,
      [],
    );
    expect(actual).toBeUndefined();
  });
  it("should evaluate test method results", () => {
    const report = evaluate(BundleLabsFinal, mappings["diagnosticReports"])[0];
    const actual = evaluateDiagnosticReportData(
      report,
      BundleLabsFinal as unknown as Bundle,
      mappings,
    );
    const actualDisplay = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={[<>{actual}</>]}
        organizationId="test"
      />
    );

    render(actualDisplay.props.content);

    expect(
      screen.getAllByText("LAB DEVICE: BIOFIRE® FILMARRAY® 2.0 SYSTEM"),
    ).not.toBeEmpty();
  });
  it("should display comment", () => {
    const report = evaluate(BundleLabsFinal, mappings["diagnosticReports"])[2];
    const actual = evaluateDiagnosticReportData(
      report,
      BundleLabsFinal as unknown as Bundle,
      mappings,
    );
    render(actual!);

    expect(screen.getByText("View comment")).toBeInTheDocument();
  });
});

describe("Evaluate Organization with ID", () => {
  it("should return a matching org", () => {
    const result = evaluateLabOrganizationData(
      "22c6cdd0-bde1-e220-9ba4-2c2802f795ad",
      BundleLabsFinal as unknown as Bundle,
      mappings,
      0,
    );
    expect(result[0].value).toEqual("VUMC CERNER LAB");
  });
  it("should combine the data into new format", () => {
    const testResultObject: ResultObject = {
      "Organization/22c6cdd0-bde1-e220-9ba4-2c2802f795ad": [<div></div>],
    };
    const result = combineOrgAndReportData(
      testResultObject,
      BundleLabsFinal as unknown as Bundle,
      mappings,
    );
    expect(result[0].organizationDisplayData).toBeArray();
  });
});

describe("Evaluate the lab info section", () => {
  it("should return a list of objects", () => {
    const result = evaluateLabInfoData(
      BundleLabsFinal as unknown as Bundle,
      mappings,
    );
    expect(result[0]).toHaveProperty("diagnosticReportDataElements");
    expect(result[0]).toHaveProperty("organizationDisplayData");
  });
  it("should properly count the number of labs", () => {
    const result = evaluateLabInfoData(
      BundleLabsFinal as unknown as Bundle,
      mappings,
    );
    expect(result[0].organizationDisplayData[3].title).toEqual(
      "Number of Results",
    );
    expect(result[0].organizationDisplayData[3].value).toEqual(2);
  });
});

describe("evaluate value", () => {
  it("should provide the string in the case of valueString", () => {
    const actual = evaluateValue(
      { resourceType: "Observation", valueString: "abc" } as any,
      "value",
    );

    expect(actual).toEqual("abc");
  });
  it("should provide the string in the case of valueCodeableConcept", () => {
    const actual = evaluateValue(
      {
        resourceType: "Observation",
        valueCodeableConcept: {
          coding: [
            {
              display: "Negative",
            },
          ],
        },
      } as any,
      "value",
    );

    expect(actual).toEqual("Negative");
  });
  describe("Quantity", () => {
    it("should provide the value and string unit with a space inbetween", () => {
      const actual = evaluateValue(
        {
          resourceType: "Observation",
          valueQuantity: { value: 1, unit: "ft" },
        } as any,
        "value",
      );

      expect(actual).toEqual("1 ft");
    });
    it("should provide the value and symbol unit", () => {
      const actual = evaluateValue(
        {
          resourceType: "Observation",
          valueQuantity: { value: 1, unit: "%" },
        } as any,
        "value",
      );

      expect(actual).toEqual("1%");
    });
  });
});

describe("Evaluate Table", () => {
  describe("hiddenBaseText", () => {
    const pathMapping: PathMappings = { idPath: "id", notePath: "note.text" };
    describe("single column", () => {
      const columnInfo: ColumnInfoInput[] = [
        {
          infoPath: "notePath",
          columnName: "Lab notes",
          hiddenBaseText: "notes",
        },
      ];

      it("should show view notes button", () => {
        const fhirResource = [
          {
            note: [
              {
                text: "wow this is interesting",
              },
            ],
          } as any,
        ];
        render(evaluateTable(fhirResource, pathMapping, columnInfo, ""));

        expect(screen.getByText("View notes")).toBeInTheDocument();
        expect(screen.queryByText("wow this is interesting")).not.toBeVisible();
      });
      it("should show notes text and replace 'View notes' with 'Hide notes' when 'View notes' button is clicked", async () => {
        const user = userEvent.setup();
        const pathMapping: PathMappings = { notePath: "note.text" };
        const fhirResource = [
          {
            note: [
              {
                text: "wow this is interesting",
              },
            ],
          } as any,
        ];
        render(evaluateTable(fhirResource, pathMapping, columnInfo, ""));

        await user.click(screen.getByText("View notes"));

        expect(screen.queryByText("View notes")).not.toBeInTheDocument();
        expect(screen.getByText("Hide notes")).toBeInTheDocument();
        expect(screen.getByText("wow this is interesting")).toBeVisible();
      });
      it("should only open one note when 'View notes' is clicked", async () => {
        const user = userEvent.setup();
        const fhirResource = [
          {
            note: [
              {
                text: "wow this is interesting",
              },
            ],
          } as any,
          {
            note: [
              {
                text: "no one should see this",
              },
            ],
          },
        ];

        render(evaluateTable(fhirResource, pathMapping, columnInfo, ""));

        await user.click(screen.getAllByText("View notes")[0]);

        expect(screen.getAllByText("View notes")).toHaveLength(1);
        expect(screen.getByText("no one should see this")).not.toBeVisible();
      });
    });
    it("should span across the whole table", async () => {
      const columnInfo: ColumnInfoInput[] = [
        {
          columnName: "id",
          infoPath: "idPath",
        },
        {
          columnName: "Lab notes",
          infoPath: "notePath",
          hiddenBaseText: "notes",
        },
      ];
      const fhirResource = [
        {
          id: "1234",
          note: [
            {
              text: "wow this is interesting",
            },
          ],
        } as any,
      ];

      render(evaluateTable(fhirResource, pathMapping, columnInfo, ""));

      expect(screen.getByText("wow this is interesting")).toHaveAttribute(
        "colSpan",
        "2",
      );
    });
  });
});
