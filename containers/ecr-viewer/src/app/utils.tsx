import React from "react";
import * as dateFns from "date-fns";
import {
  Bundle,
  Condition,
  Immunization,
  Procedure,
  Practitioner,
  FhirResource,
} from "fhir/r4";
import { evaluate } from "fhirpath";
import parse from "html-react-parser";
import classNames from "classnames";

import {
  formatAddress,
  formatDate,
  formatName,
  formatPhoneNumber,
  formatStartEndDateTime,
  formatVitals,
  formatDateTime,
  formatTablesToJSON,
  TableRow,
} from "@/app/format-service";
import { evaluateTable, evaluateReference } from "./evaluate-service";
import { Table } from "@trussworks/react-uswds";
import { CareTeamParticipant, CarePlanActivity } from "fhir/r4b";

export interface DisplayData {
  title?: string;
  className?: string;
  value?: string | React.JSX.Element | React.JSX.Element[] | React.ReactNode;
  dividerLine?: boolean;
}

export interface ReportableConditions {
  [condition: string]: {
    [trigger: string]: Set<string>;
  };
}

export interface PathMappings {
  [key: string]: string;
}

export interface ColumnInfoInput {
  columnName: string;
  infoPath?: string;
  value?: string;
  sentenceCase?: boolean;
}

export interface CompleteData {
  availableData: DisplayData[];
  unavailableData: DisplayData[];
}

export const noData = (
  <span className="no-data text-italic text-base">No data</span>
);

