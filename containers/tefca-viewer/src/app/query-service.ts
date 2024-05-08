"use server";
import fetch from "node-fetch";
import {
  Patient,
  Observation,
  DiagnosticReport,
  Condition,
  Encounter,
  Medication,
  MedicationAdministration,
  Resource,
} from "fhir/r4";
import FHIRClient, { FHIR_SERVERS } from "./fhir-servers";

type USE_CASES =
  | "social-determinants"
  | "newborn-screening"
  | "syphilis"
  | "cancer";

type UseCaseQueryRequest = {
  use_case: USE_CASES;
  fhir_server: FHIR_SERVERS;
  first_name: string;
  last_name: string;
  dob: string;
};

type QueryResponse = {
  patients?: Patient[];
  observations?: Observation[];
  diagnosticReports?: DiagnosticReport[];
  conditions?: Condition[];
  encounters?: Encounter[];
  medications?: Medication[];
  medicationAdmins?: MedicationAdministration[];
};

const useCaseQueryMap: {
  [key in USE_CASES]: (
    patientId: string,
    fhirClient: FHIRClient,
    queryResponse: QueryResponse,
  ) => Promise<void>;
} = {
  "social-determinants": socialDeterminantsQuery,
  "newborn-screening": newbornScreeningQuery,
  syphilis: syphilisQuery,
  cancer: cancerQuery,
};

// Expected responses from the FHIR server
export type UseCaseQueryResponse = Awaited<ReturnType<typeof useCaseQuery>>;

/**
 * Query a FHIR server for a patient based on demographics provided in the request. If
 * a patient is found, store in the queryResponse object.
 * @param request - The request object containing the patient demographics.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the patient.
 * @returns - The response body from the FHIR server.
 */
async function patientQuery(
  request: UseCaseQueryRequest,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<void> {
  // Query for patient
  const query = `Patient?given=${request.first_name}&family=${request.last_name}&birthdate=${request.dob}`;
  const response = await fhirClient.get(query);

  // Check for errors
  if (response.status !== 200) {
    throw new Error(
      `Patient search failed. Status: ${response.status} \n ${await response.text()} \n Headers: ${JSON.stringify(response.headers.raw())}`,
    );
  }

  queryResponse.patients = (await parseFhirSearch(response)) as Patient[];

  if (queryResponse.patients.length === 0) {
    throw new Error("No patient found.");
  } else if (queryResponse.patients.length > 1) {
    throw new Error("Multiple patients found. Please refine your search.");
  }
}

/**
 * Query a FHIR API for a public health use case based on patient demographics provided
 * in the request. If data is found, return in a queryResponse object.
 * @param request - UseCaseQueryRequest object containing the patient demographics and use case.
 * @returns - The response object containing the query results.
 */
export async function useCaseQuery(
  request: UseCaseQueryRequest,
): Promise<QueryResponse> {
  const fhirClient = new FHIRClient(request.fhir_server);

  const queryResponse: QueryResponse = {};
  await patientQuery(request, fhirClient, queryResponse);
  const patientId = queryResponse.patients?.[0]?.id ?? "";

  await useCaseQueryMap[request.use_case](patientId, fhirClient, queryResponse);

  return queryResponse;
}

/**
 * Social Determinant of Health use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results
 */
async function socialDeterminantsQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<void> {
  const query = `/Observation?subject=${patientId}&category=social-history`;
  const response = await fhirClient.get(query);

  queryResponse.observations = (await parseFhirSearch(
    response,
  )) as Observation[];
}

/**
 * Newborn Screening use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results
 */
async function newbornScreeningQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<void> {
  const loincs: Array<string> = [
    "73700-7",
    "73698-3",
    "54108-6",
    "54109-4",
    "58232-0",
    "57700-7",
    "73739-5",
    "73742-9",
    "2708-6",
    "8336-0",
  ];
  const loincFilter: string = "code=" + loincs.join(",");

  const query = `/Observation?subject=Patient/${patientId}&code=${loincFilter}`;
  const response = await fhirClient.get(query);
  queryResponse.observations = (await parseFhirSearch(
    response,
  )) as Observation[];
}

/**
 * Syphilis use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results
 */
async function syphilisQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<void> {
  const loincs: Array<string> = ["LP70657-9", "98212-4"];
  const snomed: Array<string> = ["76272004"];
  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");

  const observationQuery = `/Observation?subject=${patientId}&code=${loincFilter}`;
  const observationResponse = await fhirClient.get(observationQuery);
  queryResponse.observations = (await parseFhirSearch(
    observationResponse,
  )) as Observation[];

  const diagnositicReportQuery = `/DiagnosticReport?subject=${patientId}&code=${loincFilter}`;
  const diagnositicReportResponse = await fhirClient.get(
    diagnositicReportQuery,
  );
  queryResponse.diagnosticReports = (await parseFhirSearch(
    diagnositicReportResponse,
  )) as DiagnosticReport[];

  const conditionQuery = `/Condition?subject=${patientId}&code=${snomedFilter}`;
  const conditionResponse = await fhirClient.get(conditionQuery);
  queryResponse.conditions = (await parseFhirSearch(
    conditionResponse,
  )) as Condition[];

  if (queryResponse.conditions && queryResponse.conditions.length > 0) {
    const conditionId = queryResponse.conditions[0].id;
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);
    queryResponse.encounters = (await parseFhirSearch(
      encounterResponse,
    )) as Encounter[];
  }
}

