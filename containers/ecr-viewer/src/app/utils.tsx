import { Bundle } from "fhir/r4";
import { evaluate } from "fhirpath";

export interface DisplayData {
  title: string;
  value: string;
}

export interface PathMappings {
  [key: string]: string;
}

export const socialData = [
  {
    title: "Occupation",
    value: "patientCurrentJobTitle",
  },
  {
    title: "Tobacco Use",
    value: "patientTobaccoUse",
  },
  {
    title: "Travel History",
    value: "patientTravelHistory",
  },
  {
    title: "Homeless Status",
    value: "patientHomelessStatus",
  },
  {
    title: "Pregnancy Status",
    value: "patientPregnancyStatus",
  },
  {
    title: "Alcohol Use",
    value: "patientAlcoholUse",
  },
  {
    title: "Sexual Orientation",
    value: "patientSexualOrientation",
  },
  {
    title: "Gender Identity",
    value: "patientGenderIdentity",
  },
  {
    title: "Occupation",
    value: "patientCurrentJobTitle",
  },
];

export const formatPatientName = (
  fhirBundle: Bundle | undefined,
  fhirPathMappings: PathMappings,
) => {
  const givenNames = evaluate(
    fhirBundle,
    fhirPathMappings.patientGivenName,
  ).join(" ");
  const familyName = evaluate(fhirBundle, fhirPathMappings.patientFamilyName);

  return `${givenNames} ${familyName}`;
};

export const formatPatientAddress = (
  fhirBundle: Bundle | undefined,
  fhirPathMappings: PathMappings,
) => {
  const streetAddresses = evaluate(
    fhirBundle,
    fhirPathMappings.patientStreetAddress,
  ).join("\n");
  const city = evaluate(fhirBundle, fhirPathMappings.patientCity);
  const state = evaluate(fhirBundle, fhirPathMappings.patientState);
  const zipCode = evaluate(fhirBundle, fhirPathMappings.patientZipCode);
  const country = evaluate(fhirBundle, fhirPathMappings.patientCountry);
  return `${streetAddresses}
    ${city}, ${state}
    ${zipCode}${country && `, ${country}`}`;
};

export const formatPatientContactInfo = (
  fhirBundle: Bundle | undefined,
  fhirPathMappings: PathMappings,
) => {
  const phoneNumbers = evaluate(
    fhirBundle,
    fhirPathMappings.patientPhoneNumbers,
  )
    .map(
      (phoneNumber) =>
        `${
          phoneNumber?.use?.charAt(0).toUpperCase() +
          phoneNumber?.use?.substring(1)
        } ${phoneNumber.value}`,
    )
    .join("\n");
  const emails = evaluate(fhirBundle, fhirPathMappings.patientEmails)
    .map((email) => `${email.value}`)
    .join("\n");

  return `${phoneNumbers}
    ${emails}`;
};

export const evaluateSocialData = (
  fhirBundle: Bundle | undefined,
  mappings: PathMappings,
) => {
  let socialArray: DisplayData[] = [];
  let unavailableArray: DisplayData[] = [];
  socialData.forEach((item) => {
    const evaluatedFhirPath = evaluate(fhirBundle, mappings[item.value]);
    const evaluatedItem: DisplayData = {
      title: item.title,
      value: evaluatedFhirPath[0],
    };

    if (evaluatedFhirPath.length > 0) {
      socialArray.push(evaluatedItem);
    } else {
      unavailableArray.push(evaluatedItem);
    }
  });
  return { available_data: socialArray, unavailable_data: unavailableArray };
};
