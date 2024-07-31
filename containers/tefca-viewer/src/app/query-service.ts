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
  Bundle,
} from "fhir/r4";

import FHIRClient from "./fhir-servers";
import { USE_CASES, FHIR_SERVERS } from "./constants";

import { CustomQuery } from "./CustomQuery";

import * as fs from "fs";

/**
 * The query response when the request source is from the Viewer UI.
 */
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

export type APIQueryResponse = Bundle;

export type UseCaseQueryRequest = {
  use_case: USE_CASES;
  fhir_server: FHIR_SERVERS;
  first_name?: string;
  last_name?: string;
  dob?: string;
  mrn?: string;
  phone?: string;
};

const UseCaseQueryMap: {
  [key in USE_CASES]: (
    patientId: string,
    fhirClient: FHIRClient,
    queryResponse: QueryResponse,
  ) => Promise<QueryResponse>;
} = {
  "social-determinants": socialDeterminantsQuery,
  "newborn-screening": newbornScreeningQuery,
  syphilis: syphilisQuery,
  gonorrhea: gonorrheaQuery,
  chlamydia: chlamydiaQuery,
  cancer: cancerQuery,
};

// Expected responses from the FHIR server
export type UseCaseQueryResponse = Awaited<ReturnType<typeof UseCaseQuery>>;

const FORMATS_TO_SEARCH: string[] = [
  "$1$2$3",
  "$1-$2-$3",
  "$1+$2+$3",
  "($1)+$2+$3",
  "($1)-$2-$3",
  "($1)$2-$3",
  "1($1)$2-$3",
];

/**
 * @todo Once the country code box is created on the search form, we'll
 * need to use that value to act as a kind of switch logic here to figure
 * out which formats we should be using.
 * Helper function to transform a cleaned, digit-only representation of
 * a phone number into multiple possible formatting options of that phone
 * number. If the given number has fewer than 10 digits, or contains any
 * delimiters, no formatting is performed and only the given number is
 * used.
 * @param phone A digit-only representation of a phone number.
 * @returns An array of formatted phone numbers.
 */
export async function GetPhoneQueryFormats(phone: string) {
  // Digit-only phone numbers will resolve as actual numbers
  if (isNaN(Number(phone)) || phone.length != 10) {
    const strippedPhone = phone.replace(" ", "+");
    return [strippedPhone];
  }
  // Map the phone number into each format we want to check
  const possibleFormats: string[] = FORMATS_TO_SEARCH.map((fmt) => {
    return phone.replace(/(\d{3})(\d{3})(\d{4})/gi, fmt);
  });
  return possibleFormats;
}

/**
 * @todo Add encounters as _include in condition query & batch encounter queries
 * A helper function to handle the "second-pass" batching approach to custom
 * queries, namely the encounters by referenced condition. Many use cases will
 * have a subset of queries mutually dependent on the results of another query,
 * meaning they can't be batched in the initial call. This function handles
 * that remaining subset, after other queries have already returned.
 * @param patientId The ID of the patient being queried for.
 * @param fhirClient The FHIR client to use for the queries.
 * @param queryResponse The data structure to store the accumulated results.
 * @returns The updated query response with encounter information.
 */
async function queryEncounters(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);
    queryResponse = await parseFhirSearch(encounterResponse, queryResponse);
  }
  return queryResponse;
}

/**
 * Helper function to read a JSON file from a given file path. Since utils
 * are tagged with 'use-client', this will be compiled and packed for browser
 * use, meaning we don't have access to the `fs` filesystem module. We need
 * to use JSON APIs instead.
 * @param filePath The relative string path to the file.
 * @returns A JSON object of the string representation of the file.
 */
