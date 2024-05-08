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
  MedicationRequest,
  Resource,
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
    input: UseCaseQueryRequest,
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
): Promise<QueryResponse> {
  // Query for patient
  const query = `Patient?given=${request.first_name}&family=${request.last_name}&birthdate=${request.dob}`;
  const response = await fetch(request.fhir_host + query, {
    headers: request.headers,
    ...request.init,
  });

  // Check for errors
  if (response.status !== 200) {
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }
  queryResponse = {
    ...queryResponse,
    ...(await parseFhirSearch(response, ["Patient"])),
  };

  if (!queryResponse.Patient || queryResponse.Patient.length === 0) {
    throw new Error("No patient found.");
  } else if (queryResponse.Patient.length > 1) {
    throw new Error("Multiple patients found. Please refine your search.");
  }

  return queryResponse;
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

  const queryResponse = await patientQuery(request, {});
  request.patientId = queryResponse.Patient?.[0]?.id ?? "";

  return await useCaseQueryMap[request.use_case](request, queryResponse);
}

/**
 * Social Determinant of Health use case query.
 * @param request - The request object containing the patient ID.
 * @param queryResponse - The response object to store the results
 * @returns - The response object containing the query results.
 */
async function socialDeterminantsQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const query = `/Observation?subject=${request.patientId}&category=social-history`;
  const response = await fetch(request.fhir_host + query, request.init);
  return {
    ...queryResponse,
    ...(await parseFhirSearch(response, ["Observation"])),
  };
}

/**
 * Newborn Screening use case query.
 * @param request - The request object containing the patient ID.
 * @param queryResponse - The response object to store the results
 * @returns - The response object containing the query results.
 */
async function newbornScreeningQuery(
  request: UseCaseQueryRequest,
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

  const query = `/Observation?subject=Patient/${request.patientId}&code=${loincFilter}`;
  const response = await fetch(request.fhir_host + query, {
    headers: request.headers,
    ...request.init,
  });

  return {
    ...queryResponse,
    ...(await parseFhirSearch(response, ["Observation"])),
  };
}

/**
 * Syphilis use case query.
 * @param request - The request object containing the patient ID.
 * @param queryResponse - The response object to store the results
 * @returns - The response object containing the query results.
 */
async function syphilisQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const loincs: Array<string> = ["LP70657-9", "98212-4"];
  const snomed: Array<string> = ["76272004"];
  const rxnorm: Array<string> = ["2671695"]; // drug codes from NLM/NIH RxNorm
  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");

  const observationQuery = `/Observation?subject=${request.patientId}&code=${loincFilter}`;
  const observationResponse = await fetch(
    request.fhir_host + observationQuery,
    request.init,
  );
  queryResponse = {
    ...queryResponse,
    ...(await parseFhirSearch(observationResponse, ["Observation"])),
  };

  const diagnositicReportQuery = `/DiagnosticReport?subject=${request.patientId}&code=${loincFilter}`;
  const diagnositicReportResponse = await fetch(
    request.fhir_host + diagnositicReportQuery,
    request.init,
  );
  queryResponse = {
    ...queryResponse,
    ...(await parseFhirSearch(diagnositicReportResponse, ["DiagnosticReport"])),
  };

  // Query for conditions
  const conditionQuery = `/Condition?subject=${request.patientId}&code=${snomedFilter}`;
  const conditionResponse = await fetch(
    request.fhir_host + conditionQuery,
    request.init,
  );
  const conditions = await parseFhirSearch(conditionResponse, ["Condition"]);
  queryResponse = {
    ...queryResponse,
    ...conditions,
  };

  // Query for encounters. TODO: Add encounters as _include in condition query
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    const encounterQuery = `/Encounter?subject=${request.patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fetch(
      request.fhir_host + encounterQuery,
      request.init,
    );

    queryResponse = {
      ...queryResponse,
      ...(await parseFhirSearch(encounterResponse, ["Encounter"])),
    };
  }
  // Query for medicationRequests
  const medicationRequestQuery = `/MedicationRequest?subject=${request.patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`;
  const medicationRequestResponse = await fetch(
    request.fhir_host + medicationRequestQuery,
    request.init,
  );
  return {
    ...queryResponse,
    ...(await parseFhirSearch(medicationRequestResponse, [
      "MedicationRequest",
      "Medication",
      "MedicationAdministration",
    ])),
  };
}

/**
 * Cancer use case query.
 * @param request - The request object containing the patient ID.
 * @param queryResponse - The response object to store the results
 * @returns - The response object containing the query results.
 */
async function cancerQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const snomed: Array<string> = ["92814006"];
  const rxnorm: Array<string> = ["828265"]; // drug codes from NLM/NIH RxNorm
  const cpt: Array<string> = ["15301000"]; // encounter codes from AMA CPT
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");
  const cptFilter: string = cpt.join(",");

  // Query for conditions and encounters
  const conditionQuery = `/Condition?subject=${request.patientId}&code=${snomedFilter}`;
  const conditionResponse = await fetch(
    request.fhir_host + conditionQuery,
    request.init,
  );
  queryResponse = {
    ...queryResponse,
    ...(await parseFhirSearch(conditionResponse, ["Condition"])),
  };

  // Query for encounters
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    const encounterQuery = `/Encounter?subject=${request.patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fetch(
      request.fhir_host + encounterQuery,
      request.init,
    );
    queryResponse = {
      ...queryResponse,
      ...(await parseFhirSearch(encounterResponse, ["Encounter"])),
    };
  }

  const medicationRequestQuery = `/MedicationRequest?subject=${request.patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`;
  const medicationRequestResponse = await fetch(
    request.fhir_host + medicationRequestQuery,
    request.init,
  );
  return {
    ...queryResponse,
    ...(await parseFhirSearch(medicationRequestResponse, [
      "MedicationRequest",
      "Medication",
      "MedicationAdministration",
    ])),
  };
}

/**
 * Parse the response from a FHIR search query. If the response is successful and
 * contains data, return an array of resources.
 * @param response - The response from the FHIR server.
 * @param resourceTypes - The type of resource to parse.
 * @returns - The parsed response.
 */
async function parseFhirSearch(
  response: fetch.Response,
  resourceTypes: Array<string>,
): Promise<Record<string, Resource[]>> {
  const output: Record<string, Resource[]> = {};
  for (const rt of resourceTypes) {
    output[rt] = [];
  }
  // TODO: Handle _include & _revinclude queries
  if (response.status === 200) {
    const body = await response.json();
    if (body.entry) {
      for (const entry of body.entry) {
        if (resourceTypes.includes(entry.resource.resourceType)) {
          output[entry.resource.resourceType as string].push(entry.resource);
        }
      }
    }
  }
  return output;
}
