"use server";
import { v4 as uuidv4 } from "uuid";
import https from "https";
import fetch, { RequestInit } from "node-fetch";
import {
  Patient,
  Observation,
  DiagnosticReport,
  Condition,
  Encounter,
} from "fhir/r4";

type FHIR_SERVERS = "meld" | "ehealthexchange";

type USE_CASES =
  | "social-determinants"
  | "newborn-screening"
  | "syphilis"
  | "cancer";

const FHIR_SERVERS: {
  [key: string]: {
    hostname: string;
    username?: string;
    password?: string;
    headers?: { [key: string]: string };
  };
} = {
  // https://gw.interop.community/skylightsandbox/open/
  meld: { hostname: "https://gw.interop.community/HeliosConnectathonSa/open/" },
  ehealthexchange: {
    hostname: "https://concept01.ehealthexchange.org:52780/fhirproxy/r4/",
    username: "svc_eHxFHIRSandbox",
    password: "willfulStrongStandurd7",
    headers: {
      Accept: "application/json, application/*+json, */*",
      "Accept-Encoding": "gzip, deflate, br",
      "Content-Type": "application/fhir+json; charset=UTF-8",
      "X-DESTINATION": "CernerHelios",
      "X-POU": "TREATMENT",
      "X-Request-Id": uuidv4(),
      prefer: "return=representation",
      "Cache-Control": "no-cache",
      OAUTHSCOPES:
        "system/Condition.read system/Encounter.read system/" +
        "Immunization.read system/MedicationRequest.read system/" +
        "Observation.read system/Patient.read system/Procedure" +
        ".read system/MedicationAdministration.read system/" +
        "DiagnosticReport.read system/RelatedPerson.read",
    },
  },
};

type UseCaseQueryRequest = {
  use_case: USE_CASES;
  fhir_server: FHIR_SERVERS;
  first_name: string;
  last_name: string;
  dob: string;
  fhir_host?: string;
  init?: RequestInit;
  headers?: { [key: string]: string };
  patientId?: string;
};

type QueryResponse = {
  patients?: Patient[];
  observations?: Observation[];
  diagnosticReports?: DiagnosticReport[];
  conditions?: Condition[];
  encounters?: Encounter[];
};

const useCaseQueryMap: {
  [key in USE_CASES]: (
    input: UseCaseQueryRequest,
    queryResponse: QueryResponse,
  ) => Promise<void>;
} = {
  "social-determinants": socialDeterminantsQuery,
  "newborn-screening": newbornScreeningQuery,
  syphilis: syphilisQuery,
  cancer: async () => {
    throw new Error("Not implemented");
  },
};

// Expected responses from the FHIR server
export type UseCaseQueryResponse = Awaited<ReturnType<typeof useCaseQuery>>;

/**
 * Given a UseCaseQueryRequest object, set the appropriate FHIR server connection
 * configurations.
 * @param request - The request object to configure.
 * @returns
 */
function configureFHIRServerConnection(request: UseCaseQueryRequest): void {
  request.fhir_host = FHIR_SERVERS[request.fhir_server].hostname;
  request.headers = FHIR_SERVERS[request.fhir_server].headers || {};

  // Set up init object for eHealth Exchange
  request.init = {};

  // Add username to headers if it exists in input.fhir_server
  if (
    FHIR_SERVERS[request.fhir_server].username &&
    FHIR_SERVERS[request.fhir_server].password
  ) {
    const credentials = btoa(
      `${FHIR_SERVERS[request.fhir_server].username}:${
        FHIR_SERVERS[request.fhir_server].password || ""
      }`,
    );
    request.headers.Authorization = `Basic ${credentials}`;
    request.init.agent = new https.Agent({
      rejectUnauthorized: false,
    });
  }
}

/**
 * Query a FHIR server for a patient based on demographics provided in the request. If
 * a patient is found, store in the queryResponse object.
 * @param request - The request object containing the patient demographics.
 * @param queryResponse - The response object to store the patient.
 * @returns - The response body from the FHIR server.
 */