function readJSONFile(filePath: string): any {
  try {
    const data = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error reading JSON file from ${filePath}:`, error);
    return null;
  }
}

// WORKING DIRECTORY
// /app/containers/tefca-viewer

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
  let query = "Patient?";
  if (request.first_name) {
    query += `given=${request.first_name}&`;
  }
  if (request.last_name) {
    query += `family=${request.last_name}&`;
  }
  if (request.dob) {
    query += `birthdate=${request.dob}&`;
  }
  if (request.mrn) {
    query += `identifier=${request.mrn}&`;
  }
  if (request.phone) {
    // We might have multiple phone numbers if we're coming from the API
    // side, since we parse *all* telecom structs
    const phonesToSearch = request.phone.split(";");
    let phonePossibilities: string[] = [];
    for (const phone of phonesToSearch) {
      const possibilities = await GetPhoneQueryFormats(phone);
      phonePossibilities.push(...possibilities);
    }
    query += `phone=${phonePossibilities.join(",")}&`;
  }

  const response = await fhirClient.get(query);

  // Check for errors
  if (response.status !== 200) {
    console.error(
      `Patient search failed. Status: ${
        response.status
      } \n Body: ${response.text} \n Headers: ${JSON.stringify(
        response.headers.raw(),
      )}`,
    );
  }
  queryResponse = await parseFhirSearch(response, queryResponse);
}

/**
 * Query a FHIR API for a public health use case based on patient demographics provided
 * in the request. If data is found, return in a queryResponse object.
 * @param request - UseCaseQueryRequest object containing the patient demographics and use case.
 * @param queryResponse - The response object to store the query results.
 * @returns - The response object containing the query results.
 */
export async function UseCaseQuery(
  request: UseCaseQueryRequest,
  queryResponse: QueryResponse = {},
): Promise<QueryResponse> {
  const fhirClient = new FHIRClient(request.fhir_server);

  if (!queryResponse.Patient || queryResponse.Patient.length === 0) {
    await patientQuery(request, fhirClient, queryResponse);
  }

  if (!queryResponse.Patient || queryResponse.Patient.length !== 1) {
    return queryResponse;
  }

  const patientId = queryResponse.Patient[0].id ?? "";

  await UseCaseQueryMap[request.use_case](patientId, fhirClient, queryResponse);

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
  const newbornSpec = readJSONFile(
    "/app/customQueries/newbornScreeningQuery.json",
  );
  const newbornQuery = new CustomQuery(newbornSpec, patientId);
  const response = await fhirClient.get(newbornQuery.getQuery("observation"));
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
  const syphilisSpec = readJSONFile("/app/customQueries/syphilisQuery.json");
  const syphilisQuery = new CustomQuery(syphilisSpec, patientId);
  const queryRequests: string[] = syphilisQuery.getAllQueries();
  const bundleResponse = await fhirClient.getBatch(queryRequests);
  queryResponse = await parseFhirSearch(bundleResponse, queryResponse);
  queryResponse = await queryEncounters(patientId, fhirClient, queryResponse);
  return queryResponse;
}

/**
 * Gonorrhea use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The response object containing the query results.
 */
async function gonorrheaQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const gonorrheaSpec = readJSONFile("/app/customQueries/gonorrheaQuery.json");
  const gonorrheaQuery = new CustomQuery(gonorrheaSpec, patientId);
  const queryRequests: string[] = gonorrheaQuery.getAllQueries();
  const bundleResponse = await fhirClient.getBatch(queryRequests);
  queryResponse = await parseFhirSearch(bundleResponse, queryResponse);
  queryResponse = await queryEncounters(patientId, fhirClient, queryResponse);
  return queryResponse;
}

/**
 * Chlamydia use case query.
 * @param patientId - The ID of the patient to query.
 * @param fhirClient - The client to query the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The response object containing the query results.
 */
async function chlamydiaQuery(
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const chlamydiaSpec = readJSONFile(
    "/app/containers/tefca-viewer/src/app/customQueries/chlamydiaQuery.json",
  );
  const chlamydiaQuery = new CustomQuery(chlamydiaSpec, patientId);
  const queryRequests: string[] = chlamydiaQuery.getAllQueries();
  const bundleResponse = await fhirClient.getBatch(queryRequests);
  queryResponse = await parseFhirSearch(bundleResponse, queryResponse);
  queryResponse = await queryEncounters(patientId, fhirClient, queryResponse);
  return queryResponse;
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
  const cancerSpec = readJSONFile("/app/customQueries/cancerQuery.json");
  const cancerQuery = new CustomQuery(cancerSpec, patientId);
  const conditionQuery = cancerQuery.getQuery("condition");
  const medicationRequestQuery = cancerQuery.getQuery("medication");
  const queryRequests: Array<string> = [conditionQuery, medicationRequestQuery];
  const bundleResponse = await fhirClient.getBatch(queryRequests);
  queryResponse = await parseFhirSearch(bundleResponse, queryResponse);
  queryResponse = await queryEncounters(patientId, fhirClient, queryResponse);

  return queryResponse;
}

/**
 * Parse the response from a FHIR search query. If the response is successful and
 * contains data, return an array of parsed resources.
 * @param response - The response from the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The parsed response.
 */
async function parseFhirSearch(
  response: fetch.Response | Array<fetch.Response>,
  queryResponse: QueryResponse = {},
): Promise<QueryResponse> {
  let resourceArray: any[] = [];

  // Process the responses
  if (Array.isArray(response)) {
    for (const r of response) {
      resourceArray = resourceArray.concat(await processResponse(r));
    }
  } else {
    resourceArray = await processResponse(response);
  }

  // Add resources to queryResponse
  for (const resource of resourceArray) {
    const resourceType = resource.resourceType as keyof QueryResponse;
    if (!queryResponse[resourceType]) {
      queryResponse[resourceType] = [resource];
    } else {
      queryResponse[resourceType]!.push(resource);
    }
  }
  return queryResponse;
}

/**
 * Process the response from a FHIR search query. If the response is successful and
 * contains data, return an array of resources that are ready to be parsed.
 * @param response - The response from the FHIR server.
 * @returns - The array of resources from the response.
 */
async function processResponse(response: fetch.Response): Promise<any[]> {
  let resourceArray: any[] = [];
  if (response.status === 200) {
    const body = await response.json();
    if (body.entry) {
      for (const entry of body.entry) {
        resourceArray.push(entry.resource);
      }
    }
  }
  return resourceArray;
}

/**
 * Create a FHIR Bundle from the query response.
 * @param queryResponse - The response object to store the results.
 * @returns - The FHIR Bundle of queried data.
 */
export async function createBundle(
  queryResponse: QueryResponse,
): Promise<APIQueryResponse> {
  const bundle: Bundle = {
    resourceType: "Bundle",
    type: "searchset",
    total: 0,
    entry: [],
  };

  Object.entries(queryResponse).forEach(([key, resources]) => {
    if (Array.isArray(resources)) {
      resources.forEach((resource) => {
        bundle.entry?.push({ resource });
        bundle.total = (bundle.total || 0) + 1;
      });
    }
  });

  return bundle;
}
