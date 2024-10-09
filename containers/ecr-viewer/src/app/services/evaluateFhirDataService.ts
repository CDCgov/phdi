import {
  Bundle,
  CodeableConcept,
  Encounter,
  Identifier,
  Location,
  Organization,
  Practitioner,
  PractitionerRole,
  Quantity,
} from "fhir/r4";
import { evaluate } from "@/app/view-data/utils/evaluate";
import * as dateFns from "date-fns";
import { PathMappings, evaluateData } from "../view-data/utils/utils";
import {
  formatAddress,
  formatContactPoint,
  formatName,
  formatPhoneNumber,
  formatStartEndDateTime,
} from "./formatService";
import fhirpath_r4_model from "fhirpath/fhir-context/r4";
import { Element } from "fhir/r4";
import { DisplayDataProps } from "@/app/view-data/components/DataDisplay";

/**
 * Evaluates patient name from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing patient contact info.
 * @param mappings - The object containing the fhir paths.
 * @returns The formatted patient name
 */
export const evaluatePatientName = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const givenNames = evaluate(fhirBundle, mappings.patientGivenName).join(" ");
  const familyName = evaluate(fhirBundle, mappings.patientFamilyName);

  return `${givenNames} ${familyName}`;
};

/**
 * Evaluates the patient's race from the FHIR bundle and formats for display.
 * @param fhirBundle - The FHIR bundle containing patient contact info.
 * @param mappings - The object containing the fhir paths.
 * @returns - The patient's race information, including race OMB category and detailed extension (if available).
 */
export const evaluatePatientRace = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const raceCat = evaluate(fhirBundle, mappings.patientRace)[0];
  const raceDetailedExt =
    evaluate(fhirBundle, mappings.patinetRaceExtension)[0] ?? "";

  if (raceDetailedExt) {
    return `${raceCat}, ${raceDetailedExt}`;
  } else {
    return raceCat;
  }
};

/**
 * Evaluates patient address from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing patient contact info.
 * @param mappings - The object containing the fhir paths.
 * @returns The formatted patient address
 */
export const evaluatePatientAddress = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const streetAddresses = evaluate(fhirBundle, mappings.patientStreetAddress);
  const city = evaluate(fhirBundle, mappings.patientCity)[0];
  const state = evaluate(fhirBundle, mappings.patientState)[0];
  const zipCode = evaluate(fhirBundle, mappings.patientZipCode)[0];
  const country = evaluate(fhirBundle, mappings.patientCountry)[0];
  return formatAddress(streetAddresses, city, state, zipCode, country);
};

/**
 * Finds correct encounter ID
 * @param fhirBundle - The FHIR bundle containing encounter resources.
 * @param mappings - Path mappings for resolving references.
 * @returns Encounter ID or empty string if not available.
 */
export const evaluateEncounterId = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const encounterIDs = evaluate(fhirBundle, mappings.encounterID);
  const filteredIds = encounterIDs
    .filter((id) => /^\d+$/.test(id.value))
    .map((id) => id.value);

  return filteredIds[0] ?? "";
};

/**
 * Evaluates patient contact info from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing patient contact info.
 * @param mappings - The object containing the fhir paths.
 * @returns All phone numbers and emails seperated by new lines
 */
export const evaluatePatientContactInfo = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const phoneNumbers = evaluate(fhirBundle, mappings.patientPhoneNumbers)
    .map(
      (phoneNumber) =>
        `${
          phoneNumber?.use?.charAt(0).toUpperCase() +
          phoneNumber?.use?.substring(1)
        } ${phoneNumber.value}`,
    )
    .join("\n");
  const emails = evaluate(fhirBundle, mappings.patientEmails)
    .map((email) => `${email.value}`)
    .join("\n");

  return `${phoneNumbers}\n${emails}`;
};

/**
 * Extracts travel history information from the provided FHIR bundle based on the FHIR path mappings.
 * @param fhirBundle - The FHIR bundle containing patient travel history data.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns - A formatted string representing the patient's travel history, or undefined if no relevant data is found.
 */
const evaluateTravelHistory = (
  fhirBundle: Bundle,
  mappings: PathMappings,
): string | undefined => {
  const startDate = evaluate(
    fhirBundle,
    mappings["patientTravelHistoryStartDate"],
  )[0];
  const endDate = evaluate(
    fhirBundle,
    mappings["patientTravelHistoryEndDate"],
  )[0];
  const location = evaluate(
    fhirBundle,
    mappings["patientTravelHistoryLocation"],
  )[0];
  const purposeOfTravel = evaluate(
    fhirBundle,
    mappings["patientTravelHistoryPurpose"],
  )[0];
  if (startDate || endDate || location || purposeOfTravel) {
    return `Dates: ${startDate} - ${endDate}
         Location(s): ${location ?? "No data"}
         Purpose of Travel: ${purposeOfTravel ?? "No data"}
         `;
  }
};

