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
  Medication,
  MedicationAdministration,
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
    headers: {
      Accept: "application/json, application/*+json, */*",
      "Accept-Encoding": "gzip, deflate, br",
      "Content-Type": "application/fhir+json; charset=UTF-8",
      "X-DESTINATION": "CernerHelios",
      "X-POU": "PUBHLTH",
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
  medications?: Medication[];
  medicationAdmins?: MedicationAdministration[];
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
  cancer: cancerQuery,
};

// Expected responses from the FHIR server
export type UseCaseQueryResponse = Awaited<ReturnType<typeof useCaseQuery>>;

/**
 * Given a UseCaseQueryRequest object, set the appropriate FHIR server connection
 * configurations.
 * @param request - The request object to configure.
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
 * @param request - UseCaseQueryRequest object containing the patient demographics and use case.
 * @returns - The response object containing the query results.
 */
export async function useCaseQuery(
  request: UseCaseQueryRequest,
): Promise<QueryResponse> {
  console.log("input:", request);

  configureFHIRServerConnection(request);

  const queryResponse: QueryResponse = {};
  const { responseBody } = await patientQuery(request, queryResponse);
  request.patientId = responseBody.entry[0].resource.id;

  await useCaseQueryMap[request.use_case](request, queryResponse);

  return queryResponse;
}

/**
 * Social Determinant of Health use case query.
 * @param request - The request object containing the patient ID.
 * @param queryResponse - The response object to store the results
 */
async function socialDeterminantsQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<void> {
  const query = `/Observation?subject=${request.patientId}&category=social-history`;
  const response = await fetch(request.fhir_host + query, request.init);

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
 * @param queryResponse - The response object to store the results
 */
async function newbornScreeningQuery(
  request: UseCaseQueryRequest,
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

  const query = `/Observation?subject=Patient/${request.patientId}&code=${loincFilter}`;
  const response = await fetch(request.fhir_host + query, {
    headers: request.headers,
    ...request.init,
  });

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
 * @param queryResponse - The response object to store the results
 */
async function syphilisQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<void> {
  const loincs: Array<string> = ["LP70657-9", "98212-4"];
  const snomed: Array<string> = ["76272004"];
  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");

  const observationQuery = `/Observation?subject=${request.patientId}&code=${loincFilter}`;
  const observationResponse = await fetch(
    request.fhir_host + observationQuery,
    request.init,
  );
  if (observationResponse.status === 200) {
    queryResponse.observations = (await observationResponse.json()).entry.map(
      (entry: any) => entry.resource,
    );
  }

  const diagnositicReportQuery = `/DiagnosticReport?subject=${request.patientId}&code=${loincFilter}`;
  const diagnositicReportResponse = await fetch(
    request.fhir_host + diagnositicReportQuery,
    request.init,
  );
  if (diagnositicReportResponse.status === 200) {
    queryResponse.diagnosticReports = (
      await diagnositicReportResponse.json()
    ).entry.map((entry: any) => entry.resource);
  }

  const conditionQuery = `/Condition?subject=${request.patientId}&code=${snomedFilter}`;
  const conditionResponse = await fetch(
    request.fhir_host + conditionQuery,
    request.init,
  );
  if (conditionResponse.status === 200) {
    queryResponse.conditions = (await conditionResponse.json()).entry.map(
      (entry: any) => entry.resource,
    );
  }

  if (queryResponse.conditions && queryResponse.conditions.length === 0) {
    const conditionId = queryResponse.conditions[0].id;
    const encounterQuery = `/Encounter?subject=${request.patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fetch(
      request.fhir_host + encounterQuery,
      request.init,
    );
    if (encounterResponse.status === 200) {
      queryResponse.encounters = (await encounterResponse.json()).entry.map(
        (entry: any) => entry.resource,
      );
    }
  }
}

/**
 * Cancer use case query.
 * @param request - The request object containing the patient ID.
 * @param queryResponse - The response object to store the results
 */
async function cancerQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<void> {
  const snomed: Array<string> = ["92814006"];
  const rxnorm: Array<string> = ["828265"]; // drug codes from NLM/NIH RxNorm
  const cpt: Array<string> = ["15301000"]; // encounter codes from AMA CPT
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");
  const cptFilter: string = cpt.join(",");

  // Query for conditions
  const conditionQuery = `/Condition?subject=${request.patientId}&code=${snomedFilter}`;
  const conditionResponse = await fetch(
    request.fhir_host + conditionQuery,
    request.init,
  );
  if (conditionResponse.status === 200) {
    queryResponse.conditions = (await conditionResponse.json()).entry.map(
      (entry: any) => entry.resource,
    );
  }

  // Query for encounters
  if (queryResponse.conditions && queryResponse.conditions.length === 0) {
    const conditionId = queryResponse.conditions[0].id;
    const encounterQuery = `/Encounter?subject=${request.patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fetch(
      request.fhir_host + encounterQuery,
      request.init,
    );
    if (encounterResponse.status === 200) {
      queryResponse.encounters = (await encounterResponse.json()).entry.map(
        (entry: any) => entry.resource,
      );
    }
  }

  // Query for medications
  // type medicationResponse = {
  //   entry: Record<string, unknown>[];
  // } & Record<string, unknown>;

  const medicationsQuery = `/MedicationRequest?subject=Patient/${request.patientId}&code=${rxnormFilter}`;
  const medicationResponse = await fetch(
    request.fhir_host + medicationsQuery,
    request.init,
  );
  if (medicationResponse.status >= 400) {
    throw new Error(
      `Error querying medications. Status: ${medicationResponse.status}`,
    );
  }
  const m = await medicationResponse.json();
  queryResponse.medications = m.entry.map((entry: any) => entry.resource);

  // Query for medication administrations
  const medicationsAdministered: Array<string> = m.entry.map(
    (medication: { resource: { id: string } }) => medication.resource.id,
  );
  const medicationFilter: string = medicationsAdministered.join(",");
  const medicationsAdminQuery = `/MedicationAdministration?subject=Patient/${request.patientId}&request=${medicationFilter}`;
  const medicationAdminResponse = await fetch(
    request.fhir_host + medicationsAdminQuery,
    request.init,
  );
  if (medicationAdminResponse.status === 200) {
    queryResponse.medicationAdmins = (
      await medicationAdminResponse.json()
    ).entry.map((entry: any) => entry.resource);
  }
}
