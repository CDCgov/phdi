import {
  Bundle,
  Condition,
  FhirResource,
  Immunization,
  Organization,
  Procedure,
} from "fhir/r4";
import { evaluate } from "fhirpath";
import { Table } from "@trussworks/react-uswds";
import React from "react";
import parse from "html-react-parser";
import classNames from "classnames";
import { AccordionRR } from "@/app/view-data/components/AccordionRR";

export interface DisplayData {
  title: string;
  value?: string | React.JSX.Element;
}

export interface PathMappings {
  [key: string]: string;
}

export interface ColumnInfoInput {
  columnName: string;
  infoPath: string;
}

export const formatPatientName = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  const givenNames = evaluate(
    fhirBundle,
    fhirPathMappings.patientGivenName,
  ).join(" ");
  const familyName = evaluate(fhirBundle, fhirPathMappings.patientFamilyName);

  return `${givenNames} ${familyName}`;
};

const formatName = (firstName: string, lastName: string) => {
  if (firstName != undefined) {
    return `${firstName} ${lastName}`;
  } else {
    return undefined;
  }
};

export const extractPatientAddress = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  const streetAddresses = evaluate(
    fhirBundle,
    fhirPathMappings.patientStreetAddress,
  );
  const city = evaluate(fhirBundle, fhirPathMappings.patientCity)[0];
  const state = evaluate(fhirBundle, fhirPathMappings.patientState)[0];
  const zipCode = evaluate(fhirBundle, fhirPathMappings.patientZipCode)[0];
  const country = evaluate(fhirBundle, fhirPathMappings.patientCountry)[0];
  return formatAddress(streetAddresses, city, state, zipCode, country);
};

function extractLocationResource(
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) {
  const locationReference = evaluate(
    fhirBundle,
    fhirPathMappings.facilityLocation,
  ).join("");
  const locationUID = locationReference.split("/")[1];
  const locationExpression = `Bundle.entry.resource.where(resourceType = 'Location').where(id = '${locationUID}')`;
  return evaluate(fhirBundle, locationExpression)[0];
}

export const extractFacilityAddress = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  const locationResource = extractLocationResource(
    fhirBundle,
    fhirPathMappings,
  );

  const streetAddresses = locationResource?.address?.line;
  const city = locationResource?.address?.city;
  const state = locationResource?.address?.state;
  const zipCode = locationResource?.address?.postalCode;
  const country = locationResource?.address?.country;

  return formatAddress(streetAddresses, city, state, zipCode, country);
};

const formatAddress = (
  streetAddress: string[],
  city: string,
  state: string,
  zipCode: string,
  country: string,
) => {
  let address = {
    streetAddress: streetAddress || [],
    cityState: [city, state],
    zipCodeCountry: [zipCode, country],
  };

  return [
    address.streetAddress.join("\n"),
    address.cityState.filter(Boolean).join(", "),
    address.zipCodeCountry.filter(Boolean).join(", "),
  ]
    .filter(Boolean)
    .join("\n");
};

export const extractFacilityContactInfo = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  const locationResource = extractLocationResource(
    fhirBundle,
    fhirPathMappings,
  );
  const phoneNumbers = locationResource.telecom?.filter(
    (contact: any) => contact.system === "phone",
  );
  return phoneNumbers?.[0].value;
};

export const formatPatientContactInfo = (
  fhirBundle: Bundle,
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

  return `${phoneNumbers}\n${emails}`;
};

export const formatEncounterDate = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  const startDate = formatDateTime(
    evaluate(fhirBundle, fhirPathMappings.encounterStartDate).join(""),
  );
  const endDate = formatDateTime(
    evaluate(fhirBundle, fhirPathMappings.encounterEndDate).join(""),
  );

  return `Start: ${startDate}
    End: ${endDate}`;
};

const formatDateTime = (dateTime: string) => {
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "numeric",
    minute: "2-digit",
  };

  return new Date(dateTime)
    .toLocaleDateString("en-Us", options)
    .replace(",", "");
};

