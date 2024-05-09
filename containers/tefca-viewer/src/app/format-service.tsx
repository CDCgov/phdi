import {
  CodeableConcept,
  HumanName,
  Address,
  ContactPoint,
  Identifier,
} from "fhir/r4";
/**
 * Formats a string.
 * @param input - The string to format.
 * @returns The formatted string.
 */
export const formatString = (input: string): string => {
  // Convert to lowercase
  let result = input.toLowerCase();

  // Replace spaces with underscores
  result = result.replace(/\s+/g, "-");

  // Remove all special characters except underscores
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
    name = names[0].given?.join(" ") + " " + names[0].family;
  }
  return name;
}

/**
 * Formats the address of a FHIR Address object.
 * @param address - The Address object to format.
 * @returns The formatted address.
 */
export function formatAddress(address: Address[]): string {
  let formattedAddress = "";
  if (address.length > 0) {
    formattedAddress =
      address[0]?.line?.join("\n") +
      "\n" +
      address[0].city +
      ", " +
      address[0].state +
      " " +
      address[0].postalCode;
  }
  return formattedAddress;
}

/**
 * Formats the contact information of a FHIR ContactPoint object.
 * @param contacts - The ContactPoint object to format.
 * @returns - The formatted contact information.
 */
export function formatContact(contacts: ContactPoint[]): string {
  return contacts
    .map((contact) => {
      if (contact.system === "phone") {
        return `${contact.use}: ${contact.value}`;
      } else if (contact.system === "email") {
        return contact.value;
      }
    })
    .join("\n");
}

/**
 * Formats the identifiers of a FHIR Identifier object.
 * @param identifier - The Identifier object to format.
 * @returns The formatted identifiers.
 */
export function formatIdentifier(identifier: Identifier[]): string {
  return identifier
    .map((id) => {
      let idType = id.type?.coding?.[0].display ?? "";
      if (idType === "") {
        idType = id.type?.text ?? "";
      }

      return `${idType}: ${id.value}`;
    })
    .join("\n");
}
