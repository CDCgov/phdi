import { Bundle, Condition, Extension, Observation } from "fhir/r4";
import { evaluateData, PathMappings } from "@/app/view-data/utils/utils";
import {
  formatDate,
  formatStartEndDateTime,
} from "@/app/services/formatService";
import { evaluate } from "@/app/view-data/utils/evaluate";
import {
  evaluatePatientName,
  evaluatePatientContactInfo,
  evaluatePatientAddress,
} from "./evaluateFhirDataService";
import { DisplayDataProps } from "@/app/view-data/components/DataDisplay";
import { returnProblemsTable } from "@/app/view-data/components/common";
import { LabReport, evaluateLabInfoData } from "./labsService";
import { ConditionSummary } from "@/app/view-data/components/EcrSummary";
import React from "react";

/**
 * ExtensionConditionCode extends the FHIR Extension interface to include a 'coding' property.
 * This property aligns with the CDC's ReportStream specifications for condition
 * to code mappings, using 'coding.code' for descriptive names of testing methods.
 *
 * Refer to the ReportStream documentation for details:
 * https://github.com/CDCgov/prime-reportstream/blob/master/prime-router/docs/design/0023-condition-to-code-mapping.md
 */
interface ExtensionConditionCode extends Extension {
  coding?: { code: string; system: string }[];
}

interface ConditionStamped extends Condition {
  extension?: ExtensionConditionCode[];
}

interface LabReportStamped extends LabReport {
  id: string;
  extension?: ExtensionConditionCode[];
}

interface ObservationStamped extends Observation {
  extension?: ExtensionConditionCode[];
}

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
  return evaluateData([
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
      title: "Sex",
      value: evaluate(fhirBundle, fhirPathMappings.patientGender)[0],
    },
    {
      title: "Patient Address",
      value: evaluatePatientAddress(fhirBundle, fhirPathMappings),
    },
    {
      title: "Patient Contact",
      value: evaluatePatientContactInfo(fhirBundle, fhirPathMappings),
    },
  ]);
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
  return evaluateData([
    {
      title: "Encounter Date/Time",
      value: evaluateEncounterDate(fhirBundle, fhirPathMappings),
    },
    {
      title: "Encounter Type",
      value: evaluate(fhirBundle, fhirPathMappings.encounterType),
    },
    {
      title: "Facility Name",
      value: evaluate(fhirBundle, fhirPathMappings.facilityName),
    },
    {
      title: "Facility Contact",
      value: evaluate(fhirBundle, fhirPathMappings.facilityContact),
    },
  ]);
};

/**
 * Finds all unique RCKMS rule summaries in an observation
 * @param observation - FHIR Observation
 * @returns Set of rule summaries
 */
const evaluateRuleSummaries = (observation: Observation): Set<string> => {
  const ruleSummaries = new Set<string>();
  observation.extension?.forEach((extension) => {
    if (
      extension.url ===
        "http://hl7.org/fhir/us/ecr/StructureDefinition/us-ph-determination-of-reportability-rule-extension" &&
      extension?.valueString?.trim()
    ) {
      ruleSummaries.add(extension.valueString.trim());
    }
  });
  return ruleSummaries;
};

/**
 * Evaluates and retrieves all condition details in a bundle.
 * @param fhirBundle - The FHIR bundle containing patient data.
 * @param fhirPathMappings - Object containing fhir path mappings.
 * @param snomedCode - The SNOMED code identifying the main snomed code.
 * @returns An array of condition summary objects.
 */
