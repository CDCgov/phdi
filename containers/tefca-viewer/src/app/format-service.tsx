import React from "react";
import {
  CodeableConcept,
  HumanName,
  Address,
  ContactPoint,
  Identifier,
} from "fhir/r4";
import { ValueSetItem } from "./constants";
import { QueryStruct } from "./query-service";

/**
 * Formats a string.
 * @param input - The string to format.
 * @returns The formatted string.
 */
export const formatString = (input: string): string => {
  // Convert to lowercase
  let result = input.toLowerCase();

  // Replace spaces with dashes
  result = result.replace(/\s+/g, "-");

  // Remove all special characters except dashes
  result = result.replace(/[^a-z0-9\-]/g, "");

  return result;
};

/**
 * Formats a CodeableConcept object for display. If the object has a coding array,
 * the first coding object is used.
 * @param concept - The CodeableConcept object.
 * @returns The CodeableConcept data formatted for
 * display.
 */
export function formatCodeableConcept(concept: CodeableConcept | undefined) {
  if (!concept) {
    return "";
  }
  if (!concept.coding || concept.coding.length === 0) {
    return concept.text || "";
  }
  const coding = concept.coding[0];
  return (
    <>
      {" "}
      {coding.display} <br /> {coding.code} <br /> {coding.system}{" "}
    </>
  );
}

/**
 * Formats the name of a FHIR HumanName object.
 * @param names - The HumanName object to format.
 * @returns The formatted name.
 */
export function formatName(names: HumanName[]): string {
  let name = "";
  if (names.length > 0) {
    const givenNames = names[0].given?.filter((n) => n).join(" ") ?? "";
    const familyName = names[0].family ?? "";
    name = `${givenNames} ${familyName}`.trim();
  }
  return name;
}

/**
 * Formats the address of a FHIR Address object.
 * @param address - The Address object to format.
 * @returns The formatted address.
 */
export function formatAddress(address: Address[]): JSX.Element {
  // return empty if no items in address
  if (address.length === 0) {
    return <></>;
  }

  const addr = address[0];
  const allFieldsEmpty = [
    ...(addr.line || []),
    addr.city,
    addr.state,
    addr.postalCode,
  ].every((field) => !field);
  // return empty if all items in address are empty
  if (allFieldsEmpty) {
    return <></>;
  }
  // else return
  return (
    <div>
      {addr.line?.map((line, index) => <div key={index}>{line}</div>)}
      <div>
        {addr.city}
        {addr.city && ", "}
        {addr.state} {addr.postalCode}
      </div>
    </div>
  );
}

/**
 * Formats the contact information of a FHIR ContactPoint object.
 * @param contacts - The ContactPoint object to format.
 * @returns - The formatted contact information.
 */
export function formatContact(contacts: ContactPoint[]): JSX.Element {
  return (
    <>
      {contacts.map((contact, index) => {
        if (contact.system === "phone") {
          return (
            <React.Fragment key={index}>
              {contact.use}: {contact.value} <br />
            </React.Fragment>
          );
        } else if (contact.system === "email") {
          return (
            <React.Fragment key={index}>
              {contact.value} <br />
            </React.Fragment>
          );
        }
        return null;
      })}
    </>
  );
}

/**
 * Formats the identifiers of a FHIR Identifier object.
 * @param identifier - The Identifier object to format.
 * @returns The formatted identifiers.
 */
export function formatIdentifier(identifier: Identifier[]): JSX.Element {
  return (
    <>
      {identifier.map((id) => {
        let idType = id.type?.coding?.[0].display ?? "";
        if (idType === "") {
          idType = id.type?.text ?? "";
        }

        return (
          <>
            {" "}
            {idType}: {id.value} <br />{" "}
          </>
        );
      })}
    </>
  );
}

/**
 * Formats the MRN of a FHIR Identifier object.
 * @param identifier - The Identifier object to format.
 * @returns The formatted MRN.
 */
export function formatMRN(identifier: Identifier[]): JSX.Element {
  return (
    <>
      {identifier.map((id) => {
        let mrnFlag = false;
        id.type?.coding?.forEach((code) => {
          if (code.code === "MR") {
            mrnFlag = true;
          }
        });
        if (mrnFlag) {
          return (
            <>
              {" "}
              {id.value} <br />{" "}
            </>
          );
        }

        return null;
      })}
    </>
  );
}

