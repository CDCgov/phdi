import React from "react";
import { Bundle, Observation, Organization, Reference } from "fhir/r4";
import { PathMappings, ColumnInfoInput, noData } from "@/app/utils";
import { evaluate } from "@/app/view-data/utils/evaluate";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import {
  formatDateTime,
  extractNumbersAndPeriods,
  formatAddress,
  formatPhoneNumber,
} from "@/app/services/formatService";
import { ObservationComponent } from "fhir/r4b";
import EvaluateTable from "@/app/view-data/components/EvaluateTable";
import { evaluateReference, evaluateValue } from "./evaluateFhirDataService";
import { DataDisplay, DisplayDataProps } from "@/app/DataDisplay";
import {
  formatTablesToJSON,
  TableJson,
} from "@/app/services/formatTablesToJSON";

export interface LabReport {
  result: Array<Reference>;
}

export interface ResultObject {
  [key: string]: JSX.Element[];
}

export interface LabReportElementData {
  organizationId: string;
  diagnosticReportDataElements: React.JSX.Element[];
  organizationDisplayDataProps: DisplayDataProps[];
}

/**
 * Extracts an array of `Observation` resources from a given FHIR bundle based on a list of observation references.
 * @param report - The lab report containing the results to be processed.
 * @param fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param mappings - An object containing paths to relevant fields within the FHIR resources.
 * @returns An array of `Observation` resources from the FHIR bundle that correspond to the
 * given references. If no matching observations are found or if the input references array is empty, an empty array
 * is returned.
 */
export const getObservations = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): Array<Observation> => {
  if (!report || !Array.isArray(report.result) || report.result.length === 0)
    return [];
  return report.result
    .map((obsRef) => {
      return (
        obsRef.reference &&
        evaluateReference(fhirBundle, mappings, obsRef.reference)
      );
    })
    .filter((obs) => obs);
};

/**
 * Retrieves the JSON representation of a lab report from the labs HTML string.
 * @param report - The LabReport object containing information about the lab report.
 * @param fhirBundle - The FHIR Bundle object containing relevant FHIR resources.
 * @param mappings - The PathMappings object containing mappings for extracting data.
 * @returns The JSON representation of the lab report.
 */
export const getLabJsonObject = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): TableJson => {
  // Get reference value (result ID) from Observations
  const observations = getObservations(report, fhirBundle, mappings);
  const observationRefValsArray = observations.flatMap((observation) => {
    const refVal = evaluate(observation, mappings["observationReferenceValue"]);
    return extractNumbersAndPeriods(refVal);
  });
  const observationRefVal = [...new Set(observationRefValsArray)].join(", "); // should only be 1

  // Get lab reports HTML String (for all lab reports) & convert to JSON
  const labsString = evaluate(fhirBundle, mappings["labResultDiv"])[0].div;
  const labsJson = formatTablesToJSON(labsString);

  // Get specified lab report (by reference value)
  return observationRefVal
    ? labsJson.filter((obj) => obj.resultId?.includes(observationRefVal))[0]
    : ({} as TableJson);
};

/**
 * Checks whether the result name of a lab report includes the term "abnormal"
 * @param labReportJson - A JSON object representing the lab report HTML string
 * @returns True if the result name includes "abnormal" (case insensitive), otherwise false. Will also return false if lab does not have JSON object.
 */
export const checkAbnormalTag = (labReportJson: TableJson): boolean => {
  if (!labReportJson) {
    return false;
  }
  const labResultName = labReportJson.resultName;

  return labResultName?.toLowerCase().includes("abnormal") ?? false;
};

/**
 * Recursively searches through a nested array of objects to find values associated with a specified search key.
 * @param result - The array of objects to search through.
 * @param searchKey - The key to search for within the objects.
 * @returns - A comma-separated string containing unique search key values.
 * @example result - JSON object that contains the tables for all lab reports
 * @example searchKey - Ex. "Analysis Time" or the field that we are searching data for.
 */
