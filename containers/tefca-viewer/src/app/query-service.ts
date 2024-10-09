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
import { USE_CASES, FHIR_SERVERS, ValueSetItem } from "./constants";
import { CustomQuery } from "./CustomQuery";
import { GetPhoneQueryFormats } from "./format-service";
import { formatValueSetItemsAsQuerySpec } from "./format-service";

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

/**
 * Expected structure of a query object
 */
export type QueryStruct = {
  labCodes: string[];
  snomedCodes: string[];
  rxnormCodes: string[];
  classTypeCodes: string[];
  hasSecondEncounterQuery: boolean;
};

// Expected responses from the FHIR server
export type UseCaseQueryResponse = Awaited<ReturnType<typeof UseCaseQuery>>;

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
      let possibilities = await GetPhoneQueryFormats(phone);
      possibilities = possibilities.filter((phone) => phone !== "");
      if (possibilities.length !== 0) {
        phonePossibilities.push(...possibilities);
      }
    }
    if (phonePossibilities.length > 0) {
      query += `phone=${phonePossibilities.join(",")}&`;
    }
  }

  const response = await fhirClient.get(query);

  // Check for errors
  if (response.status !== 200) {
    console.error(
      `Patient search failed. Status: ${response.status} \n Body: ${
        response.text
      } \n Headers: ${JSON.stringify(response.headers.raw())}`,
    );
  }
  queryResponse = await parseFhirSearch(response, queryResponse);
}

/**
 * Query a FHIR API for a public health use case based on patient demographics provided
 * in the request. If data is found, return in a queryResponse object.
 * @param request - UseCaseQueryRequest object containing the patient demographics and use case.
 * @param queryValueSets - The value sets to be included in query filtering.
 * @param queryResponse - The response object to store the query results.
 * @returns - The response object containing the query results.
 */
export async function UseCaseQuery(
  request: UseCaseQueryRequest,
  queryValueSets: ValueSetItem[],
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

  await generalizedQuery(
    request.use_case,
    queryValueSets,
    patientId,
    fhirClient,
    queryResponse,
  );

  return queryResponse;
}

/**
 * Performs a generalized query for collections of patients matching
 * particular criteria. The query is determined by a collection of passed-in
 * valuesets to include in the query results, and any patients found must
 * have eCR data interseecting with these valuesets.
 * @param useCase The particular use case the query is associated with.
 * @param queryValueSets The valuesets to include as reference points for patient
 * data.
 * @param patientId The ID of the patient for whom to search.
 * @param fhirClient The client used to communicate with the FHIR server.
 * @param queryResponse The response object for the query results.
 * @returns A promise for an updated query response.
 */
async function generalizedQuery(
  useCase: USE_CASES,
  queryValueSets: ValueSetItem[],
  patientId: string,
  fhirClient: FHIRClient,
  queryResponse: QueryResponse,
): Promise<QueryResponse> {
  const querySpec = await formatValueSetItemsAsQuerySpec(
    useCase,
    queryValueSets,
  );
  const builtQuery = new CustomQuery(querySpec, patientId);
  let response: fetch.Response | fetch.Response[];

  // Special cases for plain SDH or newborn screening, which just use one query
  if (useCase === "social-determinants") {
    response = await fhirClient.get(builtQuery.getQuery("social"));
  } else if (useCase === "newborn-screening") {
    response = await fhirClient.get(builtQuery.getQuery("observation"));
  } else {
    const queryRequests: string[] = builtQuery.getAllQueries();
    response = await fhirClient.getBatch(queryRequests);
  }
  queryResponse = await parseFhirSearch(response, queryResponse);
  if (!querySpec.hasSecondEncounterQuery) {
    return queryResponse;
  } else {
    queryResponse = await queryEncounters(patientId, fhirClient, queryResponse);
    return queryResponse;
  }
}

/**
 * Parse the response from a FHIR search query. If the response is successful and
 * contains data, return an array of parsed resources.
 * @param response - The response from the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The parsed response.
 */
export async function parseFhirSearch(
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
export async function processResponse(
  response: fetch.Response,
): Promise<any[]> {
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

  Object.entries(queryResponse).forEach(([_, resources]) => {
    if (Array.isArray(resources)) {
      resources.forEach((resource) => {
        bundle.entry?.push({ resource });
        bundle.total = (bundle.total || 0) + 1;
      });
    }
  });

  return bundle;
}