/**
 * Cancer use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results
 */
async function cancerQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<void> {
  const snomed: Array<string> = ["92814006"];
  const rxnorm: Array<string> = ["828265"]; // drug codes from NLM/NIH RxNorm
  const cpt: Array<string> = ["15301000"]; // encounter codes from AMA CPT
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");
  const cptFilter: string = cpt.join(",");

  // Query for conditions
  const conditionQuery = `/Condition?subject=${patientId}&code=${snomedFilter}`;
  const conditionResponse = await fhirClient.get(conditionQuery);
  queryResponse.conditions = (await parseFhirSearch(
    conditionResponse,
  )) as Condition[];

  // Query for encounters
  if (queryResponse.conditions && queryResponse.conditions.length > 0) {
    const conditionId = queryResponse.conditions[0].id;
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);
    queryResponse.encounters = (await parseFhirSearch(
      encounterResponse,
    )) as Encounter[];
  }

  // Query for medications
  // type medicationResponse = {
  //   entry: Record<string, unknown>[];
  // } & Record<string, unknown>;

  const medicationsQuery = `/MedicationRequest?subject=Patient/${patientId}&code=${rxnormFilter}`;
  const medicationResponse = await fhirClient.get(medicationsQuery);
  queryResponse.medications = (await parseFhirSearch(
    medicationResponse,
  )) as Medication[];

  // Query for medication administrations
  const medicationsAdministered = queryResponse.medications.map(
    (medication) => medication.id,
  );
  const medicationFilter: string = medicationsAdministered.join(",");
  const medicationsAdminQuery = `/MedicationAdministration?subject=Patient/${patientId}&request=${medicationFilter}`;
  const medicationAdminResponse = await fhirClient.get(medicationsAdminQuery);
  queryResponse.medicationAdmins = (await parseFhirSearch(
    medicationAdminResponse,
  )) as MedicationAdministration[];
}

/**
 * Parse the response from a FHIR search query. If the response is successful and
 * contains data, return an array of resources.
 * @param response - The response from the FHIR server.
 * @returns - The parsed response.
 */
async function parseFhirSearch(
  response: fetch.Response,
): Promise<Resource[] | []> {
  if (response.status === 200) {
    const body = await response.json();
    if (body.entry) {
      return body.entry.map((entry: any) => entry.resource);
    }
  }
  return [];
}