/**
 * Formats the provided date string into a formatted date string with year, month, and day.
 * @param {string} date - The date string to be formatted.
 * @returns {string | undefined} - The formatted date string or undefined if the input date is falsy.
 */
export const formatDate = (date?: string): string | undefined => {
  if (date) {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      timeZone: "UTC",
    }); // UTC, otherwise will have timezone issues
  }
};

const formatPhoneNumber = (phoneNumber: string) => {
  try {
    return phoneNumber
      .replace(/\D/g, "")
      .replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
  } catch {
    return undefined;
  }
};

const formatStartEndDateTime = (
  startDateTime: "string",
  endDateTime: "string",
) => {
  const startDateObject = new Date(startDateTime);
  const endDateObject = new Date(endDateTime);

  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  };

  const startFormattedDate = startDateObject
    .toLocaleString("en-US", options)
    .replace(",", "");
  const endFormattedDate = endDateObject
    .toLocaleString("en-us", options)
    .replace(",", "");

  return `Start: ${startFormattedDate}
        End: ${endFormattedDate}`;
};

const formatVitals = (
  heightAmount: string,
  heightMeasurementType: string,
  weightAmount: string,
  weightMeasurementType: string,
  bmi: string,
) => {
  let heightString = "";
  let weightString = "";
  let bmiString = "";

  let heightType = "";
  let weightType = "";
  if (heightAmount && heightMeasurementType) {
    if (heightMeasurementType === "[in_i]") {
      heightType = "inches";
    } else if (heightMeasurementType === "cm") {
      heightType = "cm";
    }
    heightString = `Height: ${heightAmount} ${heightType}\n\n`;
  }

  if (weightAmount && weightMeasurementType) {
    if (weightMeasurementType === "[lb_av]") {
      weightType = "Lbs";
    } else if (weightMeasurementType === "kg") {
      weightType = "kg";
    }
    weightString = `Weight: ${weightAmount} ${weightType}\n\n`;
  }

  if (bmi) {
    bmiString = `Body Mass Index (BMI): ${bmi}`;
  }

  const combinedString = `${heightString} ${weightString} ${bmiString}`;
  return combinedString.trim();
};

/**
 * Formats a table based on the provided resources, mappings, columns, and caption.
 * @param {FhirResource[]} resources - An array of FHIR Resources representing the data entries.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @param {ColumnInfoInput[]} columns - An array of objects representing column information.
 *                                      The order of columns in the array determines the order of appearance.
 * @param {string} caption - The caption for the table.
 * @returns {React.JSX.Element} - A formatted table React element.
 */
const formatTable = (
  resources: FhirResource[],
  mappings: PathMappings,
  columns: ColumnInfoInput[],
  caption: string,
): React.JSX.Element => {
  let headers = columns.map((column, index) => (
    <th
      key={`${column.columnName}${index}`}
      scope="col"
      className="bg-gray-5 minw-15"
    >
      {column.columnName}
    </th>
  ));

  let tableRows = resources.map((entry, index) => {
    let rowCells = columns.map((column, index) => {
      let rowCellData = evaluate(entry, mappings[column.infoPath])[0] ?? (
        <span className={"text-italic text-base"}>No data</span>
      );
      return (
        <td key={`row-data-${index}`} className="text-top">
          {rowCellData}
        </td>
      );
    });

    return <tr key={`table-row-${index}`}>{rowCells}</tr>;
  });

  return (
    <Table
      bordered={false}
      fullWidth={true}
      caption={caption}
      className="border-top border-left border-right table-caption-margin margin-y-0"
      data-testid="table"
    >
      <thead>
        <tr>{headers}</tr>
      </thead>
      <tbody>{tableRows}</tbody>
    </Table>
  );
};

/**
 * Extracts travel history information from the provided FHIR bundle based on the FHIR path mappings.
 * @param {Bundle} fhirBundle - The FHIR bundle containing patient travel history data.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @returns {string | undefined} - A formatted string representing the patient's travel history, or undefined if no relevant data is found.
 */