/**
 * Calculates the age of a patient to a given date or today.
 * @param fhirBundle - The FHIR bundle containing patient information.
 * @param fhirPathMappings - The mappings for retrieving patient date of birth.
 * @param [givenDate] - Optional. The target date to calculate the age. Defaults to the current date if not provided.
 * @returns - The age of the patient in years, or undefined if date of birth is not available.
 */
export const calculatePatientAge = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
  givenDate?: string,
) => {
  const patientDOBString = evaluate(fhirBundle, fhirPathMappings.patientDOB)[0];
  if (patientDOBString) {
    const patientDOB = new Date(patientDOBString);
    const targetDate = givenDate ? new Date(givenDate) : new Date();
    return dateFns.differenceInYears(targetDate, patientDOB);
  }
};

/**
 * Evaluates social data from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing social data.
 * @param mappings - The object containing the fhir paths.
 * @returns An array of evaluated and formatted social data.
 */
export const evaluateSocialData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const socialData: DisplayDataProps[] = [
    {
      title: "Occupation",
      value: evaluate(fhirBundle, mappings["patientCurrentJobTitle"])[0],
    },
    {
      title: "Tobacco Use",
      value: evaluate(fhirBundle, mappings["patientTobaccoUse"])[0],
    },
    {
      title: "Travel History",
      value: evaluateTravelHistory(fhirBundle, mappings),
    },
    {
      title: "Homeless Status",
      value: evaluate(fhirBundle, mappings["patientHomelessStatus"])[0],
    },
    {
      title: "Pregnancy Status",
      value: evaluate(fhirBundle, mappings["patientPregnancyStatus"])[0],
    },
    {
      title: "Alcohol Use",
      value: evaluate(fhirBundle, mappings["patientAlcoholUse"])[0],
    },
    {
      title: "Sexual Orientation",
      value: evaluate(fhirBundle, mappings["patientSexualOrientation"])[0],
    },
    {
      title: "Gender Identity",
      value: evaluate(fhirBundle, mappings["patientGenderIdentity"])[0],
    },
    {
      title: "Occupation",
      value: evaluate(fhirBundle, mappings["patientCurrentJobTitle"])[0],
    },
  ];
  return evaluateData(socialData);
};

/**
 * Evaluates demographic data from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing demographic data.
 * @param mappings - The object containing the fhir paths.
 * @returns An array of evaluated and formatted demographic data.
 */
export const evaluateDemographicsData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const demographicsData: DisplayDataProps[] = [
    {
      title: "Patient Name",
      value: evaluatePatientName(fhirBundle, mappings),
    },
    { title: "DOB", value: evaluate(fhirBundle, mappings.patientDOB)[0] },
    {
      title: "Current Age",
      value: calculatePatientAge(fhirBundle, mappings)?.toString(),
    },
    {
      title: "Vital Status",
      value: evaluate(fhirBundle, mappings.patientVitalStatus)[0]
        ? "Deceased"
        : "Alive",
    },
    { title: "Sex", value: evaluate(fhirBundle, mappings.patientGender)[0] },
    {
      title: "Race",
      value: evaluatePatientRace(fhirBundle, mappings),
    },
    {
      title: "Ethnicity",
      value: evaluate(fhirBundle, mappings.patientEthnicity)[0],
    },
    {
      title: "Tribal Affiliation",
      value: evaluate(fhirBundle, mappings.patientTribalAffiliation)[0],
    },
    {
      title: "Preferred Language",
      value: evaluate(fhirBundle, mappings.patientLanguage)[0],
    },
    {
      title: "Patient Address",
      value: evaluatePatientAddress(fhirBundle, mappings),
    },
    {
      title: "County",
      value: evaluate(fhirBundle, mappings.patientCounty)[0],
    },
    {
      title: "Contact",
      value: evaluatePatientContactInfo(fhirBundle, mappings),
    },
    {
      title: "Emergency Contact",
      value: evaluateEmergencyContact(fhirBundle, mappings),
    },
    {
      title: "Patient IDs",
      toolTip:
        "Unique patient identifier(s) from their medical record. For example, a patient's social security number or medical record number.",
      value: evaluateIdentifiers(fhirBundle, mappings.patientIds),
    },
  ];
  return evaluateData(demographicsData);
};

