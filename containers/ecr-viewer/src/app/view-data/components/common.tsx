import {
  calculatePatientAge,
  evaluateReference,
} from "@/app/services/evaluateFhirDataService";
import EvaluateTable from "@/app/view-data/components/EvaluateTable";
import {
  formatName,
  formatVitals,
  formatDate,
} from "@/app/services/formatService";
import {
  ColumnInfoInput,
  PathMappings,
  evaluateData,
  noData,
} from "@/app/utils";
import { Table } from "@trussworks/react-uswds";
import {
  Bundle,
  CarePlanActivity,
  CareTeamParticipant,
  Condition,
  FhirResource,
  Immunization,
  Organization,
  Practitioner,
  Procedure,
} from "fhir/r4";
import { evaluate } from "@/app/view-data/utils/evaluate";
import parse from "html-react-parser";
import { DisplayDataProps } from "@/app/DataDisplay";
import {
  formatTablesToJSON,
  TableRow,
} from "@/app/services/formatTablesToJSON";
import { JSDOM } from "jsdom";
import DOMPurify from "dompurify";

/**
 * Returns a table displaying administered medication information.
 * @param fhirBundle - The FHIR bundle containing care team data.
 * @param mappings - The object containing the fhir paths.
 * @returns The JSX element representing the table, or undefined if no administed medications are found.
 */
export const returnAdminMedTable = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const adminMedTables = formatTablesToJSON(
    evaluate(fhirBundle, mappings["administeredMedications"])[0]?.div,
  );
  const adminMedJson = adminMedTables[0]?.tables?.[0];
  if (
    adminMedJson &&
    adminMedJson[0]["Medication Name"] &&
    adminMedJson[0]["Medication Start Date"]
  ) {
    const header = ["Medication Name", "Medication Start Date"];
    return (
      <Table
        bordered={false}
        fullWidth={true}
        caption="Administered Medications"
        className={
          "table-caption-margin margin-y-0 border-top border-left border-right"
        }
        data-testid="table"
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
          {adminMedJson.map((entry: TableRow, index: number) => {
            const entryDate = entry["Medication Start Date"].value;
            const formattedDate = formatDate(entryDate);
            return (
              <tr key={`table-row-${index}`}>
                <td>{entry["Medication Name"]?.value ?? noData}</td>
                <td>{formattedDate ?? noData}</td>
              </tr>
            );
          })}
        </tbody>
      </Table>
    );
  }
};

/**
 * Returns a table displaying care team information.
 * @param bundle - The FHIR bundle containing care team data.
 * @param mappings - The object containing the fhir paths.
 * @returns The JSX element representing the care team table, or undefined if no care team participants are found.
 */
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
      applyToValue: "toSentenceCase",
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
  return (
    <EvaluateTable
      resources={careTeamParticipants as FhirResource[]}
      mappings={mappings}
      columns={columnInfo}
      caption={"Care Team"}
      fixed={false}
    />
  );
};

/**
 * Generates a formatted table representing the list of immunizations based on the provided array of immunizations and mappings.
 * @param fhirBundle - The FHIR bundle containing patient and immunizations information.
 * @param immunizationsArray - An array containing the list of immunizations.
 * @param mappings - An object containing the FHIR path mappings.
 * @returns - A formatted table React element representing the list of immunizations, or undefined if the immunizations array is empty.
 */
export const returnImmunizations = (
  fhirBundle: Bundle,
  immunizationsArray: Immunization[],
  mappings: PathMappings,
): React.JSX.Element | undefined => {
  if (immunizationsArray.length === 0) {
    return undefined;
  }

  const columnInfo = [
    { columnName: "Name", infoPath: "immunizationsName" },
    { columnName: "Administration Dates", infoPath: "immunizationsAdminDate" },
    { columnName: "Dose Number", infoPath: "immunizationsDoseNumber" },
    {
      columnName: "Manufacturer",
      infoPath: "immunizationsManufacturerName",
    },
    { columnName: "Lot Number", infoPath: "immunizationsLotNumber" },
  ];

  immunizationsArray.forEach((entry) => {
    entry.occurrenceDateTime = formatDate(entry.occurrenceDateTime);

    const manufacturer = evaluateReference(
      fhirBundle,
      mappings,
      entry.manufacturer?.reference || "",
    ) as Organization;
    if (manufacturer) {
      (entry.manufacturer as any).name = manufacturer.name || "";
    }
  });

  immunizationsArray.sort(
    (a, b) =>
      new Date(b.occurrenceDateTime ?? "").getTime() -
      new Date(a.occurrenceDateTime ?? "").getTime(),
  );
  return (
    <EvaluateTable
      resources={immunizationsArray}
      mappings={mappings}
      columns={columnInfo}
      caption={"Immunization History"}
    />
  );
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
  problemsArray = problemsArray.filter(
    (entry) => entry.code?.coding?.[0].display,
  );

  if (problemsArray.length === 0) {
    return undefined;
  }

  const columnInfo: ColumnInfoInput[] = [
    {
      columnName: "Active Problem",
      infoPath: "activeProblemsDisplay",
      className: "width-mobile-lg",
    },
    { columnName: "Onset Date", infoPath: "activeProblemsOnsetDate" },
    { columnName: "Onset Age", infoPath: "activeProblemsOnsetAge" },
  ];

  problemsArray.forEach((entry) => {
    entry.onsetDateTime = formatDate(entry.onsetDateTime);
    entry.onsetAge = {
      value: calculatePatientAge(fhirBundle, mappings, entry.onsetDateTime),
    };
  });

  if (problemsArray.length === 0) {
    return undefined;
  }

  problemsArray.sort(
    (a, b) =>
      new Date(b.onsetDateTime ?? "").getTime() -
      new Date(a.onsetDateTime ?? "").getTime(),
  );

  return (
    <EvaluateTable
      resources={problemsArray}
      mappings={mappings}
      columns={columnInfo}
      caption={"Problems List"}
      fixed={false}
    />
  );
};

