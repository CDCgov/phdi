import { formatDateTime } from "@/app/services/formatService";
import { PathMappings, evaluateData } from "@/app/view-data/utils/utils";
import { Bundle } from "fhir/r4";
import { evaluate } from "@/app/view-data/utils/evaluate";
import { DisplayDataProps } from "@/app/view-data/components/DataDisplay";

export interface ReportableConditions {
  [condition: string]: {
    [trigger: string]: Set<string>;
  };
}

export interface ERSDWarning {
  warning: string;
  versionUsed: string;
  expectedVersion: string;
  suggestedSolution: string;
}

/**
 * Evaluates eCR metadata from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing eCR metadata.
 * @param mappings - The object containing the fhir paths.
 * @returns An object containing evaluated and formatted eCR metadata.
 */
export const evaluateEcrMetadata = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const rrDetails = evaluate(fhirBundle, mappings.rrDetails);

  let reportableConditionsList: ReportableConditions = {};

  for (const condition of rrDetails) {
    let name = condition.valueCodeableConcept.coding[0].display;
    const triggers = condition.extension
      .filter(
        (x: { url: string; valueString: string }) =>
          x.url ===
          "http://hl7.org/fhir/us/ecr/StructureDefinition/us-ph-determination-of-reportability-rule-extension",
      )
      .map((x: { url: string; valueString: string }) => x.valueString);
    if (!reportableConditionsList[name]) {
      reportableConditionsList[name] = {};
    }

    for (let i in triggers) {
      if (!reportableConditionsList[name][triggers[i]]) {
        reportableConditionsList[name][triggers[i]] = new Set();
      }
      condition.performer
        .map((x: { display: string }) => x.display)
        .forEach((x: string) =>
          reportableConditionsList[name][triggers[i]].add(x),
        );
    }
  }

  const eicrReleaseVersion = (fhirBundle: any, mappings: any) => {
    const releaseVersion = evaluate(fhirBundle, mappings.eicrReleaseVersion)[0];
    console.log(releaseVersion);
    if (releaseVersion === "2016-12-01") {
      return "R1.1 (2016-12-01)";
    } else if (releaseVersion === "2021-01-01") {
      return "R3.1 (2021-01-01)";
    } else {
      return releaseVersion;
    }
  };

  const eRSDwarnings = evaluate(fhirBundle, mappings.eRSDwarnings);
  let eRSDtext: ERSDWarning[] = [];

  for (const warning of eRSDwarnings) {
    if (warning.code == "RRVS34") {
      eRSDtext.push({
        warning:
          "Sending organization is using an malformed eRSD (RCTC) version",
        versionUsed: "2020-06-23",
        expectedVersion:
          "Sending organization should be using one of the following: 2023-10-06, 1.2.2.0, 3.x.x.x.",
        suggestedSolution:
          "The trigger code version your organization is using could not be determined. The trigger codes may be out date. Please have your EHR administrators update the version format for complete eCR functioning.",
      });
    } else if (warning.code == "RRVS29") {
      eRSDtext.push({
        warning:
          "Sending organization is using an outdated eRSD (RCTC) version",
        versionUsed: "2020-06-23",
        expectedVersion:
          "Sending organization should be using one of the following: 2023-10-06, 1.2.2.0, 3.x.x.x.",
        suggestedSolution:
          "The trigger code version your organization is using is out-of-date. Please have your EHR administration install the current version for complete eCR functioning.",
      });
    }
  }

  const eicrDetails: DisplayDataProps[] = [
    {
      title: "eICR Identifier",
      toolTip:
        "Unique document ID for the eICR that originates from the medical record. Different from the Document ID that NBS creates for all incoming records.",
      value: evaluate(fhirBundle, mappings.eicrIdentifier)[0],
    },
    {
      title: "Date/Time eCR Created",
      value: formatDateTime(
        evaluate(fhirBundle, mappings.dateTimeEcrCreated)[0],
      ),
    },
    {
      title: "eICR Release Version",
      value: eicrReleaseVersion(fhirBundle, mappings),
    },
    {
      title: "EHR Software Name",
      toolTip: "EHR system used by the sending provider.",
      value: evaluate(fhirBundle, mappings.ehrSoftware)[0],
    },
    {
      title: "EHR Manufacturer Model Name",
      value: evaluate(fhirBundle, mappings.ehrManufacturerModel)[0],
    },
  ];
  return {
    eicrDetails: evaluateData(eicrDetails),
    rrDetails: reportableConditionsList,
    eRSDwarnings: eRSDtext,
  };
};
