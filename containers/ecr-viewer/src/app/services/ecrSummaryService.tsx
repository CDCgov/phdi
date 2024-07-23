import { Bundle, Condition, Extension, Observation } from "fhir/r4";
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
import { DisplayDataProps } from "@/app/DataDisplay";
import { returnProblemsTable } from "@/app/view-data/components/common";
import { LabReport, evaluateLabInfoData } from "./labsService";

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
 * @param snomedCode - The SNOMED code identifying which Reportable Condition should be displayed.
 * @returns An array of condition details objects containing title and value pairs.
 */
export const evaluateEcrSummaryAboutTheConditionDetails = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
  snomedCode?: string,
): DisplayDataProps[] => {
  const rrArray: Observation[] = evaluate(
    fhirBundle,
    fhirPathMappings.rrDetails,
  );
  let conditionDisplayName: Set<string> = new Set();
  let ruleSummary: Set<string> = new Set();
  if (snomedCode) {
    rrArray.forEach((obs) => {
      const coding = obs.valueCodeableConcept?.coding?.find(
        (coding) => coding.code === snomedCode,
      );
      if (coding) {
        if (coding.display) {
          conditionDisplayName.add(coding.display);
        }
        obs.extension?.forEach((extension) => {
          if (
            extension.url ===
              "http://hl7.org/fhir/us/ecr/StructureDefinition/us-ph-determination-of-reportability-rule-extension" &&
            extension?.valueString?.trim()
          ) {
            ruleSummary.add(extension.valueString.trim());
          }
        });
      }
    });
  }
  if (conditionDisplayName.size === 0) {
    const names = evaluate(fhirBundle, fhirPathMappings.rrDisplayNames);
    let summaries = evaluate(
      fhirBundle,
      fhirPathMappings.rckmsTriggerSummaries,
    );
    conditionDisplayName = new Set([...names]);
    ruleSummary = new Set([...summaries]);
  }
  return [
    {
      title: "Reportable Condition",
      toolTip:
        "Condition that caused this eCR to be sent to your jurisdiction.",
      value: (
        <div className={"p-list"}>
          {[...conditionDisplayName].map((displayName) => (
            <p key={displayName}>{displayName}</p>
          ))}
        </div>
      ),
    },
    {
      title: "RCKMS Rule Summary",
      toolTip:
        "Reason(s) that this eCR was sent for this condition. Corresponds to your jurisdiction's rules for routing eCRs in RCKMS (Reportable Condition Knowledge Management System).",
      value: (
        <div className={"p-list"}>
          {[...ruleSummary].map((summary) => (
            <p key={summary}>{summary}</p>
          ))}
        </div>
      ),
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
 * @returns An array of lab result details objects containing title and value pairs.
 */
export const evaluateEcrSummaryRelevantLabResults = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
  snomedCode: string,
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
  );

  resultsArray = relevantLabElements.flatMap((element) =>
    element.diagnosticReportDataElements.map((reportElement) => ({
      value: reportElement,
      dividerLine: false,
    })),
  );

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
