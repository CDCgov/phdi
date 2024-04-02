import { evaluate } from "fhirpath";
import { evaluateReference, evaluateValue } from "@/app/evaluate-service";
import {
  evaluateObservationTable,
  evaluateDiagnosticReportData,
  evaluateLabOrganizationData,
  combineOrgAndReportData,
  ResultObject,
  evaluateLabInfoData,
} from "@/app/labs/utils";
import BundleWithMiscNotes from "@/app/tests/assets/BundleMiscNotes.json";
import { Bundle, DiagnosticReport } from "fhir/r4";
import BundleWithPatient from "@/app/tests/assets/BundlePatient.json";
import BundleLabInfo from "@/app/tests/assets/BundleLabInfo.json";
import { loadYamlConfig } from "@/app/api/utils";
import { render, screen } from "@testing-library/react";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";

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
    const report = evaluate(BundleLabInfo, mappings["diagnosticReports"])[0];
    const actual = evaluateDiagnosticReportData(
      report,
      BundleLabInfo as unknown as Bundle,
      mappings,
    );
    const actualDisplay = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={<>{actual}</>}
      />
    );

    expect(actualDisplay.props.title).toContain(
      "Drugs Of Abuse Comprehensive Screen, Ur",
    );
  });
  it("should evaluate diagnostic report results", () => {
    const report = evaluate(BundleLabInfo, mappings["diagnosticReports"])[0];
    const actual = evaluateDiagnosticReportData(
      report,
      BundleLabInfo as unknown as Bundle,
      mappings,
    );
    const actualDisplay = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={<>{actual}</>}
      />
    );

    render(actualDisplay.props.content);

    expect(screen.getByText("Phencyclidine Screen, Urine")).toBeInTheDocument();
    expect(screen.getByText("Negative")).toBeInTheDocument();
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
      diagnosticReport as DiagnosticReport,
      null as Bundle,
      mappings,
      [],
    );
    expect(actual).toBeUndefined();
  });
});

describe("Evaluate Organization with ID", () => {
  it("should return a matching org", () => {
    const result = evaluateLabOrganizationData(
      "d46ea14e-251a-ab52-3a32-89b12270d9e6",
      BundleLabInfo as unknown as Bundle,
      mappings,
    );
    expect(result[0].value).toEqual(
      "HOAG MEMORIAL HOSPITAL NEWPORT BEACH LABORATORY (CLIA 05D0578635)",
    );
  });
  it("should combine the data into new format", () => {
    const testResultObject: ResultObject = {
      "Organization/d46ea14e-251a-ab52-3a32-89b12270d9e6": [<div></div>],
    };
    const result = combineOrgAndReportData(
      testResultObject,
      BundleLabInfo as unknown as Bundle,
      mappings,
    );
    expect(result[0].organizationDisplayData).toBeArray();
  });
});

describe("Evaluate the lab info section", () => {
  it("should return a list of objects", () => {
    const result = evaluateLabInfoData(
      BundleLabInfo as unknown as Bundle,
      mappings,
    );
    expect(result[0]).toHaveProperty("diagnosticReportDataElements");
    expect(result[0]).toHaveProperty("organizationDisplayData");
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