const extractTravelHistory = (
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

export const evaluateSocialData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const socialData = [
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
      value: extractTravelHistory(fhirBundle, mappings),
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

export const evaluateDemographicsData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const demographicsData = [
    {
      title: "Patient Name",
      value: formatPatientName(fhirBundle, mappings),
    },
    { title: "DOB", value: evaluate(fhirBundle, mappings.patientDOB)[0] },
    { title: "Sex", value: evaluate(fhirBundle, mappings.patientGender)[0] },
    { title: "Race", value: evaluate(fhirBundle, mappings.patientRace)[0] },
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
      value: extractPatientAddress(fhirBundle, mappings),
    },
    {
      title: "County",
      value: evaluate(fhirBundle, mappings.patientCounty)[0],
    },
    { title: "Contact", value: formatPatientContactInfo(fhirBundle, mappings) },
    {
      title: "Emergency Contact",
      value: evaluateEmergencyContact(fhirBundle, mappings),
    },
    {
      title: "Patient IDs",
      value: evaluate(fhirBundle, mappings.patientId)[0],
    },
  ];
  return evaluateData(demographicsData);
};

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
      value: evaluate(fhirBundle, mappings["facilityID"])[0],
    },
  ];
  return evaluateData(encounterData);
};

export const evaluateProviderData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const providerData = [
    {
      title: "Provider Name",
      value: formatName(
        evaluate(fhirBundle, mappings["providerGivenName"])[0],
        evaluate(fhirBundle, mappings["providerFamilyName"])[0],
      ),
    },
    {
      title: "Provider Contact",
      value: formatPhoneNumber(
        evaluate(fhirBundle, mappings["providerContact"])[0],
      ),
    },
  ];
  return evaluateData(providerData);
};

export const evaluateEcrMetadata = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const rrPerformerReferences = evaluate(fhirBundle, mappings.rrPerformers);

  const rrPerformers: Organization[] = rrPerformerReferences.map((ref) => {
    ref = ref.split("/");
    return evaluate(fhirBundle, mappings.resolve, {
      resourceType: ref[0],
      id: ref[1],
    })[0];
  });
  const rrDetails: DisplayData[] = [
    {
      title: "Reportable Condition(s)",
      value: evaluate(fhirBundle, mappings.rrDisplayNames)?.join("\n"),
    },
    {
      title: "RCKMS Trigger Summary",
      value: evaluate(fhirBundle, mappings.rckmsTriggerSummaries)?.join("\n"),
    },
    {
      title: "Jurisdiction(s) Sent eCR",
      value: rrPerformers.map((org) => org.name)?.join("\n"),
    },
  ];
  const eicrDetails: DisplayData[] = [
    {
      title: "eICR Identifier",
      value: evaluate(fhirBundle, mappings.eicrIdentifier)[0],
    },
  ];
  const ecrSenderDetails: DisplayData[] = [
    {
      title: "Date/Time eCR Created",
      value: evaluate(fhirBundle, mappings.dateTimeEcrCreated)[0],
    },
    {
      title: "Sender Software",
      value: evaluate(fhirBundle, mappings.senderSoftware)[0],
    },
    {
      title: "Sender Facility Name",
      value: evaluate(fhirBundle, mappings.senderFacilityName),
    },
    {
      title: "Facility Address",
      value: extractFacilityAddress(fhirBundle, mappings),
    },
    {
      title: "Facility Contact",
      value: evaluate(fhirBundle, mappings.facilityContact)[0],
    },
    {
      title: "Facility ID",
      value: evaluate(fhirBundle, mappings.facilityID)[0],
    },
  ];
  return {
    eicrDetails: evaluateData(eicrDetails),
    ecrSenderDetails: evaluateData(ecrSenderDetails),
    rrDetails: evaluateData(rrDetails),
  };
};

