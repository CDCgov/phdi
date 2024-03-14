import { evaluate } from "fhirpath";
import { Bundle, FhirResource, Observation } from "fhir/r4";
import { ColumnInfoInput, PathMappings, evaluateTable } from "@/app/utils";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import React from "react";

/**
 * Evaluates a reference in a FHIR bundle.
 *
 * @param fhirBundle - The FHIR bundle containing resources.
 * @param mappings - Path mappings for resolving references.
 * @param ref - The reference string (e.g., "Patient/123").
 * @returns The FHIR Resource or undefined if not found.
 */
export const evaluateReference = (
  fhirBundle: Bundle,
  mappings: PathMappings,
  ref: string,
) => {
  const [resourceType, id] = ref.split("/");
  return evaluate(fhirBundle, mappings.resolve, {
    resourceType,
    id,
  })[0];
};

// Component, Value, Ref Range, Test Method

export const evaluateDiagnosticReportData = (
  fhirBundle: Bundle<FhirResource>,
  mappings: PathMappings,
) => {
  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Component", infoPath: "observationComponent" },
    { columnName: "Value", infoPath: "observationValue" },
    { columnName: "Ref Range", infoPath: "observationReferenceRange" },
    { columnName: "Test Method", infoPath: "observationMethod" },
  ];

  return evaluate(fhirBundle, mappings["diagnosticReports"]).map((report) => {
    const observations: Observation[] = report.result.map((obsRef) =>
      evaluateReference(fhirBundle, mappings, obsRef.reference),
    );
    const obsTable = evaluateTable(observations, mappings, columnInfo, "");
    return (
      <AccordionLabResults
        title={report.code.coding[0].display}
        abnormalTag={false}
        content={<>{obsTable}</>}
      />
    );
  });
};
