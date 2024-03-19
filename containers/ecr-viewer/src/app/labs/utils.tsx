import React from "react";
import { Bundle, Observation, Reference } from "fhir/r4";
import {
  PathMappings,
  CompleteData,
  DisplayData,
  DataDisplay,
  evaluateData,
} from "@/app/utils";
import { evaluate } from "fhirpath";
import { AccordionLabResults } from "@/app/view-data/components/AccordionLabResults";
import { formatDateTime, formatTablesToJSON } from "@/app/format-service";

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
const getObservations = (
  observationIds: Array<Reference>,
  fhirBundle: Bundle,
): Array<Observation> => {
  const ids: Array<string> = observationIds
    .map((id) => {
      return id.reference?.replace("Observation/", "");
    })
    .filter((i): i is string => i !== undefined);

  if (ids.length === 0) return [];

  return ids.map((id) => {
    return evaluate(fhirBundle, `Bundle.entry.resource.where(id = '${id}')`)[0];
  });
};

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
 * Extracts and formats the analysis time(s) from components within a lab report.
 *
 * @param {Bundle} fhirBundle - The FHIR bundle containing related resources for the lab report.
 * @param {PathMappings} mappings - An object containing paths to relevant fields within the FHIR resources.
 * @returns {React.ReactNode} A comma-separated string of unique collection times, or a 'No data' JSX element if none are found.
 */
const returnAnalysisTime = (
  fhirBundle: Bundle,
  mappings: PathMappings,
): React.ReactNode => {
  const labResultString = evaluate(fhirBundle, mappings["labResultDiv"])[0].div;
  const labResultJson = formatTablesToJSON(labResultString);
  console.log("LAB RESULT JSON: ", labResultJson);

  const analysisTime = labResultJson.map((result) => {
    return result["Analysis Time"];
  });

  if (!analysisTime || analysisTime.length === 0) {
    return noData;
  }

  return [...new Set(analysisTime)].join(", ");
};

// const returnAnatomicalLocation = (
//   fhirBundle: Bundle,
//   mappings: PathMappings,
// ): React.ReactNode => {
//   const labResultString = evaluate(fhirBundle, mappings["labResultDiv"])[0].div;
//   const labResultJson = formatTablesToJSON(labResultString);
//   console.log("labResultJson: ", labResultJson);

//   const analysisTime = labResultJson.map((result) => {
//     return result["Analysis Time"];
//   });

//   if (!analysisTime || analysisTime.length === 0) {
//     return noData;
//   }

//   return [...new Set(analysisTime)].join(", ");
// };

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
    const rrInfo: DisplayData[] = [
      {
        title: "Analysis Time",
        value: returnAnalysisTime(fhirBundle, mappings),
      },
      {
        title: "Collection Time",
        value: returnCollectionTime(report, fhirBundle, mappings),
      },
      {
        title: "Received Time",
        value: returnReceivedTime(report, fhirBundle, mappings),
      },
      {
        title: "Specimen (Source)",
        value: returnSpecimenSource(report, fhirBundle, mappings),
      },
      {
        title: "Anatomical Location/Laterality",
        value: "TBD",
      },
    ];
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
