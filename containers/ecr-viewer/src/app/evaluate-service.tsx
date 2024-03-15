import { evaluate } from "fhirpath";
import { Bundle, FhirResource, Observation, Reference } from "fhir/r4";
import { ColumnInfoInput, PathMappings, evaluateTable } from "@/app/utils";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import React from "react";
import fhirpath_r4_model from "fhirpath/fhir-context/r4";

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

/**
 * Evaluates diagnostic report data and generates formatted lab result accordions for each report.
 * @param {Bundle} fhirBundle - The FHIR bundle containing diagnostic report data.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @returns {React.JSX.Element[]} - An array of React elements representing lab result accordions.
 */
export const evaluateDiagnosticReportData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.JSX.Element[] => {
  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Component", infoPath: "observationComponent" },
    { columnName: "Value", infoPath: "observationValue" },
    { columnName: "Ref Range", infoPath: "observationReferenceRange" },
    { columnName: "Test Method", infoPath: "observationMethod" },
  ];

  return evaluate(fhirBundle, mappings["diagnosticReports"]).map((report) => {
    const observations: Observation[] = report.result.map((obsRef: Reference) =>
      evaluateReference(fhirBundle, mappings, obsRef.reference ?? ""),
    );
    const obsTable = evaluateTable(
      observations,
      mappings,
      columnInfo,
      "",
      false,
    );
    return (
      <AccordionLabResults
        title={report.code.coding[0].display}
        abnormalTag={false}
        content={<>{obsTable}</>}
      />
    );
  });
};

export const evaluateValue = (entry: FhirResource, path: string): string => {
  let data = evaluate(entry, path, undefined, fhirpath_r4_model)[0];
  let value = "";
  if (typeof data === "string") {
    value = data;
  } else if (data?.__path__ === "Quantity") {
    let unit = data.unit;
    const firstLetterRegex = /^[a-z]/i;
    if (unit?.match(firstLetterRegex)) {
      unit = " " + unit;
    }
    value = `${data.value ?? ""}${unit ?? ""}`;
  } else if (data?.__path__ === "CodeableConcept") {
    value = data.coding[0].display;
  } else if (typeof data === "object") {
    console.log(`Not implemented for ${data.__path__}`);
  }
  return value.trim();
};