/**
 * Evaluates encounter data from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing encounter data.
 * @param mappings - The object containing the fhir paths.
 * @returns An array of evaluated and formatted encounter data.
 */
export const evaluateEncounterData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const encounterData = [
    {
      title: "Encounter Date/Time",
      value: formatStartEndDateTime(
        evaluate(fhirBundle, mappings["encounterStartDate"])[0],
        evaluate(fhirBundle, mappings["encounterEndDate"])[0],
      ),
    },
    {
      title: "Encounter Type",
      value: evaluate(fhirBundle, mappings["encounterType"])[0],
    },
    {
      title: "Encounter ID",
      value: evaluateEncounterId(fhirBundle, mappings),
    },
  ];
  return evaluateData(encounterData);
};

/**
 * Evaluates facility data from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing facility data.
 * @param mappings - The object containing the fhir paths.
 * @returns An array of evaluated and formatted facility data.
 */
export const evaluateFacilityData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const facilityContactAddressRef = evaluate(
    fhirBundle,
    mappings["facilityContactAddress"],
  );
  let referenceString;

  if (facilityContactAddressRef[0]) {
    referenceString = facilityContactAddressRef[0].reference;
  }
  const facilityContactAddress = referenceString
    ? evaluateReference(fhirBundle, mappings, referenceString)?.address?.[0]
    : undefined;

  const facilityData = [
    {
      title: "Facility Name",
      value: evaluate(fhirBundle, mappings["facilityName"])[0],
    },
    {
      title: "Facility Address",
      value: formatAddress(
        evaluate(fhirBundle, mappings["facilityStreetAddress"]),
        evaluate(fhirBundle, mappings["facilityCity"])[0],
        evaluate(fhirBundle, mappings["facilityState"])[0],
        evaluate(fhirBundle, mappings["facilityZipCode"])[0],
        evaluate(fhirBundle, mappings["facilityCountry"])[0],
      ),
    },
    {
      title: "Facility Contact Address",
      value: formatAddress(
        facilityContactAddress?.line,
        facilityContactAddress?.city,
        facilityContactAddress?.state,
        facilityContactAddress?.postalCode,
        facilityContactAddress?.country,
      ),
    },
    {
      title: "Facility Contact",
      value: formatPhoneNumber(
        evaluate(fhirBundle, mappings["facilityContact"])[0],
      ),
    },
    {
      title: "Facility Type",
      value: evaluate(fhirBundle, mappings["facilityType"])[0],
    },
    {
      title: "Facility ID",
      value: evaluateFacilityId(fhirBundle, mappings),
    },
  ];
  return evaluateData(facilityData);
};

/**
 * Evaluates provider data from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing provider data.
 * @param mappings - The object containing the fhir paths.
 * @returns An array of evaluated and formatted provider data.
 */
export const evaluateProviderData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const encounterRef: string | undefined = evaluate(
    fhirBundle,
    mappings["compositionEncounterRef"],
  )[0];
  const encounter: Encounter = evaluateReference(
    fhirBundle,
    mappings,
    encounterRef ?? "",
  );
  const encounterParticipantRef: string | undefined = evaluate(
    encounter,
    mappings["encounterIndividualRef"],
  )[0];
  const { practitioner, organization } = evaluatePractitionerRoleReference(
    fhirBundle,
    mappings,
    encounterParticipantRef ?? "",
  );

  const providerData = [
    {
      title: "Provider Name",
      value: formatName(
        practitioner?.name?.[0].given,
        practitioner?.name?.[0].family,
        practitioner?.name?.[0].prefix,
        practitioner?.name?.[0].suffix,
      ),
    },
    {
      title: "Provider Address",
      value: practitioner?.address?.map((address) =>
        formatAddress(
          address.line ?? [],
          address.city ?? "",
          address.state ?? "",
          address.postalCode ?? "",
          address.country ?? "",
        ),
      ),
    },
    {
      title: "Provider Contact",
      value: formatContactPoint(practitioner?.telecom).join("\n"),
    },
    {
      title: "Provider Facility Name",
      value: organization?.name,
    },
    {
      title: "Provider Facility Address",
      value: organization?.address?.map((address) =>
        formatAddress(
          address.line ?? [],
          address.city ?? "",
          address.state ?? "",
          address.postalCode ?? "",
          address.country ?? "",
        ),
      ),
    },
    {
      title: "Provider ID",
      value: practitioner?.identifier?.map((id) => id.value).join("\n"),
    },
  ];

  return evaluateData(providerData);
};

