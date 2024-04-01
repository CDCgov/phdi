import { evaluate } from "fhirpath";
import {
  Bundle,
  CodeableConcept,
  DiagnosticReport,
  FhirResource,
  Observation,
  Quantity,
  Reference,
} from "fhir/r4";
import {
  ColumnInfoInput,
  DisplayData,
  PathMappings,
  evaluateTable,
} from "@/app/utils";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import React from "react";
import fhirpath_r4_model from "fhirpath/fhir-context/r4";
import { formatAddress } from "./format-service";

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
 * Evaluates and generates a table of observations based on the provided DiagnosticReport,
 * FHIR bundle, mappings, and column information.
 * @param {DiagnosticReport} report - The DiagnosticReport containing observations to be evaluated.
 * @param {Bundle} fhirBundle - The FHIR bundle containing observation data.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @param {ColumnInfoInput[]} columnInfo - An array of column information objects specifying column names and information paths.
 * @returns {React.JSX.Element | undefined} The JSX representation of the evaluated observation table, or undefined if there are no observations.
 */
export function evaluateObservationTable(
  report: DiagnosticReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
  columnInfo: ColumnInfoInput[],
) {
  const observations: Observation[] =
    report.result?.map((obsRef: Reference) =>
      evaluateReference(fhirBundle, mappings, obsRef.reference ?? ""),
    ) ?? [];
  let obsTable;
  if (observations?.length > 0) {
    obsTable = evaluateTable(observations, mappings, columnInfo, "", false);
  }
  return obsTable;
}

/**
 * Evaluates diagnostic report data and generates formatted lab result accordions for each report.
 * @param {Bundle} fhirBundle - The FHIR bundle containing diagnostic report data.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @returns {React.JSX.Element[]} - An array of React elements representing lab result accordions.
 */
export const evaluateDiagnosticReportData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
): ResultObject => {
  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Component", infoPath: "observationComponent" },
    { columnName: "Value", infoPath: "observationValue" },
    { columnName: "Ref Range", infoPath: "observationReferenceRange" },
    { columnName: "Test Method", infoPath: "observationMethod" },
  ];
  const evaluatedMappings = evaluate(fhirBundle, mappings["diagnosticReports"]);
  const resultObject: ResultObject = {};
  evaluatedMappings.map((report: DiagnosticReport) => {
    let obsTable = evaluateObservationTable(
      report,
      fhirBundle,
      mappings,
      columnInfo,
    );
    const organizationId = report.performer?.[0].reference ?? "";
    const element = (
      <AccordionLabResults
        title={report.code.coding?.[0].display ?? "\u{200B}"}
        abnormalTag={false}
        content={<>{obsTable}</>}
      />
    );
    groupElementByOrgId(resultObject, organizationId, element);
  });
  return resultObject;
};

/**
 * Modifies result object to be grouped by org id
 * @param resultObject
 * @param organizationId
 * @param element
 */
const groupElementByOrgId = (
  resultObject: ResultObject,
  organizationId: string,
  element: React.JSX.Element,
) => {
  if (resultObject.hasOwnProperty(organizationId)) {
    resultObject[organizationId].push(element);
  } else {
    resultObject[organizationId] = [element];
  }
};

interface ResultObject {
  [key: string]: JSX.Element[]; // Define the type of the values stored in the object
}

export const evaluateLabOrganizationData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
  id: string,
) => {
  const orgMappings = evaluate(fhirBundle, mappings["organizations"]);
  const matchingOrg = orgMappings.filter(
    (organization) => organization.id === id,
  )[0];
  const orgAddress = matchingOrg?.address?.[0];
  const streetAddress = orgAddress?.line ?? [];
  const city = orgAddress?.city ?? "";
  const state = orgAddress?.state ?? "";
  const postalCode = orgAddress?.postalCode ?? "";
  const country = orgAddress?.country ?? "";
  const formattedAddress = formatAddress(
    streetAddress,
    city,
    state,
    postalCode,
    country,
  );
  const contactInfo = matchingOrg?.contact?.[0].telecom?.[0].value ?? "";
  const name = matchingOrg?.name ?? "";
  const matchingOrgData: DisplayData[] = [
    { title: "Lab Name", value: name },
    { title: "Lab Address", value: formattedAddress },
    { title: "Lab Contact", value: contactInfo },
  ];
  return matchingOrgData;
};

/**
 * Evaluates the FHIR path and returns the appropriate string value. Supports choice elements
 *
 * @param {FhirResource} entry - The FHIR resource to evaluate.
 * @param {string} path - The path within the resource to extract the value from.
 * @returns {string} - The evaluated value as a string.
 */
export const evaluateValue = (entry: FhirResource, path: string): string => {
  let originalValue = evaluate(entry, path, undefined, fhirpath_r4_model)[0];
  let value = "";
  if (typeof originalValue === "string") {
    value = originalValue;
  } else if (originalValue?.__path__ === "Quantity") {
    const data = originalValue as Quantity;
    let unit = data.unit;
    const firstLetterRegex = /^[a-z]/i;
    if (unit?.match(firstLetterRegex)) {
      unit = " " + unit;
    }
    value = `${data.value ?? ""}${unit ?? ""}`;
  } else if (originalValue?.__path__ === "CodeableConcept") {
    const data = originalValue as CodeableConcept;
    value = data.coding?.[0].display || data.text || "";
  } else if (typeof originalValue === "object") {
    console.log(`Not implemented for ${originalValue.__path__}`);
  }
  return value.trim();
};
