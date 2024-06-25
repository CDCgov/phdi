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
      {contacts.map((contact) => {
        if (contact.system === "phone") {
          return (
            <>
              {contact.use}: {contact.value} <br />
            </>
          );
        } else if (contact.system === "email") {
          return (
            <>
              {contact.value} <br />
            </>
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