/**
 * Returns a table displaying pending results information.
 * @param fhirBundle - The FHIR bundle containing care team data.
 * @param mappings - The object containing the fhir paths.
 * @returns The JSX element representing the table, or undefined if no pending results are found.
 */
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
          "table-caption-margin caption-normal-weight margin-top-0 border-top border-left border-right margin-bottom-2"
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
 * Returns a table displaying scheduled order information.
 * @param fhirBundle - The FHIR bundle containing care team data.
 * @param mappings - The object containing the fhir paths.
 * @returns The JSX element representing the table, or undefined if no scheduled orders are found.
 */
export const returnScheduledOrdersTable = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const planOfTreatmentTables = formatTablesToJSON(
    evaluate(fhirBundle, mappings["planOfTreatment"])[0]?.div,
  );
  const scheduledOrdersTableJson = planOfTreatmentTables.find(
    (val) => val.resultName === "Scheduled Orders",
  );

  if (scheduledOrdersTableJson?.tables?.[0]) {
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
          "table-caption-margin margin-top-1 caption-normal-weight margin-y-0 border-top border-left border-right"
        }
        data-testid="table"
        caption={"Scheduled Orders"}
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
          {scheduledOrdersTableJson.tables[0].map(
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

  return (
    <EvaluateTable
      resources={proceduresArray}
      mappings={mappings}
      columns={columnInfo}
      caption={"Procedures"}
    />
  );
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
    {
      columnName: "Ordered Date",
      infoPath: "plannedProcedureOrderedDate",
      applyToValue: "formatDate",
    },
    {
      columnName: "Scheduled Date",
      infoPath: "plannedProcedureScheduledDate",
      applyToValue: "formatDate",
    },
  ];

  return (
    <EvaluateTable
      resources={carePlanActivities}
      mappings={mappings}
      columns={columnInfo}
      caption={"Planned Procedures"}
    />
  );
};

/**
 * Evaluates clinical data from the FHIR bundle and formats it into structured data for display.
 * @param fhirBundle - The FHIR bundle containing clinical data.
 * @param mappings - The object containing the fhir paths.
 * @returns An object containing evaluated and formatted clinical data.
 * @property {DisplayDataProps[]} clinicalNotes - Clinical notes data.
 * @property {DisplayDataProps[]} reasonForVisitDetails - Reason for visit details.
 * @property {DisplayDataProps[]} activeProblemsDetails - Active problems details.
 * @property {DisplayDataProps[]} treatmentData - Treatment-related data.
 * @property {DisplayDataProps[]} vitalData - Vital signs data.
 * @property {DisplayDataProps[]} immunizationsDetails - Immunization details.
 */
export const evaluateClinicalData = (
  fhirBundle: Bundle,
  mappings: PathMappings,
) => {
  const htmlString = evaluate(
    fhirBundle,
    mappings["historyOfPresentIllness"],
  )[0]?.div;
  const window = new JSDOM("").window;
  const purify = DOMPurify(window);
  const cleanMiscNotes = purify.sanitize(htmlString);

  const clinicalNotes: DisplayDataProps[] = [
    {
      title: "Miscellaneous Notes",
      value: parse(cleanMiscNotes),
    },
  ];

  const reasonForVisitData: DisplayDataProps[] = [
    {
      title: "Reason for Visit",
      value: evaluate(fhirBundle, mappings["clinicalReasonForVisit"])[0],
    },
  ];

  const activeProblemsTableData: DisplayDataProps[] = [
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
  const scheduledOrders = returnScheduledOrdersTable(fhirBundle, mappings);
  let planOfTreatmentElement: React.JSX.Element | undefined = undefined;
  if (pendingResults) {
    planOfTreatmentElement = (
      <>
        <div className={"data-title margin-bottom-1"}>Plan of Treatment</div>
        {pendingResults}
        {scheduledOrders}
      </>
    );
  }

  const adminMedResults = returnAdminMedTable(fhirBundle, mappings);
  let adminMedElement: React.JSX.Element | undefined = adminMedResults ? (
    <>{adminMedResults}</>
  ) : undefined;

  const treatmentData: DisplayDataProps[] = [
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
    {
      title: "Plan of Treatment",
      value: planOfTreatmentElement,
    },
    {
      title: "Administered Medications",
      value: adminMedElement,
    },
    {
      title: "Care Team",
      value: returnCareTeamTable(fhirBundle, mappings),
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

  const immunizationsData: DisplayDataProps[] = [
    {
      title: "Immunization History",
      value: returnImmunizations(
        fhirBundle,
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
