import { Bundle, Organization, Reference } from "fhir/r4";
import { evaluate } from "fhirpath";
import { Table } from "@trussworks/react-uswds";
import * as R4Models from "fhirpath/fhir-context/r4";

export interface DisplayData {
  title: string;
  value: string | undefined;
}

export interface PathMappings {
  [key: string]: string;
}

export interface ColumnInfoInput {
  columnName: string;
  infoPath: string;
}

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

const formatName = (firstName: string, lastName: string) => {
  if (firstName != undefined) {
    return `${firstName} ${lastName}`;
  } else {
    return undefined;
  }
};

export const extractPatientAddress = (
  fhirBundle: Bundle | undefined,
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
  fhirBundle: Bundle | undefined,
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
  fhirBundle: Bundle | undefined,
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
  fhirBundle: Bundle | undefined,
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

  return `${phoneNumbers}\n${emails}`;
};

export const formatEncounterDate = (
  fhirBundle: Bundle | undefined,
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

export const formatDate = (date: string) => {
  if (!date || date === null) {
    return "N/A";
  }

  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  };

  return new Date(date).toLocaleDateString("en-US", {
    ...options,
    timeZone: "UTC",
  }); // UTC, otherwise will have timezone issues
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
  if (heightAmount != undefined && heightMeasurementType != undefined) {
    if (heightMeasurementType == "[in_i]") {
      heightType = "inches";
    } else if (heightMeasurementType == "cm") {
      heightType = "cm";
    }
    heightString = `Height: ${heightAmount} ${heightType}\n\n`;
  }

  if (weightAmount != undefined && weightMeasurementType != undefined) {
    if (weightMeasurementType == "[lb_av]") {
      weightType = "Lbs";
    } else if (weightMeasurementType == "kg") {
      weightType = "kg";
    }
    weightString = `Weight: ${weightAmount} ${weightType}\n\n`;
  }

  if (bmi != undefined) {
    bmiString = `Body Mass Index (BMI): ${bmi}`;
  }

  const combinedString = `${heightString} ${weightString} ${bmiString}`;
  return combinedString.trim().length ? combinedString : "";
};

const formatTable = (
  resources: [],
  mappings: PathMappings,
  columns: [ColumnInfoInput], // Order of columns in array = order of apearance
  caption: string,
) => {
  let headers = [];
  columns.forEach((column) => {
    const header = (
      <>
        <th scope="col" className=" bg-gray-5 minw-15">
          {column.columnName}
        </th>
      </>
    );
    headers.push(header);
  });

  let tableRows = [];
  resources.forEach((entry) => {
    let rowCells = [];
    columns.forEach(function (column, index) {
      let isFirstCell = index === 0;

      let rowCellData;
      evaluate(entry, mappings[column.infoPath])[0]
        ? (rowCellData = evaluate(entry, mappings[column.infoPath])[0])
        : (rowCellData = "N/A");

      let rowCell = isFirstCell ? (
        <th scope="row" className="text-top">
          {rowCellData}
        </th>
      ) : (
        <td className="text-top">{rowCellData}</td>
      );
      rowCells.push(rowCell);
    });
    const tableRow = <tr>{rowCells}</tr>;
    tableRows.push(tableRow);
  });

  const tableContent = (
    <>
      <thead>
        <tr>{headers}</tr>
      </thead>
      <tbody>{tableRows}</tbody>
    </>
  );
  const table = (
    <Table
      borderless
      fullWidth
      caption={caption}
      className="border-top border-left border-right table-caption-margin"
    >
      {tableContent}
    </Table>
  );

  return table;
};

const extractTravelHistory = (
  fhirBundle: Bundle | undefined,
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
       Location(s): ${location ?? "N/A"}
       Purpose of Travel: ${purposeOfTravel ?? "N/A"}
       `;
  }
  return undefined;
};

export const evaluateSocialData = (
  fhirBundle: Bundle | undefined,
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
  fhirBundle: Bundle | undefined,
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
      value: evaluate(fhirBundle, mappings.patientEmergencyContact)[0],
    },
    {
      title: "Patient IDs",
      value: evaluate(fhirBundle, mappings.patientId)[0],
    },
  ];
  return evaluateData(demographicsData);
};

export const evaluateEncounterData = (
  fhirBundle: Bundle | undefined,
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
  fhirBundle: Bundle | undefined,
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
  fhirBundle: Bundle | undefined,
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

export const returnProblemsTable = (problemsArray, mappings) => {
  if (problemsArray.length === 0) {
    return undefined;
  }

  const columnInfo = [
    { columnName: "Active Problem", infoPath: "activeProblemsDisplay" },
    { columnName: "Onset Age", infoPath: "activeProblemsOnsetAge" },
    { columnName: "Onset Date", infoPath: "activeProblemsOnsetDate" },
  ];

  problemsArray.forEach((entry) => {
    entry.onsetDateTime
      ? (entry.onsetDateTime = formatDate(entry.onsetDateTime))
      : (entry.onsetDateTime = "N/A");
  });

  problemsArray.sort(function (a, b) {
    return new Date(b.onsetDateTime) - new Date(a.onsetDateTime);
  });

  return formatTable(problemsArray, mappings, columnInfo, "Problems List");
};

export const evaluateClinicalData = (
  fhirBundle: Bundle | undefined,
  mappings: PathMappings,
) => {
  const activeProblemsData: DisplayData[] = [
    {
      title: "Problems List",
      value: returnProblemsTable(
        evaluate(fhirBundle, mappings["activeProblems"]),
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
  return {
    activeProblemsDetails: evaluateData(activeProblemsData),
    vitalData: evaluateData(vitalData),
  };
};

const evaluateData = (data: DisplayData[]) => {
  let availableData: DisplayData[] = [];
  let unavailableData: DisplayData[] = [];
  data.forEach((item) => {
    if (item.value == undefined || item.value.length == 0) {
      unavailableData.push(item);
      item.value = "N/A";
    } else {
      availableData.push(item);
    }
  });
  return { availableData: availableData, unavailableData: unavailableData };
};