async function patientQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<{ responseBody: any }> {
  // Query for patient
  const query = `Patient?given=${request.first_name}&family=${request.last_name}&birthdate=${request.dob}`;
  const response = await fetch(request.fhir_host + query, {
    headers: request.headers,
    ...request.init,
  });

  // Check for errors
  if (response.status !== 200) {
    console.log("response:", response);
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }

  const responseBody = await response.json();
  queryResponse.patients = responseBody.entry.map(
    (entry: any) => entry.resource,
  );

  if (responseBody.total === 0) {
    throw new Error("No patient found.");
  } else if (responseBody.total > 1) {
    throw new Error("Multiple patients found. Please refine your search.");
  }

  return { responseBody };
}

/**
 * Query a FHIR API for a public health use case based on patient demographics provided
 * in the request. If data is found, return in a queryResponse object.
 * @param request - The request object containing the patient demographics.
 * @param input
 * @returns - The response object containing the query results.
 */
export async function useCaseQuery(
  input: UseCaseQueryRequest,
): Promise<QueryResponse> {
  console.log("input:", input);

  configureFHIRServerConnection(input);

  const queryResponse: QueryResponse = {};
  const { responseBody } = await patientQuery(input, queryResponse);
  input.patientId = responseBody.entry[0].resource.id;

  await useCaseQueryMap[input.use_case](input, queryResponse);

  return queryResponse;
}

/**
 * Social Determinant of Health use case query.
 * @param request - The request object containing the patient ID.
 * @param input
 * @param queryResponse - The response object to store the results
 * @returns
 */
async function socialDeterminantsQuery(
  input: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<void> {
  const query = `/Observation?subject=${input.patientId}&category=social-history`;
  const response = await fetch(input.fhir_host + query, input.init);

  // Check for errors
  if (response.status !== 200) {
    console.log("response:", response);
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }
  queryResponse.observations = (await response.json()).entry.map(
    (entry: any) => entry.resource,
  );
}

/**
 * Newborn Screening use case query.
 * @param request - The request object containing the patient ID.
 * @param input
 * @param queryResponse - The response object to store the results
 * @returns
 */
async function newbornScreeningQuery(
  input: UseCaseQueryRequest,
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

  const query = `/Observation?subject=${input.patientId}&code=${loincFilter}`;
  const response = await fetch(input.fhir_host + query, input.init);

  if (response.status !== 200) {
    console.log("response:", response);
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }

  queryResponse.observations = (await response.json()).entry.map(
    (entry: any) => entry.resource,
  );
}

/**
 * Syphilis use case query.
 * @param request - The request object containing the patient ID.
 * @param input
 * @param queryResponse - The response object to store the results
 * @returns
 */
async function syphilisQuery(
  input: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<void> {
  const loincs: Array<string> = ["LP70657-9", "98212-4"];
  const snomed: Array<string> = ["76272004"];
  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");

  const observationQuery = `/Observation?subject=${input.patientId}&code=${loincFilter}`;
  const observationResponse = await fetch(
    input.fhir_host + observationQuery,
    input.init,
  );
  if (observationResponse.status === 200) {
    queryResponse.observations = (await observationResponse.json()).entry.map(
      (entry: any) => entry.resource,
    );
  }

  const diagnositicReportQuery = `/DiagnosticReport?subject=${input.patientId}&code=${loincFilter}`;
  const diagnositicReportResponse = await fetch(
    input.fhir_host + diagnositicReportQuery,
    input.init,
  );
  if (diagnositicReportResponse.status === 200) {
    queryResponse.diagnosticReports = (
      await diagnositicReportResponse.json()
    ).entry.map((entry: any) => entry.resource);
  }

  const conditionQuery = `/Condition?subject=${input.patientId}&code=${snomedFilter}`;
  const conditionResponse = await fetch(
    input.fhir_host + conditionQuery,
    input.init,
  );
  if (conditionResponse.status === 200) {
    queryResponse.conditions = (await conditionResponse.json()).entry.map(
      (entry: any) => entry.resource,
    );
  }

  if (queryResponse.conditions && queryResponse.conditions.length === 0) {
    const conditionId = queryResponse.conditions[0].id;
    const encounterQuery = `/Encounter?subject=${input.patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fetch(
      input.fhir_host + encounterQuery,
      input.init,
    );
    if (encounterResponse.status === 200) {
      queryResponse.encounters = (await encounterResponse.json()).entry.map(
        (entry: any) => entry.resource,
      );
    }
  }
}
