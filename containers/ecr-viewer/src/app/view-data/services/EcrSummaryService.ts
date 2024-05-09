import { Bundle } from "fhir/r4";
import {
  evaluateEncounterDate,
  evaluatePatientContactInfo,
  evaluatePatientName,
  extractFacilityAddress,
  extractPatientAddress,
  PathMappings,
} from "@/app/utils";
import { formatDate } from "@/app/formatService";
import { evaluate } from "fhirpath";

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
      value: extractPatientAddress(fhirBundle, fhirPathMappings),
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
      value: extractFacilityAddress(fhirBundle, fhirPathMappings),
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
