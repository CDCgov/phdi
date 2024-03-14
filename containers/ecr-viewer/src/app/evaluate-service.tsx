import { evaluate } from "fhirpath";
import { Bundle, FhirResource } from "fhir/r4";
import { PathMappings } from "@/app/utils";
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

export const evaluateDiagnosticReportData = (
  fhirBundle: Bundle<FhirResource>,
  mappings: PathMappings,
) => {
  return evaluate(fhirBundle, mappings["diagnosticReports"]).map((report) => {
    return (
      <AccordionLabResults
        title={report.code.coding[0].display}
        abnormalTag={false}
        content={<></>}
      />
    );
  });
};