/**
 * Generates a formatted table representing the list of problems based on the provided array of problems and mappings.
 * @param {Condition[]} problemsArray - An array containing the list of problems.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @returns {React.JSX.Element | undefined} - A formatted table React element representing the list of problems, or undefined if the problems array is empty.
 */
export const returnProblemsTable = (
  problemsArray: Condition[],
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  if (problemsArray.length === 0) {
    return undefined;
  }

  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Active Problem", infoPath: "activeProblemsDisplay" },
    { columnName: "Onset Age", infoPath: "activeProblemsOnsetAge" },
    { columnName: "Onset Date", infoPath: "activeProblemsOnsetDate" },
  ];

  problemsArray.forEach((entry) => {
    entry.onsetDateTime = formatDate(entry.onsetDateTime);
  });

  problemsArray.sort(
    (a, b) =>
      new Date(b.onsetDateTime ?? "").getTime() -
      new Date(a.onsetDateTime ?? "").getTime(),
  );

  return formatTable(problemsArray, mappings, columnInfo, "Problems List");
};

/**
 * Generates a formatted table representing the list of immunizations based on the provided array of immunizations and mappings.
 * @param {Immunization[]} immunizationsArray - An array containing the list of immunizations.
 * @param {PathMappings} mappings - An object containing the FHIR path mappings.
 * @returns {React.JSX.Element | undefined} - A formatted table React element representing the list of immunizations, or undefined if the immunizations array is empty.
 */
export const returnImmunizations = (
  immunizationsArray: Immunization[],
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  if (immunizationsArray.length === 0) {
    return undefined;
  }

  const columnInfo = [
    { columnName: "Name", infoPath: "immunizationsName" },
    { columnName: "Administration Dates", infoPath: "immunizationsAdminDate" },
    { columnName: "Next Due", infoPath: "immunizationsNextDue" },
  ];

  immunizationsArray.forEach((entry) => {
    entry.occurrenceDateTime = formatDate(entry.occurrenceDateTime);
  });

  immunizationsArray.sort(
    (a, b) =>
      new Date(b.occurrenceDateTime ?? "").getTime() -
      new Date(a.occurrenceDateTime ?? "").getTime(),
  );

  return formatTable(
    immunizationsArray,
    mappings,
    columnInfo,
    "Immunization History",
  );
};

/**
 * Generates a formatted table representing the list of procedures based on the provided array of procedures and mappings.
 * @param {Procedure[]} proceduresArray - An array containing the list of procedures.
 * @param {PathMappings} mappings - An object containing FHIR path mappings for procedure attributes.
 * @returns {React.JSX.Element | undefined} - A formatted table React element representing the list of procedures, or undefined if the procedures array is empty.
 */
export const returnProceduresTable = (
  proceduresArray: Procedure[],
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  if (proceduresArray.length === 0) {
    return undefined;
  }

  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Name", infoPath: "procedureName" },
    { columnName: "Date Performed", infoPath: "procedureDate" },
    { columnName: "Reason", infoPath: "procedureReason" },
  ];

  proceduresArray.forEach((entry) => {
    entry.performedDateTime = formatDate(entry.performedDateTime);
  });

  proceduresArray.sort(
    (a, b) =>
      new Date(b.performedDateTime ?? "").getTime() -
      new Date(a.performedDateTime ?? "").getTime(),
  );

  return formatTable(proceduresArray, mappings, columnInfo, "Procedures");
};

