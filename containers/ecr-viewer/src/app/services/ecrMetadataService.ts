import {
  formatAddress,
  formatContactPoint,
  formatDateTime,
} from "@/app/services/formatService";
import { PathMappings, evaluateData } from "@/app/utils";
import { Bundle, Organization } from "fhir/r4";
import { evaluate } from "@/app/view-data/utils/evaluate";
import {
  evaluateFacilityAddress,
  evaluateReference,
  evaluateFacilityId,
} from "./evaluateFhirDataService";
import { DisplayDataProps } from "@/app/DataDisplay";

export interface ReportableConditions {
  [condition: string]: {
    [trigger: string]: Set<string>;
  };
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
  const custodianRef = evaluate(fhirBundle, mappings.eicrCustodianRef)[0] ?? "";
  const custodian = evaluateReference(
    fhirBundle,
    mappings,
    custodianRef,
  ) as Organization;

  const eicrDetails: DisplayDataProps[] = [
    {
      title: "eICR Identifier",
      toolTip:
        "Unique document ID for the eICR that originates from the medical record. Different from the Document ID that NBS creates for all incoming records.",
      value: evaluate(fhirBundle, mappings.eicrIdentifier)[0],
    },
    {
      title: "Document Author",
      value: custodian?.name,
    },
    {
      title: "Author Address",
      value: formatAddress(
        custodian?.address?.[0].line ?? [],
        custodian?.address?.[0].city ?? "",
        custodian?.address?.[0].state ?? "",
        custodian?.address?.[0].postalCode ?? "",
        custodian?.address?.[0].country ?? "",
      ),
    },
    {
      title: "Author Contact",
      value: formatContactPoint(custodian?.telecom).join("\n"),
    },
  ];
  const ecrSenderDetails: DisplayDataProps[] = [
    {
      title: "Date/Time eCR Created",
      value: formatDateTime(
        evaluate(fhirBundle, mappings.dateTimeEcrCreated)[0],
      ),
    },
    {
      title: "Sender Software",
      toolTip: "EHR system used by the sending provider.",
      value: evaluate(fhirBundle, mappings.senderSoftware)[0],
    },
    {
      title: "Sender Facility Name",
      value: evaluate(fhirBundle, mappings.senderFacilityName)[0],
    },
    {
      title: "Facility Address",
      value: evaluateFacilityAddress(fhirBundle, mappings),
    },
    {
      title: "Facility Contact",
      value: evaluate(fhirBundle, mappings.facilityContact)[0],
    },
    {
      title: "Facility ID",
      value: evaluateFacilityId(fhirBundle, mappings),
    },
  ];
  return {
    eicrDetails: evaluateData(eicrDetails),
    ecrSenderDetails: evaluateData(ecrSenderDetails),
    rrDetails: reportableConditionsList,
  };
};