export function searchResultRecord(result: any[], searchKey: string) {
  let resultsArray: any[] = [];

  // Loop through each table
  for (const table of result) {
    // For each table, recursively search through all nodes
    if (Array.isArray(table)) {
      const nestedResult: string = searchResultRecord(table, searchKey);
      if (nestedResult) {
        return nestedResult;
      }
    } else {
      const keys = Object.keys(table);
      let searchKeyValue: string = "";
      keys.forEach((key) => {
        // Search for search key value
        if (key === searchKey && table[key].hasOwnProperty("value")) {
          searchKeyValue = table[key]["value"];
        }
      });

      if (searchKeyValue !== "") {
        resultsArray.push(searchKeyValue);
      }
    }
  }
  return [...new Set(resultsArray)].join(", ");
}

/**
 * Extracts and consolidates the specimen source descriptions from observations within a lab report.
 * @param report - The lab report containing the results to be processed.
 * @param fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param mappings - An object containing paths to relevant fields within the FHIR resources.
 * @returns A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnSpecimenSource = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.ReactNode => {
  const observations = getObservations(report, fhirBundle, mappings);
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
 * @param report - The lab report containing the results to be processed.
 * @param fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param mappings - An object containing paths to relevant fields within the FHIR resources.
 * @returns A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnCollectionTime = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.ReactNode => {
  const observations = getObservations(report, fhirBundle, mappings);
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
 * @param report - The lab report containing the results to be processed.
 * @param fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param mappings - An object containing paths to relevant fields within the FHIR resources.
 * @returns A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnReceivedTime = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.ReactNode => {
  const observations = getObservations(report, fhirBundle, mappings);
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
 * @param labReportJson - A JSON object representing the lab report HTML string
 * @param fieldName - A string containing the field name for which the value is being searched.
 * @returns A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
export const returnFieldValueFromLabHtmlString = (
  labReportJson: TableJson,
  fieldName: string,
): React.ReactNode => {
  if (!labReportJson) {
    return noData;
  }
  const labTables = labReportJson.tables;
  const fieldValue = searchResultRecord(labTables ?? [], fieldName);

  if (!fieldValue || fieldValue.length === 0) {
    return noData;
  }

  return fieldValue;
};

/**
 * Extracts and formats the analysis date/time(s) from within a lab report (sourced from HTML string).
 * @param labReportJson - A JSON object representing the lab report HTML string
 * @param fieldName - A string containing the field name for Analysis Time
 * @returns A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnAnalysisTime = (
  labReportJson: TableJson,
  fieldName: string,
): React.ReactNode => {
  const fieldVals = returnFieldValueFromLabHtmlString(labReportJson, fieldName);

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
 * @param report - The DiagnosticReport containing observations to be evaluated.
 * @param fhirBundle - The FHIR bundle containing observation data.
 * @param mappings - An object containing the FHIR path mappings.
 * @param columnInfo - An array of column information objects specifying column names and information paths.
 * @returns The JSX representation of the evaluated observation table, or undefined if there are no observations.
 */
export function evaluateObservationTable(
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
  columnInfo: ColumnInfoInput[],
): React.JSX.Element | undefined {
  const observations: Observation[] = (
    report.result?.map((obsRef: Reference) =>
      evaluateReference(fhirBundle, mappings, obsRef.reference ?? ""),
    ) ?? []
  ).filter((observation) => !observation.component);
  let obsTable;
  if (observations?.length > 0) {
    return (
      <EvaluateTable
        resources={observations}
        mappings={mappings}
        columns={columnInfo}
        outerBorder={false}
      />
    );
  }
  return obsTable;
}

/**
 * Evaluates diagnostic report data and generates the lab observations for each report.
 * @param labReportJson - A JSON object representing the lab report HTML string
 * @param report - An object containing an array of result references.
 * @param fhirBundle - The FHIR bundle containing diagnostic report data.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns - An array of React elements representing the lab observations.
 */
