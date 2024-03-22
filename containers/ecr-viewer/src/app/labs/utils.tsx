import React from "react";
import { Bundle, Observation, Reference } from "fhir/r4";
import {
  PathMappings,
  CompleteData,
  DisplayData,
  DataDisplay,
  evaluateData,
} from "@/app/utils";
import { evaluateReference, evaluateTable } from "@/app/evaluate-service";
import { evaluate } from "fhirpath";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import {
  formatDateTime,
  formatTablesToJSON,
  extractNumbersAndPeriods,
} from "@/app/format-service";

export interface LabReport {
  result: Array<Reference>;
}

const noData = <span className="no-data">No data</span>;

/**
 * Extracts an array of `Observation` resources from a given FHIR bundle based on a list of observation references.
 *
 * @param {Array<Reference>} observationIds - An array of `Reference` objects pointing to `Observation` resources.
 * @param {Bundle} fhirBundle - The FHIR bundle containing potential `Observation` resources to extract.
 * @returns {Array<Observation>} An array of `Observation` resources from the FHIR bundle that correspond to the
 * given references. If no matching observations are found or if the input references array is empty, an empty array
 * is returned.
 */
export const getObservations = (
  observationIds: Array<Reference>,
  fhirBundle: Bundle,
): Array<Observation> => {
  const ids: Array<string> = observationIds
    .map((id) => {
      return id.reference?.replace("Observation/", "");
    })
    .filter((i): i is string => i !== undefined);

  if (ids.length === 0) return [];

  return ids
    .filter((id) => {
      const e = evaluate(
        fhirBundle,
        `Bundle.entry.resource.where(id = '${id}')`,
      )[0];
      return e !== undefined && e !== null;
    })
    .map((id) => {
      return evaluate(
        fhirBundle,
        `Bundle.entry.resource.where(id = '${id}')`,
      )[0];
    });
};

/**
 * Recursively searches through a nested array of objects to find values associated with a specified search key,
 * and filters results based on a reference value.
 * @param {any[]} result - The array of objects to search through.
 * @param {string} ref - The reference number used to filter results.
 * @param {string} searchKey - The key to search for within the objects.
 * @returns {string} - A comma-separated string containing unique search key values that match the reference number.
 *
 * @example result - JSON object that contains the tables for all lab reports
 * @example ref - Ex. "1.2.840.114350.1.13.297.3.7.2.798268.1670845" or another observation entry reference
 *                value. This value identifies which lab report the Observation is associated with. Function
 *                compares this value to the metadata ID in the tables to verify that the table is
 *                for the correct lab report.
 * @example searchKey - Ex. "Analysis Time" or the field that we are searching data for.
 */
export function searchResultRecord(
  result: any[],
  ref: string,
  searchKey: string,
) {
  let resultsArray: any[] = [];

  // Loop through each table
  for (const table of result) {
    // For each table, recursively search through all nodes
    if (Array.isArray(table)) {
      const nestedResult: any = searchResultRecord(table, ref, searchKey);
      if (nestedResult) {
        return nestedResult;
      }
    } else {
      const keys = Object.keys(table);
      const refNumbers: any[] = [];
      let searchKeyValue: string = "";
      keys.forEach((key) => {
        // Search for search key value
        if (key === searchKey && table[key].hasOwnProperty("value")) {
          searchKeyValue = table[key]["value"];
        }
        // Search for result IDs
        if (
          table[key].hasOwnProperty("metadata") &&
          table[key]["metadata"].hasOwnProperty("data-id")
        ) {
          if (table[key]["metadata"] !== "") {
            refNumbers.push(
              ...extractNumbersAndPeriods([table[key]["metadata"]["data-id"]]),
            );
          }
        }
      });
      const resultRef = [...new Set(refNumbers)].join(",");
      // Skip if IDs don't match (table is not for correct lab report)
      if (resultRef !== ref) {
        continue;
      }
      // Add to array of results, and return unique set
      if (searchKeyValue !== "") {
        resultsArray.push(searchKeyValue);
      }
    }
  }
  return [...new Set(resultsArray)].join(", ");
}

