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
  MedicationRequest,
} from "fhir/r4";
import FHIRClient, { FHIR_SERVERS } from "./fhir-servers";

export type USE_CASES =
  | "social-determinants"
  | "newborn-screening"
  | "syphilis"
  | "cancer";

export type UseCaseQueryRequest = {
  use_case: USE_CASES;
  fhir_server: FHIR_SERVERS;
  first_name?: string;
  last_name?: string;
  dob?: string;
};

export type QueryResponse = {
  Patient?: Patient[];
  Observation?: Observation[];
  DiagnosticReport?: DiagnosticReport[];
  Condition?: Condition[];
  Encounter?: Encounter[];
  Medication?: Medication[];
  MedicationAdministration?: MedicationAdministration[];
  MedicationRequest?: MedicationRequest[];

};

const useCaseQueryMap: {
  [key in USE_CASES]: (
    patientId: string,
    fhirClient: FHIRClient,
    queryResponse: QueryResponse,
  ) => Promise<QueryResponse>;
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
      `Patient search failed. Status: ${
        response.status
      } \n ${await response.text()} \n Headers: ${JSON.stringify(
        response.headers.raw(),
      )}`,
    );
  }
  queryResponse = await parseFhirSearch(response, queryResponse);

  queryResponse.patients = (await parseFhirSearch(response)) as Patient[];
}

/**
 * Query a FHIR API for a public health use case based on patient demographics provided
 * in the request. If data is found, return in a queryResponse object.
 * @param request - UseCaseQueryRequest object containing the patient demographics and use case.
 * @param queryResponse - The response object to store the query results.
 * @returns - The response object containing the query results.
 */
export async function useCaseQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse = {},
): Promise<QueryResponse> {
  const fhirClient = new FHIRClient(request.fhir_server);

  if (!queryResponse.patients || queryResponse.patients.length === 0) {
    await patientQuery(request, fhirClient, queryResponse);
  }

  if (!queryResponse.patients || queryResponse.patients.length === 0) {
    console.log("No patients found.");
    return queryResponse;
  } else if (queryResponse.patients.length > 1) {
    console.log("Multiple patients found.");
    return queryResponse;
  }

  const patientId = queryResponse.patients?.[0]?.id ?? "";

  await useCaseQueryMap[request.use_case](patientId, fhirClient, queryResponse);

  return queryResponse;
}

/**
 * Social Determinant of Health use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The response object containing the query results.
 */
async function socialDeterminantsQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const query = `/Observation?subject=${patientId}&category=social-history`;
  const response = await fhirClient.get(query);
  return await parseFhirSearch(response, queryResponse);
}

/**
 * Newborn Screening use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The response object containing the query results.
 */
async function newbornScreeningQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
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

  return await parseFhirSearch(response, queryResponse);
}

/**
 * Syphilis use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The response object containing the query results.
 */
async function syphilisQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const loincs: Array<string> = ["LP70657-9", "98212-4"];
  const snomed: Array<string> = ["76272004"];
  const rxnorm: Array<string> = ["2671695"]; // drug codes from NLM/NIH RxNorm
  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");

  const observationQuery = `/Observation?subject=${patientId}&code=${loincFilter}`;
  const observationResponse = await fhirClient.get(observationQuery);

  queryResponse = await parseFhirSearch(observationResponse, queryResponse);

  const diagnositicReportQuery = `/DiagnosticReport?subject=${patientId}&code=${loincFilter}`;
  const diagnositicReportResponse = await fhirClient.get(
    diagnositicReportQuery,
  );
  queryResponse = await parseFhirSearch(
    diagnositicReportResponse,
    queryResponse,
  );

  // Query for conditions
  const conditionQuery = `/Condition?subject=${patientId}&code=${snomedFilter}`;
  const conditionResponse = await fhirClient.get(conditionQuery);
  queryResponse = await parseFhirSearch(conditionResponse, queryResponse);

  // Query for encounters. TODO: Add encounters as _include in condition query
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);

    queryResponse = await parseFhirSearch(encounterResponse, queryResponse);
  }
  // Query for medicationRequests
  const medicationRequestQuery = `/MedicationRequest?subject=${patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`;
  const medicationRequestResponse = await fhirClient.get(
    medicationRequestQuery,
  );
  return await parseFhirSearch(medicationRequestResponse, queryResponse);
}

/**
 * Cancer use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The response object containing the query results.
 */
async function cancerQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const snomed: Array<string> = ["92814006"];
  const rxnorm: Array<string> = ["828265"]; // drug codes from NLM/NIH RxNorm
  const cpt: Array<string> = ["15301000"]; // encounter codes from AMA CPT
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");

  // Query for conditions and encounters
  const conditionQuery = `/Condition?subject=${patientId}&code=${snomedFilter}`;
  const conditionResponse = await fhirClient.get(conditionQuery);
  queryResponse = await parseFhirSearch(conditionResponse, queryResponse);

  // Query for encounters
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);
    queryResponse = await parseFhirSearch(encounterResponse, queryResponse);
  }

  // Query for medications & medication requests
  const medicationRequestQuery = `/MedicationRequest?subject=${patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`;
  const medicationRequestResponse = await fhirClient.get(
    medicationRequestQuery,
  );
  return await parseFhirSearch(medicationRequestResponse, queryResponse);
}

/**
 * Parse the response from a FHIR search query. If the response is successful and
 * contains data, return an array of resources.
 * @param response - The response from the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The parsed response.
 */
async function parseFhirSearch(
  response: fetch.Response,
  queryResponse: QueryResponse = {},
): Promise<QueryResponse> {
  if (response.status === 200) {
    const body = await response.json();
    if (body.entry) {
      for (const entry of body.entry) {
        const resourceType = entry.resource.resourceType as keyof QueryResponse;
        if (!queryResponse[resourceType]) {
          queryResponse[resourceType] = [entry.resource];
        } else {
          queryResponse[resourceType]!.push(entry.resource);
        }
      }
    }
  }
  return queryResponse;
}