/**
 * Formats the provided date string into a formatted date string with year, month, and day.
 * @param dateString - The date string to be formatted. formatDate will also be able to take 'yyyymmdd' as input.
 * @returns - The formatted date string, "" if input date was invalid, or undefined if the input date is falsy.
 */
export const formatDate = (dateString?: string): string | undefined => {
  if (dateString) {
    let date = new Date(dateString);

    if (date.toString() != "Invalid Date") {
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        timeZone: "UTC",
      }); // UTC, otherwise will have timezone issues
    }
  }
};

/**
 * @todo Add country code form box on search form
 * @todo Update documentation here once that's done to reflect switch
 * logic of country code
 *
 * Helper function to strip out non-digit characters from a phone number
 * entered into the search tool. Right now, we're not going to worry about
 * country code or international numbers, so we'll just make an MVP
 * assumption of 10 regular digits.
 * @param givenPhone The original phone number the user typed.
 * @returns The phone number as a pure digit string. If the cleaned number
 * is fewer than 10 digits, just return the original.
 */
export function FormatPhoneAsDigits(givenPhone: string) {
  // Start by getting rid of all existing separators for a clean slate
  const newPhone: string = givenPhone.replace(/\D/g, "");
  if (newPhone.length != 10) {
    return givenPhone;
  }
  return newPhone;
}

const FORMATS_TO_SEARCH: string[] = [
  "$1$2$3",
  "$1-$2-$3",
  "$1+$2+$3",
  "($1)+$2+$3",
  "($1)-$2-$3",
  "($1)$2-$3",
  "1($1)$2-$3",
];

/**
 * @todo Once the country code box is created on the search form, we'll
 * need to use that value to act as a kind of switch logic here to figure
 * out which formats we should be using.
 * Helper function to transform a cleaned, digit-only representation of
 * a phone number into multiple possible formatting options of that phone
 * number. If the given number has fewer than 10 digits, or contains any
 * delimiters, no formatting is performed and only the given number is
 * used.
 * @param phone A digit-only representation of a phone number.
 * @returns An array of formatted phone numbers.
 */
export async function GetPhoneQueryFormats(phone: string) {
  // Digit-only phone numbers will resolve as actual numbers
  if (isNaN(Number(phone)) || phone.length != 10) {
    const strippedPhone = phone.replace(" ", "+");
    return [strippedPhone];
  }
  // Map the phone number into each format we want to check
  const possibleFormats: string[] = FORMATS_TO_SEARCH.map((fmt) => {
    return phone.replace(/(\d{3})(\d{3})(\d{4})/gi, fmt);
  });
  return possibleFormats;
}

/**
 * Formats a statefully updated list of value set items into a JSON structure
 * used for executing custom queries.
 * @param useCase The base use case being queried for.
 * @param vsItems The list of value set items the user wants included.
 * @returns A structured specification of a query that can be executed.
 */
export const formatValueSetItemsAsQuerySpec = async (
  useCase: string,
  vsItems: ValueSetItem[],
) => {
  let secondEncounter: boolean = false;
  if (["cancer", "chlamydia", "gonorrhea", "syphilis"].includes(useCase)) {
    secondEncounter = true;
  }
  const labCodes: string[] = vsItems
    .filter((vs) => vs.system === "http://loinc.org")
    .map((vs) => vs.code);
  const snomedCodes: string[] = vsItems
    .filter((vs) => vs.system === "http://snomed.info/sct")
    .map((vs) => vs.code);
  const rxnormCodes: string[] = vsItems
    .filter((vs) => vs.system === "http://www.nlm.nih.gov/research/umls/rxnorm")
    .map((vs) => vs.code);

  const spec: QueryStruct = {
    labCodes: labCodes,
    snomedCodes: snomedCodes,
    rxnormCodes: rxnormCodes,
    classTypeCodes: [] as string[],
    hasSecondEncounterQuery: secondEncounter,
  };

  return spec;
};