export const evaluateClinicalData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const clinicalNotes: DisplayData[] = [
    {
      title: "Miscellaneous Notes",
      value: parse(
        evaluate(fhirBundle, mappings["historyOfPresentIllness"])[0]?.div || "",
      ),
    },
  ];

  const reasonForVisitData: DisplayData[] = [
    {
      title: "Reason for Visit",
      value: evaluate(fhirBundle, mappings["clinicalReasonForVisit"])[0],
    },
  ];

  const activeProblemsTableData: DisplayData[] = [
    {
      title: "Problems List",
      value: returnProblemsTable(
        evaluate(fhirBundle, mappings["activeProblems"]),
        mappings,
      ),
    },
  ];

  const treatmentData: DisplayData[] = [
    {
      title: "Procedures",
      value: returnProceduresTable(
        evaluate(fhirBundle, mappings["procedures"]),
        mappings,
      ),
    },
  ];

  const vitalData = [
    {
      title: "Vital Signs",
      value: formatVitals(
        evaluate(fhirBundle, mappings["patientHeight"])[0],
        evaluate(fhirBundle, mappings["patientHeightMeasurement"])[0],
        evaluate(fhirBundle, mappings["patientWeight"])[0],
        evaluate(fhirBundle, mappings["patientWeightMeasurement"])[0],
        evaluate(fhirBundle, mappings["patientBmi"])[0],
      ),
    },
  ];

  const immunizationsData: DisplayData[] = [
    {
      title: "Immunization History",
      value: returnImmunizations(
        evaluate(fhirBundle, mappings["immunizations"]),
        mappings,
      ),
    },
  ];
  return {
    clinicalNotes: evaluateData(clinicalNotes),
    reasonForVisitDetails: evaluateData(reasonForVisitData),
    activeProblemsDetails: evaluateData(activeProblemsTableData),
    treatmentData: evaluateData(treatmentData),
    vitalData: evaluateData(vitalData),
    immunizationsDetails: evaluateData(immunizationsData),
  };
};

/**
 * Evaluates the provided display data to determine availability.
 * @param {DisplayData[]} data - An array of display data items to be evaluated.
 * @returns {{ availableData: DisplayData[], unavailableData: DisplayData[] }} - An object containing arrays of available and unavailable display data items.
 */
const evaluateData = (
  data: DisplayData[],
): { availableData: DisplayData[]; unavailableData: DisplayData[] } => {
  let availableData: DisplayData[] = [];
  let unavailableData: DisplayData[] = [];
  data.forEach((item) => {
    if (!item.value || (Array.isArray(item.value) && item.value.length === 0)) {
      unavailableData.push(item);
    } else {
      availableData.push(item);
    }
  });
  return { availableData: availableData, unavailableData: unavailableData };
};

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
 * Functional component for displaying data.
 * @param {object} props - Props for the component.
 * @param {DisplayData} props.item - The display data item to be rendered.
 * @param {string} [props.className] - Additional class name for styling purposes.
 * @returns {React.JSX.Element} - A React element representing the display of data.
 */
export const DataDisplay: React.FC<{
  item: DisplayData;
  className?: string;
}> = ({
  item,
  className,
}: {
  item: DisplayData;
  className?: string;
}): React.JSX.Element => {
  return (
    <div>
      <div className="grid-row">
        <div className="data-title">{item.title}</div>
        <div
          className={classNames("grid-col-auto maxw7 text-pre-line", className)}
        >
          {item.value}
        </div>
      </div>
      <div className={"section__line_gray"} />
    </div>
  );
};

export const DataTableDisplay: React.FC<{ item: DisplayData }> = ({
  item,
}): React.JSX.Element => {
  return (
    <div className="grid-row">
      <div className="grid-col-auto text-pre-line">{item.value}</div>
      <div className={"section__line_gray"} />
    </div>
  );
};

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

export const evaluateLabInfoData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const labInfo: DisplayData[] = [
    {
      title: "Lab Performing Name",
      value: "",
    },
    {
      title: "Lab Address",
      value: "",
    },
    {
      title: "Lab Contact",
      value: "",
    },
  ];

  const rrData = evaluate(fhirBundle, mappings["diagnosticReports"]).map(
    (report) => {
      return (
        <AccordionRR
          title={report.code.coding[0].display}
          abnormalTag={false}
          content={<>hi</>}
        />
      );
    },
  );

  return {
    labInfo: evaluateData(labInfo),
    rr: rrData,
  };
};