export const evaluateDiagnosticReportData = (
  labReportJson: TableJson,
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Component", infoPath: "observationComponent" },
    { columnName: "Value", infoPath: "observationValue" },
    { columnName: "Ref Range", infoPath: "observationReferenceRange" },
    {
      columnName: "Test Method",
      value: returnFieldValueFromLabHtmlString(
        labReportJson,
        "Test Method",
      ) as string,
    },
    {
      columnName: "Lab Comment",
      infoPath: "observationNote",
      hiddenBaseText: "comment",
    },
  ];
  return evaluateObservationTable(report, fhirBundle, mappings, columnInfo);
};

/**
 * Evaluates lab organisms data and generates a lab table for each report.
 * @param report - An object containing an array of lab result references. If it exists, one of the Observations in the report will contain all the lab organisms table data.
 * @param fhirBundle - The FHIR bundle containing diagnostic report data.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns - An array of React elements representing the lab organisms table.
 */
export const evaluateOrganismsReportData = (
  report: LabReport,
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  let components: ObservationComponent[] = [];
  let observation: Observation | undefined;

  report.result?.find((obsRef: Reference) => {
    const obs: Observation = evaluateReference(
      fhirBundle,
      mappings,
      obsRef.reference ?? "",
    );
    if (obs.component) {
      observation = obs;
      return true;
    }
    return false;
  });

  if (observation === undefined) {
    return undefined;
  }
  components = observation.component!;
  const columnInfo: ColumnInfoInput[] = [
    {
      columnName: "Organism",
      value: evaluateValue(observation, mappings["observationOrganism"]),
    },
    { columnName: "Antibiotic", infoPath: "observationAntibiotic" },
    { columnName: "Method", infoPath: "observationOrganismMethod" },
    { columnName: "Susceptibility", infoPath: "observationSusceptibility" },
  ];

  return (
    <EvaluateTable
      resources={components}
      mappings={mappings}
      columns={columnInfo}
      outerBorder={false}
    />
  );
};

/**
 * Evaluates lab information and RR data from the provided FHIR bundle and mappings.
 * @param fhirBundle - The FHIR bundle containing lab and RR data.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns An array of the Diagnostic reports Elements and Organization Display Data
 */
export const evaluateLabInfoData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
): LabReportElementData[] => {
  const labReports = evaluate(fhirBundle, mappings["diagnosticReports"]);
  // the keys are the organization id, the value is an array of jsx elements of diagnsotic reports
  let organizationElements: ResultObject = {};

  labReports.map((report) => {
    const labReportJson = getLabJsonObject(report, fhirBundle, mappings);
    const labTableDiagnostic = evaluateDiagnosticReportData(
      labReportJson,
      report,
      fhirBundle,
      mappings,
    );
    const labTableOrganisms = evaluateOrganismsReportData(
      report,
      fhirBundle,
      mappings,
    );
    const rrInfo: DisplayDataProps[] = [
      {
        title: "Analysis Time",
        value: returnAnalysisTime(labReportJson, "Analysis Time"),
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
          labReportJson,
          "Anatomical Location / Laterality",
        ),
        className: "lab-text-content",
      },
      {
        title: "Collection Method/Volume",
        value: returnFieldValueFromLabHtmlString(
          labReportJson,
          "Collection Method / Volume",
        ),
        className: "lab-text-content",
      },
      {
        title: "Resulting Agency Comment",
        value: returnFieldValueFromLabHtmlString(
          labReportJson,
          "Resulting Agency Comment",
        ),
        className: "lab-text-content",
      },
      {
        title: "Authorizing Provider",
        value: returnFieldValueFromLabHtmlString(
          labReportJson,
          "Authorizing Provider",
        ),
        className: "lab-text-content",
      },
      {
        title: "Result Type",
        value: returnFieldValueFromLabHtmlString(labReportJson, "Result Type"),
        className: "lab-text-content",
      },
      {
        title: "Narrative",
        value: returnFieldValueFromLabHtmlString(labReportJson, "Narrative"),
        className: "lab-text-content",
      },
    ];
    const content: Array<React.JSX.Element> = [];
    if (labTableDiagnostic)
      content.push(
        <React.Fragment key={"lab-table-diagnostic"}>
          {labTableDiagnostic}
        </React.Fragment>,
      );
    if (labTableOrganisms) {
      content.push(
        <React.Fragment key={"lab-table-oragnisms"}>
          {labTableOrganisms}
        </React.Fragment>,
      );
    }
    content.push(
      ...rrInfo.map((item) => {
        return <DataDisplay key={`${item.title}-${item.value}`} item={item} />;
      }),
    );
    const organizationId = (report.performer?.[0].reference ?? "").replace(
      "Organization/",
      "",
    );
    const element = (
      <AccordionLabResults
        key={report.id}
        title={report.code.coding[0].display}
        abnormalTag={checkAbnormalTag(labReportJson)}
        content={content}
        organizationId={organizationId}
      />
    );
    organizationElements = groupElementByOrgId(
      organizationElements,
      organizationId,
      element,
    );
  });
  return combineOrgAndReportData(organizationElements, fhirBundle, mappings);
};

