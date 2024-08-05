"use server";

import { Patient } from "fhir/r4";
import { FormatPhoneAsDigits } from "@/app/format-service";

export type PatientIdentifiers = {
  first_name?: string;
  last_name?: string;
  dob?: string;
  mrn?: string;
  phone?: string;
};

/**
 * Parses a patient resource to extract patient demographics.
 * @param patient - The patient resource to parse.
 * @returns An array of patient demographics extracted from the patient resource.
 */
export async function parsePatientDemographics(
  patient: Patient,
): Promise<PatientIdentifiers> {
  const identifiers: PatientIdentifiers = {};

  if (patient.name) {
    const name = patient.name[0];
    if (name.given) {
      identifiers.first_name = name.given[0];
    }
    if (name.family) {
      identifiers.last_name = name.family;
    }
  }

  if (patient.birthDate) {
    identifiers.dob = patient.birthDate;
  }

  // Extract MRNs from patient.identifier
  const mrnIdentifiers = await parseMRNs(patient);
  // Add 1st value of MRN array to identifiers
  // TODO: Handle multiple MRNs to query
  if (mrnIdentifiers && mrnIdentifiers.length > 0) {
    identifiers.mrn = mrnIdentifiers[0];
  }

  // Extract phone numbers from patient telecom arrays
  let phoneNumbers = await parsePhoneNumbers(patient);
  if (phoneNumbers) {
    // Strip formatting so the query service can generate options
    phoneNumbers = phoneNumbers
      .map((phone) => FormatPhoneAsDigits(phone || ""))
      .filter((phone) => phone !== "");
    if (phoneNumbers.length == 1) {
      identifiers.phone = phoneNumbers[0];
    } else if (phoneNumbers.length > 1) {
      identifiers.phone = phoneNumbers.join(";");
    }
  }

  return identifiers;
}

/**
 * Extracts all MRNs from a patient resource and returns them as an array.
 * @param patient - The patient resource to parse.
 * @returns An array of MRNs extracted from the patient resource.
 */
export async function parseMRNs(
  patient: Patient,
): Promise<(string | undefined)[] | undefined> {
  if (patient.identifier) {
    const mrnIdentifiers = patient.identifier.filter((id) =>
      id.type?.coding?.some(
        (coding) =>
          coding.system === "http://terminology.hl7.org/CodeSystem/v2-0203" &&
          coding.code === "MR",
      ),
    );
    return mrnIdentifiers.map((id) => id.value);
  }
}

/**
 * Helper function that extracts all applicable phone numbers from a patient resource
 * and returns them as a list of strings, without changing the input formatting
 * of the phone numbers.
 * @param patient A FHIR Patient resource.
 * @returns A list of phone numbers, or undefined if the patient has no telecom.
 */
export async function parsePhoneNumbers(
  patient: Patient,
): Promise<(string | undefined)[] | undefined> {
  if (patient.telecom) {
    const phoneNumbers = patient.telecom.filter(
      (contactPoint) =>
        contactPoint.system === "phone" ||
        ["home", "work", "mobile"].includes(contactPoint.use || ""),
    );
    return phoneNumbers.map((contactPoint) => contactPoint.value);
  }
}