export const evaluatePatientName = (
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

/**
 * Extracts a specific location resource from a given FHIR bundle based on defined path mappings.
 * @param fhirBundle - The FHIR bundle object containing various resources, including location resources.
 * @param fhirPathMappings - An object containing FHIR path mappings, which should include a mapping
 *   for `facilityLocation` that determines how to find the location reference within the bundle.
 * @returns The location resource object from the FHIR bundle that matches the UID derived from the
 *   facility location reference. If no matching resource is found, the function returns `undefined`.
 */
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

export const evaluatePatientContactInfo = (
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

export const evaluateEncounterDate = (
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

/**
 * Extracts travel history information from the provided FHIR bundle based on the FHIR path mappings.
 * @param fhirBundle - The FHIR bundle containing patient travel history data.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns - A formatted string representing the patient's travel history, or undefined if no relevant data is found.
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

export const evaluateSocialData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const socialData: DisplayData[] = [
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
  const demographicsData: DisplayData[] = [
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
        evaluate(fhirBundle, mappings["providerGivenName"]),
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

  const eicrDetails: DisplayData[] = [
    {
      title: "eICR Identifier",
      value: evaluate(fhirBundle, mappings.eicrIdentifier)[0],
    },
  ];
  const ecrSenderDetails: DisplayData[] = [
    {
      title: "Date/Time eCR Created",
      value: formatDateTime(
        evaluate(fhirBundle, mappings.dateTimeEcrCreated)[0],
      ),
    },
    {
      title: "Sender Software",
      value: evaluate(fhirBundle, mappings.senderSoftware)[0],
    },
    {
      title: "Sender Facility Name",
      value: evaluate(fhirBundle, mappings.senderFacilityName)[0],
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
    rrDetails: reportableConditionsList,
  };
};

/**
 * Generates a formatted table representing the list of problems based on the provided array of problems and mappings.
 * @param fhirBundle - The FHIR bundle containing patient information.
 * @param problemsArray - An array containing the list of problems.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns - A formatted table React element representing the list of problems, or undefined if the problems array is empty.
 */
export const returnProblemsTable = (
  fhirBundle: Bundle,
  problemsArray: Condition[],
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  if (problemsArray.length === 0) {
    return undefined;
  }

  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Active Problem", infoPath: "activeProblemsDisplay" },
    { columnName: "Onset Date", infoPath: "activeProblemsOnsetDate" },
    { columnName: "Onset Age", infoPath: "activeProblemsOnsetAge" },
  ];

  problemsArray.forEach((entry) => {
    entry.onsetDateTime = formatDate(entry.onsetDateTime);
    entry.onsetAge = {
      value: calculatePatientAge(fhirBundle, mappings, entry.onsetDateTime),
    };
  });

  problemsArray.sort(
    (a, b) =>
      new Date(b.onsetDateTime ?? "").getTime() -
      new Date(a.onsetDateTime ?? "").getTime(),
  );

  return evaluateTable(
    problemsArray,
    mappings,
    columnInfo,
    "Problems List",
    false,
  );
};

export const returnPendingResultsTable = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const planOfTreatmentTables = formatTablesToJSON(
    evaluate(fhirBundle, mappings["planOfTreatment"])[0]?.div,
  );
  const pendingResultsTableJson = planOfTreatmentTables.find(
    (val) => val.resultName === "Pending Results",
  );

  if (pendingResultsTableJson?.tables?.[0]) {
    const header = [
      "Name",
      "Type",
      "Priority",
      "Associated Diagnoses",
      "Date/Time",
    ];

    return (
      <Table
        bordered={false}
        fullWidth={true}
        className={
          "table-caption-margin caption-normal-weight margin-y-0 border-top border-left border-right"
        }
        data-testid="table"
        caption={"Pending Results"}
      >
        <thead>
          <tr>
            {header.map((column) => (
              <th key={`${column}`} scope="col" className="bg-gray-5 minw-15">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {pendingResultsTableJson.tables[0].map(
            (entry: TableRow, index: number) => {
              return (
                <tr key={`table-row-${index}`}>
                  <td>{entry.Name?.value ?? noData}</td>
                  <td>{entry.Type?.value ?? noData}</td>
                  <td>{entry.Priority?.value ?? noData}</td>
                  <td>{entry.AssociatedDiagnoses?.value ?? noData}</td>
                  <td>{entry["Date/Time"]?.value ?? noData}</td>
                </tr>
              );
            },
          )}
        </tbody>
      </Table>
    );
  }
};

/**
 * Generates a formatted table representing the list of immunizations based on the provided array of immunizations and mappings.
 * @param immunizationsArray - An array containing the list of immunizations.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns - A formatted table React element representing the list of immunizations, or undefined if the immunizations array is empty.
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

  return evaluateTable(
    immunizationsArray,
    mappings,
    columnInfo,
    "Immunization History",
  );
};

export const returnCareTeamTable = (
  bundle: Bundle,
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  const careTeamParticipants: CareTeamParticipant[] = evaluate(
    bundle,
    mappings["careTeamParticipants"],
  );
  if (careTeamParticipants.length === 0) {
    return undefined;
  }

  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Member", infoPath: "careTeamParticipantMemberName" },
    { columnName: "Role", infoPath: "careTeamParticipantRole" },
    {
      columnName: "Status",
      infoPath: "careTeamParticipantStatus",
      sentenceCase: true,
    },
    { columnName: "Dates", infoPath: "careTeamParticipantPeriod" },
  ];

  careTeamParticipants.forEach((entry) => {
    if (entry?.period) {
      const textArray: String[] = [];

      if (entry.period.start) {
        let startDate = formatDate(entry.period.start);
        if (startDate !== "Invalid Date") {
          textArray.push(`Start: ${startDate}`);
        }
      }

      if (entry.period.end) {
        let endDate = formatDate(entry.period.end);
        if (endDate !== "Invalid Date") {
          textArray.push(`End: ${endDate}`);
        }
      }

      (entry.period as any).text = textArray.join(" ");
    }

    const practitioner = evaluateReference(
      bundle,
      mappings,
      entry?.member?.reference || "",
    ) as Practitioner;
    const practitionerNameObj = practitioner.name?.find(
      (nameObject) => nameObject.family,
    );
    if (entry.member) {
      (entry.member as any).name = formatName(
        practitionerNameObj?.given,
        practitionerNameObj?.family,
        practitionerNameObj?.prefix,
        practitionerNameObj?.suffix,
      );
    }
  });

  return evaluateTable(
    careTeamParticipants as FhirResource[],
    mappings,
    columnInfo,
    "Care Team",
    false,
  );
};

/**
 * Generates a formatted table representing the list of procedures based on the provided array of procedures and mappings.
 * @param proceduresArray - An array containing the list of procedures.
 * @param mappings - An object containing FHIR path mappings for procedure attributes.
 * @returns - A formatted table React element representing the list of procedures, or undefined if the procedures array is empty.
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

  return evaluateTable(proceduresArray, mappings, columnInfo, "Procedures");
};

/**
 * Generates a formatted table representing the list of planned procedures
 * @param carePlanActivities - An array containing the list of procedures.
 * @param mappings - An object containing FHIR path mappings for procedure attributes.
 * @returns - A formatted table React element representing the list of planned procedures, or undefined if the procedures array is empty.
 */
export const returnPlannedProceduresTable = (
  carePlanActivities: CarePlanActivity[],
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  carePlanActivities = carePlanActivities.filter(
    (entry) => entry.detail?.code?.coding?.[0]?.display,
  );
  if (carePlanActivities.length === 0) {
    return undefined;
  }

  const columnInfo: ColumnInfoInput[] = [
    { columnName: "Procedure Name", infoPath: "plannedProcedureName" },
    { columnName: "Ordered Date", infoPath: "plannedProcedureOrderedDate" },
    { columnName: "Scheduled Date", infoPath: "plannedProcedureScheduledDate" },
  ];

  carePlanActivities.forEach((entry) => {
    if (entry.extension) {
      const orderedDateIndex = entry.extension.findIndex(
        (extension) => extension.url === "dibbs.orderedDate",
      );

      if (orderedDateIndex !== -1) {
        entry.extension[orderedDateIndex].valueString = formatDate(
          entry.extension[orderedDateIndex].valueString,
        );
      }
    }

    if (entry.detail) {
      entry.detail.scheduledString = formatDate(entry.detail.scheduledString);
    }
  });

  return evaluateTable(
    carePlanActivities,
    mappings,
    columnInfo,
    "Planned Procedures",
  );
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
        fhirBundle,
        evaluate(fhirBundle, mappings["activeProblems"]),
        mappings,
      ),
    },
  ];

  const pendingResults = returnPendingResultsTable(fhirBundle, mappings);
  let planOfTreatmentElement: React.JSX.Element | undefined = undefined;
  if (pendingResults) {
    planOfTreatmentElement = (
      <>
        <div className={"data-title margin-bottom-1"}>Plan of Treatment</div>
        {pendingResults}
      </>
    );
  }

  const treatmentData: DisplayData[] = [
    {
      title: "Plan of Treatment",
      value: planOfTreatmentElement,
    },
    {
      title: "Care Team",
      value: returnCareTeamTable(fhirBundle, mappings),
    },
    {
      title: "Procedures",
      value: returnProceduresTable(
        evaluate(fhirBundle, mappings["procedures"]),
        mappings,
      ),
    },
    {
      title: "Planned Procedures",
      value: returnPlannedProceduresTable(
        evaluate(fhirBundle, mappings["plannedProcedures"]),
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
 * @param data - An array of display data items to be evaluated.
 * @returns - An object containing arrays of available and unavailable display data items.
 */
export const evaluateData = (data: DisplayData[]): CompleteData => {
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

/**
 * Functional component for displaying data.
 * @param props - Props for the component.
 * @param props.item - The display data item to be rendered.
 * @param [props.className] - Additional class name for styling purposes.
 * @returns - A React element representing the display of data.
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
  item.dividerLine =
    item.dividerLine == null || item.dividerLine == undefined
      ? true
      : item.dividerLine;
  return (
    <div>
      <div className="grid-row">
        {item.title ? <div className="data-title">{item.title}</div> : ""}
        <div
          className={classNames(
            "grid-col-auto maxw7 text-pre-line",
            className,
            item.className ? item.className : "",
          )}
        >
          {item.value}
        </div>
      </div>
      {item.dividerLine ? <div className={"section__line_gray"} /> : ""}
    </div>
  );
};

export const DataTableDisplay: React.FC<{ item: DisplayData }> = ({
  item,
}): React.JSX.Element => {
  return (
    <div className="grid-row">
      <div className="grid-col-auto width-full text-pre-line">{item.value}</div>
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