/**
 * Evaluates emergency contact information from the FHIR bundle and formats it into a readable string.
 * @param fhirBundle - The FHIR bundle containing patient information.
 * @param mappings - The object containing the fhir paths.
 * @returns The formatted emergency contact information.
 */
export const evaluateEmergencyContact = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const contact = evaluate(fhirBundle, mappings.patientEmergencyContact)[0];

  let formattedContact;

  if (contact) {
    if (contact.relationship) {
      const relationship = contact.relationship;
      formattedContact = `${relationship}`;
    }

    if (contact.address) {
      const address = formatAddress(
        contact.address[0].line,
        contact.address[0].city,
        contact.address[0].state,
        contact.address[0].postalCode,
        contact.address[0].country,
      );

      formattedContact = `${formattedContact}\n${address}`;
    }

    if (contact.telecom) {
      const phoneNumbers = evaluate(fhirBundle, mappings.patientPhoneNumbers)
        .map(
          (phoneNumber) =>
            `${
              phoneNumber?.use?.charAt(0).toUpperCase() +
              phoneNumber?.use?.substring(1)
            } ${phoneNumber.value}`,
        )
        .join("\n");

      formattedContact = `${formattedContact}\n${phoneNumbers}`;
    }

    return formattedContact;
  }
};

/**
 * Evaluates a reference in a FHIR bundle.
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
 * Evaluates the FHIR path and returns the appropriate string value. Supports choice elements
 * @param entry - The FHIR resource to evaluate.
 * @param path - The path within the resource to extract the value from.
 * @returns - The evaluated value as a string.
 */
export const evaluateValue = (entry: Element, path: string): string => {
  let originalValue = evaluate(entry, path, undefined, fhirpath_r4_model)[0];

  let value = "";
  const originalValuePath = originalValue?.__path__?.path;
  if (typeof originalValue === "string" || typeof originalValue === "number") {
    value = originalValue.toString();
  } else if (originalValuePath === "Quantity") {
    const data = originalValue as Quantity;
    let unit = data.unit;
    const firstLetterRegex = /^[a-z]/i;
    if (unit?.match(firstLetterRegex)) {
      unit = " " + unit;
    }
    value = `${data.value ?? ""}${unit ?? ""}`;
  } else if (originalValuePath === "CodeableConcept") {
    const data = originalValue as CodeableConcept;
    value = data.coding?.[0].display || data.text || "";
  } else if (typeof originalValue === "object") {
    console.log(`Not implemented for ${originalValue.__path__}`);
  }
  return value.trim();
};

/**
 * Evaluate the identifiers string and return in a formatted list.
 * @param fhirBundle The FHIR resource to evaluate.
 * @param path The path within the resource to extract the value from.
 * @returns Formatted string of identifiers
 */
export const evaluateIdentifiers = (fhirBundle: Bundle, path: string) => {
  const identifiers = evaluate(fhirBundle, path) as Identifier[];

  return identifiers
    .map((identifier) => {
      return `${identifier.value}`;
    })
    .join("\n");
};

/**
 * Find facility ID based on the first encounter's location
 * @param fhirBundle - The FHIR bundle containing resources.
 * @param mappings - Path mappings for resolving references.
 * @returns Facility id
 */
export const evaluateFacilityId = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const encounterLocationRef =
    evaluate(fhirBundle, mappings.facilityLocation)?.[0] ?? "";
  const location: Location = evaluateReference(
    fhirBundle,
    mappings,
    encounterLocationRef,
  );

  return location?.identifier?.[0].value;
};

/**
 * Evaluate practitioner role reference
 * @param fhirBundle - The FHIR bundle containing resources.
 * @param mappings - Path mappings for resolving references.
 * @param practitionerRoleRef - practitioner role reference to be searched.
 * @returns practitioner and organization
 */
export const evaluatePractitionerRoleReference = (
  fhirBundle: Bundle,
  mappings: PathMappings,
  practitionerRoleRef: string,
): { practitioner?: Practitioner; organization?: Organization } => {
  const practitionerRole: PractitionerRole | undefined = evaluateReference(
    fhirBundle,
    mappings,
    practitionerRoleRef,
  );
  const practitioner: Practitioner | undefined = evaluateReference(
    fhirBundle,
    mappings,
    practitionerRole?.practitioner?.reference ?? "",
  );
  const organization: Organization | undefined = evaluateReference(
    fhirBundle,
    mappings,
    practitionerRole?.organization?.reference ?? "",
  );
  return { practitioner, organization };
};