/**
 * Combines the org display data with the diagnostic report elements
 * @param organizationElements - Object contianing the keys of org data, values of the diagnostic report elements
 * @param fhirBundle - The FHIR bundle containing lab and RR data.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns An array of the Diagnostic reports Elements and Organization Display Data
 */
export const combineOrgAndReportData = (
  organizationElements: ResultObject,
  fhirBundle: Bundle,
  mappings: PathMappings,
): LabReportElementData[] => {
  return Object.keys(organizationElements).map((key: string) => {
    const organizationId = key.replace("Organization/", "");
    const orgData = evaluateLabOrganizationData(
      organizationId,
      fhirBundle,
      mappings,
      organizationElements[key].length,
    );
    return {
      organizationId: organizationId,
      diagnosticReportDataElements: organizationElements[key],
      organizationDisplayDataProps: orgData,
    };
  });
};

/**
 * Finds the Orgnization that matches the id and creates a DisplayDataProps array
 * @param id - id of the organization
 * @param fhirBundle - The FHIR bundle containing lab and RR data.
 * @param mappings - An object containing the FHIR path mappings.
 * @param labReportCount - A number representing the amount of lab reports for a specific organization
 * @returns The organization display data as an array
 */
export const evaluateLabOrganizationData = (
  id: string,
  fhirBundle: Bundle,
  mappings: PathMappings,
  labReportCount: number,
) => {
  const orgMappings = evaluate(fhirBundle, mappings["organizations"]);
  const matchingOrg: Organization = orgMappings.filter(
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

  const contactInfo = formatPhoneNumber(matchingOrg?.telecom?.[0].value ?? "");
  const name = matchingOrg?.name ?? "";
  const matchingOrgData: DisplayDataProps[] = [
    { title: "Lab Performing Name", value: name },
    { title: "Lab Address", value: formattedAddress },
    { title: "Lab Contact", value: contactInfo },
    { title: "Number of Results", value: labReportCount },
  ];
  return matchingOrgData;
};

/**
 * Groups a JSX element under a specific organization ID within a result object. If the organization ID
 * already exists in the result object, the element is added to the existing array. If the organization ID
 * does not exist, a new array is created for that ID and the element is added to it.
 * @param resultObject - An object that accumulates grouped elements, where each key is an
 *   organization ID and its value is an array of JSX elements associated
 *   with that organization.
 * @param organizationId - The organization ID used to group the element. This ID determines the key
 *   under which the element is stored in the result object.
 * @param element - The JSX element to be grouped under the specified organization ID.
 * @returns The updated result object with the element added to the appropriate group.
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
  return resultObject;
};