/**
 * Extracts and consolidates the specimen source descriptions from observations within a lab report.
 *
 * @param {LabReport} report - The lab report containing the results to be processed.
 * @param {Bundle} fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param {PathMappings} mappings - An object containing paths to relevant fields within the FHIR resources.
 * @returns {React.ReactNode} A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnSpecimenSource = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.ReactNode => {
  const observations = getObservations(report.result, fhirBundle);
  const specimenSource = observations.flatMap((observation) => {
    return evaluate(observation, mappings["specimenSource"]);
  });
  if (!specimenSource || specimenSource.length === 0) {
    return noData;
  }
  return [...new Set(specimenSource)].join(", ");
};

/**
 * Extracts and formats the specimen collection time(s) from observations within a lab report.
 *
 * @param {LabReport} report - The lab report containing the results to be processed.
 * @param {Bundle} fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param {PathMappings} mappings - An object containing paths to relevant fields within the FHIR resources.
 * @returns {React.ReactNode} A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnCollectionTime = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.ReactNode => {
  const observations = getObservations(report.result, fhirBundle);
  const collectionTime = observations.flatMap((observation) => {
    const rawTime = evaluate(observation, mappings["specimenCollectionTime"]);
    return rawTime.map((dateTimeString) => formatDateTime(dateTimeString));
  });

  if (!collectionTime || collectionTime.length === 0) {
    return noData;
  }

  return [...new Set(collectionTime)].join(", ");
};

/**
 * Extracts and formats the specimen received time(s) from observations within a lab report.
 *
 * @param {LabReport} report - The lab report containing the results to be processed.
 * @param {Bundle} fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param {PathMappings} mappings - An object containing paths to relevant fields within the FHIR resources.
 * @returns {React.ReactNode} A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnReceivedTime = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.ReactNode => {
  const observations = getObservations(report.result, fhirBundle);
  const receivedTime = observations.flatMap((observation) => {
    const rawTime = evaluate(observation, mappings["specimenReceivedTime"]);
    return rawTime.map((dateTimeString) => formatDateTime(dateTimeString));
  });

  if (!receivedTime || receivedTime.length === 0) {
    return noData;
  }

  return [...new Set(receivedTime)].join(", ");
};

/**
 * Extracts and formats a field value from within a lab report (sourced from HTML string).
 *
 * @param {LabReport} report - The lab report containing the results to be processed.
 * @param {Bundle} fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param {PathMappings} mappings - An object containing paths to relevant fields within the FHIR resources.
 * @param {string} fieldName - A string containing the field name for which the value is being searched.
 * @returns {React.ReactNode} A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
export const returnFieldValueFromLabHtmlString = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
  fieldName: string,
): React.ReactNode => {
  // Get reference value (result ID) from Observations
  const observations = getObservations(report.result, fhirBundle);
  const observationRefValsArray = observations.flatMap((observation) => {
    const refVal = evaluate(observation, mappings["observationReferenceValue"]);
    return extractNumbersAndPeriods(refVal);
  });
  const observationRefVal = [...new Set(observationRefValsArray)].join(", "); // should only be 1

  // Get lab reports HTML String (for all lab reports) & convert to JSON
  const labResultString = evaluate(fhirBundle, mappings["labResultDiv"])[0].div;
  const labResultJson = formatTablesToJSON(labResultString);

  // Find field value from matching lab report tables
  const fieldValue = searchResultRecord(
    labResultJson,
    observationRefVal,
    fieldName,
  );

  if (!fieldValue || fieldValue.length === 0) {
    return noData;
  }

  return fieldValue;
};

/**
 * Extracts and formats the analysis date/time(s) from within a lab report (sourced from HTML string).
 *
 * @param {LabReport} report - The lab report containing the analysis times to be processed.
 * @param {Bundle} fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param {PathMappings} mappings - An object containing paths to relevant fields within the FHIR resources.
 * @param {string} fieldName - A string containing the field name for Analysis Time
 * @returns {React.ReactNode} A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnAnalysisTime = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
  fieldName: string,
): React.ReactNode => {
  const fieldVals = returnFieldValueFromLabHtmlString(
    report,
    fhirBundle,
    mappings,
    fieldName,
  );

  if (fieldVals === noData) {
    return noData;
  }

  const analysisTimeArray =
    typeof fieldVals === "string" ? fieldVals.split(", ") : [];
  const analysisTimeArrayFormatted = analysisTimeArray.map((dateTime) => {
    return formatDateTime(dateTime);
  });

  return [...new Set(analysisTimeArrayFormatted)].join(", ");
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

// TODO#: Fix docstring (returns)
/**
 * Evaluates diagnostic report data and generates the lab observations for each report.
 * @param {Bundle} fhirBundle - The FHIR bundle containing diagnostic report data.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @returns {React.JSX.Element[]} - An array of React elements representing the lab observations.
 */
export const evaluateDiagnosticReportData = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Component", infoPath: "observationComponent" },
    { columnName: "Value", infoPath: "observationValue" },
    { columnName: "Ref Range", infoPath: "observationReferenceRange" },
    { columnName: "Test Method", infoPath: "observationMethod" },
  ];
  return evaluateObservationTable(report, fhirBundle, mappings, columnInfo);
};

/**
 * Evaluates lab information and RR data from the provided FHIR bundle and mappings.
 * @param {Bundle} fhirBundle - The FHIR bundle containing lab and RR data.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @returns {{
 *   labInfo: CompleteData,
 *   labResults: React.JSX.Element[]
 * }} An object containing evaluated lab information and lab results.
 */
export const evaluateLabInfoData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
): {
  labInfo: CompleteData;
  labResults: React.JSX.Element[];
} => {
  const labReports = evaluate(fhirBundle, mappings["diagnosticReports"]);
  const labInfo: DisplayData[] = [
    {
      title: "Lab Performing Name",
      value: "",
    },
    {
      title: "Lab Address",
      value: "",
    },
    {
      title: "Lab Contact",
      value: "",
    },
  ];

  const rrData = labReports.map((report) => {
    const labTable = evaluateDiagnosticReportData(report, fhirBundle, mappings);
    const rrInfo: DisplayData[] = [
      {
        title: "Analysis Time",
        value: returnAnalysisTime(
          report,
          fhirBundle,
          mappings,
          "Analysis Time",
        ),
        className: "lab-text-content",
      },
      {
        title: "Collection Time",
        value: returnCollectionTime(report, fhirBundle, mappings),
        className: "lab-text-content",
      },
      {
        title: "Received Time",
        value: returnReceivedTime(report, fhirBundle, mappings),
        className: "lab-text-content",
      },
      {
        title: "Specimen (Source)",
        value: returnSpecimenSource(report, fhirBundle, mappings),
        className: "lab-text-content",
      },
      {
        title: "Anatomical Location/Laterality",
        value: returnFieldValueFromLabHtmlString(
          report,
          fhirBundle,
          mappings,
          "Anatomical Location / Laterality",
        ),
        className: "lab-text-content",
      },
    ];
    if (labTable) rrInfo.unshift({ value: labTable, className: "lab-table" });
    const content: Array<React.JSX.Element> = rrInfo.map((item) => {
      return <DataDisplay item={item} />;
    });
    return (
      <AccordionLabResults
        title={report.code.coding[0].display}
        abnormalTag={false}
        content={content}
      />
    );
  });

  return {
    labInfo: evaluateData(labInfo),
    labResults: rrData,
  };
};