export const evaluateEcrSummaryConditionSummary = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
  snomedCode?: string,
): ConditionSummary[] => {
  const rrArray: Observation[] = evaluate(
    fhirBundle,
    fhirPathMappings.rrDetails,
  );
  const conditionsList: {
    [index: string]: { ruleSummaries: Set<string>; snomedDisplay: string };
  } = {};
  for (const observation of rrArray) {
    const coding = observation?.valueCodeableConcept?.coding?.find(
      (coding) => coding.system === "http://snomed.info/sct",
    );
    if (coding?.code) {
      const snomed = coding.code;
      if (!conditionsList[snomed]) {
        conditionsList[snomed] = {
          ruleSummaries: new Set(),
          snomedDisplay: coding.display!,
        };
      }

      evaluateRuleSummaries(observation).forEach((ruleSummary) =>
        conditionsList[snomed].ruleSummaries.add(ruleSummary),
      );
    }
  }

  const conditionSummaries: ConditionSummary[] = [];
  for (let conditionsListKey in conditionsList) {
    const conditionSummary = {
      title: conditionsList[conditionsListKey].snomedDisplay,
      snomed: conditionsListKey,
      conditionDetails: [
        {
          title: "RCKMS Rule Summary",
          toolTip:
            "Reason(s) that this eCR was sent for this condition. Corresponds to your jurisdiction's rules for routing eCRs in RCKMS (Reportable Condition Knowledge Management System).",
          value: (
            <div className={"p-list"}>
              {[...conditionsList[conditionsListKey].ruleSummaries].map(
                (summary) => (
                  <p key={summary}>{summary}</p>
                ),
              )}
            </div>
          ),
        },
      ],
      clinicalDetails: evaluateEcrSummaryRelevantClinicalDetails(
        fhirBundle,
        fhirPathMappings,
        conditionsListKey,
      ),
      labDetails: evaluateEcrSummaryRelevantLabResults(
        fhirBundle,
        fhirPathMappings,
        conditionsListKey,
        false,
      ),
    };

    if (conditionSummary.snomed === snomedCode) {
      conditionSummaries.unshift(conditionSummary);
    } else {
      conditionSummaries.push(conditionSummary);
    }
  }

  return conditionSummaries;
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
): DisplayDataProps[] => {
  const noData: string = "No matching clinical data found in this eCR";
  if (!snomedCode) {
    return [{ value: noData, dividerLine: true }];
  }

  const problemsList: ConditionStamped[] = evaluate(
    fhirBundle,
    fhirPathMappings["activeProblems"],
  );
  const problemsListFiltered = problemsList.filter((entry) =>
    entry.extension?.some(
      (ext) =>
        ext.url ===
          "https://reportstream.cdc.gov/fhir/StructureDefinition/condition-code" &&
        ext.coding?.some((item) => item.code === snomedCode),
    ),
  );

  if (problemsListFiltered.length === 0) {
    return [{ value: noData, dividerLine: true }];
  }

  const problemsElement = returnProblemsTable(
    fhirBundle,
    problemsListFiltered as Condition[],
    fhirPathMappings,
  );

  return [{ value: problemsElement, dividerLine: true }];
};

/**
 * Evaluates and retrieves relevant lab results from the FHIR bundle using the provided SNOMED code and path mappings.
 * @param fhirBundle - The FHIR bundle containing patient data.
 * @param fhirPathMappings - Object containing fhir path mappings.
 * @param snomedCode - String containing the SNOMED code search parameter.
 * @param lastDividerLine - Boolean to determine if a divider line should be added to the end of the lab results. Default to true
 * @returns An array of lab result details objects containing title and value pairs.
 */
export const evaluateEcrSummaryRelevantLabResults = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
  snomedCode: string,
  lastDividerLine: boolean = true,
): DisplayDataProps[] => {
  const noData: string = "No matching lab results found in this eCR";
  let resultsArray: DisplayDataProps[] = [];

  if (!snomedCode) {
    return [{ value: noData, dividerLine: true }];
  }

  const labReports: LabReportStamped[] = evaluate(
    fhirBundle,
    fhirPathMappings["diagnosticReports"],
  );
  const labsWithCode = labReports.filter((entry) =>
    entry.extension?.some(
      (ext) =>
        ext.url ===
          "https://reportstream.cdc.gov/fhir/StructureDefinition/condition-code" &&
        ext.coding?.some((item) => item.code === snomedCode),
    ),
  );

  const obsIdsWithCode: (string | undefined)[] = (
    evaluate(
      fhirBundle,
      fhirPathMappings["observations"],
    ) as ObservationStamped[]
  )
    .filter((entry) =>
      entry.extension?.some(
        (ext) =>
          ext.url ===
            "https://reportstream.cdc.gov/fhir/StructureDefinition/condition-code" &&
          ext.coding?.some((item) => item.code === snomedCode),
      ),
    )
    .map((entry) => entry.id);

  const labsFromObsWithCode = (() => {
    const obsIds = new Set(obsIdsWithCode);
    const labsWithCodeIds = new Set(labsWithCode.map((lab) => lab.id));

    return labReports.filter((lab) => {
      if (labsWithCodeIds.has(lab.id)) {
        return false;
      }

      return lab.result.some((result) => {
        if (result.reference) {
          const referenceId = result.reference.replace(/^Observation\//, "");
          return obsIds.has(referenceId);
        }
      });
    });
  })();

  const relevantLabs = labsWithCode.concat(labsFromObsWithCode);

  if (relevantLabs.length === 0) {
    return [{ value: noData, dividerLine: true }];
  }
  const relevantLabElements = evaluateLabInfoData(
    fhirBundle,
    relevantLabs,
    fhirPathMappings,
    "h4",
  );

  resultsArray = relevantLabElements.flatMap((element) =>
    element.diagnosticReportDataElements.map((reportElement) => ({
      value: reportElement,
      dividerLine: false,
    })),
  );

  if (lastDividerLine) {
    resultsArray.push({ dividerLine: true });
  }
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
