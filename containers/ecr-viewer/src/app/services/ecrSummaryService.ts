import { Bundle } from "fhir/r4";
import { PathMappings } from "@/app/utils";
import {
  formatDate,
  formatStartEndDateTime,
} from "@/app/services/formatService";
import { evaluate } from "@/app/view-data/utils/evaluate";
import {
  evaluatePatientName,
  evaluatePatientContactInfo,
  evaluatePatientAddress,
  evaluateFacilityAddress,
} from "./evaluateFhirDataService";
import { evaluateClinicalData } from "../view-data/components/common";
import { DisplayDataProps } from "../DataDisplay";

/**
 * Evaluates and retrieves patient details from the FHIR bundle using the provided path mappings.
 * @param fhirBundle - The FHIR bundle containing patient data.
 * @param fhirPathMappings - Object containing fhir path mappings.
 * @returns An array of patient details objects containing title and value pairs.
 */
export const evaluateEcrSummaryPatientDetails = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  return [
    {
      title: "Patient Name",
      value: evaluatePatientName(fhirBundle, fhirPathMappings),
    },
    {
      title: "DOB",
      value:
        formatDate(evaluate(fhirBundle, fhirPathMappings.patientDOB)[0]) || "",
    },
    {
      title: "Patient Address",
      value: evaluatePatientAddress(fhirBundle, fhirPathMappings),
    },
    {
      title: "Patient Contact",
      value: evaluatePatientContactInfo(fhirBundle, fhirPathMappings),
    },
  ];
};

/**
 * Evaluates and retrieves encounter details from the FHIR bundle using the provided path mappings.
 * @param fhirBundle - The FHIR bundle containing patient data.
 * @param fhirPathMappings - Object containing fhir path mappings.
 * @returns An array of encounter details objects containing title and value pairs.
 */
export const evaluateEcrSummaryEncounterDetails = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  return [
    {
      title: "Facility Name",
      value: evaluate(fhirBundle, fhirPathMappings.facilityName),
    },
    {
      title: "Facility Address",
      value: evaluateFacilityAddress(fhirBundle, fhirPathMappings),
    },
    {
      title: "Facility Contact",
      value: evaluate(fhirBundle, fhirPathMappings.facilityContact),
    },
    {
      title: "Encounter Date/Time",
      value: evaluateEncounterDate(fhirBundle, fhirPathMappings),
    },
    {
      title: "Encounter Type",
      value: evaluate(fhirBundle, fhirPathMappings.encounterType),
    },
  ];
};

/**
 * Evaluates and retrieves condition details from the FHIR bundle using the provided path mappings.
 * @param fhirBundle - The FHIR bundle containing patient data.
 * @param fhirPathMappings - Object containing fhir path mappings.
 * @returns An array of condition details objects containing title and value pairs.
 */
export const evaluateEcrSummaryAboutTheConditionDetails = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  return [
    {
      title: "Reportable Condition",
      toolTip:
        "Condition that caused this eCR to be sent to your jurisdiction.",
      value: evaluate(fhirBundle, fhirPathMappings.rrDisplayNames)[0],
    },
    {
      title: "RCKMS Rule Summary",
      toolTip:
        "Reason(s) that this eCR was sent for this condition. Corresponds to your jurisdiction's rules for routing eCRs in RCKMS (Reportable Condition Knowledge Management System).",
      value: evaluate(fhirBundle, fhirPathMappings.rckmsTriggerSummaries)[0],
    },
  ];
};

/**
 * Evaluates and retrieves relevant clinical details from the FHIR bundle using the provided SNOMED code and path mappings.
 * @param fhirBundle - The FHIR bundle containing patient data.
 * @param fhirPathMappings - Object containing fhir path mappings.
 * @param snomedCode - String containing the SNOMED code search parameter.
 * @returns An array of condition details objects containing title and value pairs.
 */
export const evaluateEcrSummaryRelevantClinicalDetails = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
  snomedCode: string,
) => {
  const noData: string = "No matching clinical data found in this eCR";
  let resultsArray: DisplayDataProps[] = [];
  const clinicalData = evaluateClinicalData(
    fhirBundle,
    fhirPathMappings,
    snomedCode,
  );
  console.log("Clinical Data", clinicalData);

  // * PROBLEMS LIST
  const problemsList = clinicalData.activeProblemsDetails.availableData;
  if (problemsList.length > 0) {
    resultsArray.push({ value: problemsList[0].value, dividerLine: false });
  }

  // * PLANNED PROCEDURES ONLY
  const plannedProcedures = clinicalData.treatmentData.availableData.filter(
    (entry) => entry.title === "Planned Procedures",
  );
  if (plannedProcedures.length > 0) {
    resultsArray.push({
      value: plannedProcedures[0].value,
      dividerLine: false,
    });
  }

  // * IMMUNIZATIONS
  const immunizations = clinicalData.immunizationsDetails.availableData;
  if (immunizations.length > 0) {
    resultsArray.push({
      value: immunizations[0].value,
      dividerLine: false,
    });
  }

  // * If no data, return noData
  if (resultsArray.length === 0) {
    console.log("No relevant clinical results");
    resultsArray.push({ value: noData, dividerLine: false });
  }

  resultsArray.push({ dividerLine: true });
  return resultsArray;
};

/**
 * Evaluates encounter date from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing encounter date.
 * @param mappings - The object containing the fhir paths.
 * @returns A string of start date - end date.
 */
const evaluateEncounterDate = (fhirBundle: Bundle, mappings: PathMappings) => {
  return formatStartEndDateTime(
    evaluate(fhirBundle, mappings.encounterStartDate).join(""),
    evaluate(fhirBundle, mappings.encounterEndDate).join(""),
  );
};
