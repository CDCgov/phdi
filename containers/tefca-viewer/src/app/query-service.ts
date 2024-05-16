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
import { v4 as uuidv4 } from "uuid";

export type USE_CASES =
  | "social-determinants"
  | "newborn-screening"
  | "syphilis"
  | "gonorrhea"
  | "chlamydia"
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
  gonorrhea: gonorrheaQuery,
  chlamydia: chlamydiaQuery,
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

  if (!queryResponse.Patient || queryResponse.Patient.length === 0) {
    await patientQuery(request, fhirClient, queryResponse);
  }

  if (!queryResponse.Patient || queryResponse.Patient.length !== 1) {
    return queryResponse;
  }
  const patientId = queryResponse.Patient[0].id ?? "";

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
  // const queryRequests: Array<string> = [query];
  // const queryBundle = await generateQueryBundle(queryRequests);
  // const bundleResponse = await fhirClient.post(queryBundle);
  // queryResponse = await parseFhirSearch(bundleResponse, queryResponse);
  // return queryResponse;

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
  const classType: Array<string> = [
    "54", // Family planning
    "441", // Sexually transmitted
  ];

  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");
  const classTypeFilter: string = classType.join(",");

  // Batch query for observations, diagnostic reports, conditions, some encounters, and medication requests
  const observationQuery = `/Observation?subject=${patientId}&code=${loincFilter}`;
  const diagnositicReportQuery = `/DiagnosticReport?subject=${patientId}&code=${loincFilter}`;
  const conditionQuery = `/Condition?subject=${patientId}&code=${snomedFilter}`;
  const medicationRequestQuery = `/MedicationRequest?subject=${patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`;
  const socialHistoryQuery = `/Observation?subject=${patientId}&category=social-history`;
  const encounterQuery = `/Encounter?subject=${patientId}&reason-code=${snomedFilter}`;
  const encounterClassTypeQuery = `/Encounter?subject=${patientId}&class=${classTypeFilter}`;

  const queryRequests: Array<string> = [
    observationQuery,
    diagnositicReportQuery,
    conditionQuery,
    medicationRequestQuery,
    socialHistoryQuery,
    encounterQuery,
    encounterClassTypeQuery,
  ];
  // const queryBundle = await generateQueryBundle(queryRequests);
  // const bundleResponse = await fhirClient.post(queryBundle);
  const bundleResponse = await fetchFHIRDataWithClient(
    queryRequests,
    fhirClient,
  );
  console.log("bundleResponse: ", bundleResponse);
  // queryResponse = await parseFhirSearch(bundleResponse, queryResponse);

  // Query for encounters. TODO: Add encounters as _include in condition query
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);

    queryResponse = await parseFhirSearch(encounterResponse, queryResponse);
  }
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
  const loincs: Array<string> = [
    "24111-7", // Neisseria gonorrhoeae DNA [Presence] in Specimen by NAA with probe detection
    "11350-6", // History of Sexual behavior Narrative
    "21613-5", // Chlamydia trachomatis DNA [Presence] in Specimen by NAA with probe detection
    "82810-3", // Pregnancy status
    "83317-8", // Sexual activity with anonymous partner in the past year
  ];
  const snomed: Array<string> = [
    "15628003", // Gonorrhea (disorder)
    "2339001", // Sexual overexposure,
    "72531000052105", // Counseling for contraception (procedure)
    "102874004", // Possible pregnancy
  ];
  const rxnorm: Array<string> = [
    "1665005", // ceftriaxone 500 MG Injection
    "434692", // azithromycin 1000 MG
  ];
  const classType = [
    "54", // Family planning
    "441", // Sexually transmitted
  ];

  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");
  const classTypeFilter: string = classType.join(",");

  // Batch query for observations, diagnostic reports, conditions, some encounters, and medication requests
  const observationQuery = `/Observation?subject=${patientId}&code=${loincFilter}`;
  const diagnositicReportQuery = `/DiagnosticReport?subject=${patientId}&code=${loincFilter}`;
  const conditionQuery = `/Condition?subject=${patientId}&code=${snomedFilter}`;
  const medicationRequestQuery = `/MedicationRequest?subject=${patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`;
  const socialHistoryQuery = `/Observation?subject=${patientId}&category=social-history`;
  const encounterQuery = `/Encounter?subject=${patientId}&reason-code=${snomedFilter}`;
  const encounterClassTypeQuery = `/Encounter?subject=${patientId}&class=${classTypeFilter}`;

  const queryRequests: Array<string> = [
    observationQuery,
    diagnositicReportQuery,
    conditionQuery,
    medicationRequestQuery,
    socialHistoryQuery,
    encounterQuery,
    encounterClassTypeQuery,
  ];
  const queryBundle = await generateQueryBundle(queryRequests);
  const bundleResponse = await fhirClient.post(queryBundle);
  queryResponse = await parseFhirSearch(bundleResponse, queryResponse);

  // Query for encounters. TODO: Add encounters as _include in condition query & batch encounter queries
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);

    queryResponse = await parseFhirSearch(encounterResponse, queryResponse);
  }

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
  const loincs: Array<string> = [
    "24111-7", // Neisseria gonorrhoeae DNA [Presence] in Specimen by NAA with probe detection
    "72828-7", // Chlamydia trachomatis and Neisseria gonorrhoeae DNA panel - Specimen
    "21613-5", // Chlamydia trachomatis DNA [Presence] in Specimen by NAA with probe detection
    "82810-3", // Pregnancy status
    "11350-6", // History of Sexual behavior Narrative
    "83317-8", // Sexual activity with anonymous partner in the past year
  ];
  const snomed: Array<string> = [
    "2339001", // Sexual overexposure,
    "72531000052105", // Counseling for contraception (procedure)
    "102874004", // Possible pregnancy
  ];
  const rxnorm: Array<string> = [
    "434692", // azithromycin 1000 MG
    "82122", // levofloxacin
    "1649987", // doxycycline hyclate 100 MG
    "1665005", // ceftriaxone 500 MG Injection
  ];
  const classType = [
    "54", // Family planning
    "441", // Sexually transmitted
  ];

  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");
  const classTypeFilter: string = classType.join(",");

  // Batch query for observations, diagnostic reports, conditions, some encounters, and medication requests
  const observationQuery = `/Observation?subject=${patientId}&code=${loincFilter}`;
  const diagnositicReportQuery = `/DiagnosticReport?subject=${patientId}&code=${loincFilter}`;
  const conditionQuery = `/Condition?subject=${patientId}&code=${snomedFilter}`;
  const medicationRequestQuery = `/MedicationRequest?subject=${patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`;
  const socialHistoryQuery = `/Observation?subject=${patientId}&category=social-history`;
  const encounterQuery = `/Encounter?subject=${patientId}&reason-code=${snomedFilter}`;
  const encounterClassTypeQuery = `/Encounter?subject=${patientId}&class=${classTypeFilter}`;

  const queryRequests: Array<string> = [
    observationQuery,
    diagnositicReportQuery,
    conditionQuery,
    medicationRequestQuery,
    socialHistoryQuery,
    encounterQuery,
    encounterClassTypeQuery,
  ];
  const queryBundle = await generateQueryBundle(queryRequests);
  const bundleResponse = await fhirClient.post(queryBundle);
  queryResponse = await parseFhirSearch(bundleResponse, queryResponse);
  // Query for encounters. TODO: Add encounters as _include in condition query & batch encounter queries
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);

    queryResponse = await parseFhirSearch(encounterResponse, queryResponse);
  }

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
  const snomed: Array<string> = ["92814006"];
  const rxnorm: Array<string> = ["828265"]; // drug codes from NLM/NIH RxNorm
  const cpt: Array<string> = ["15301000"]; // encounter codes from AMA CPT
  const snomedFilter: string = snomed.join(",");
  const rxnormFilter: string = rxnorm.join(",");

  // Query for conditions and encounters
  const conditionQuery = `/Condition?subject=${patientId}&code=${snomedFilter}`;
  const medicationRequestQuery = `/MedicationRequest?subject=${patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`;

  const queryRequests: Array<string> = [conditionQuery, medicationRequestQuery];
  const queryBundle = await generateQueryBundle(queryRequests);
  const bundleResponse = await fhirClient.post(queryBundle);
  queryResponse = await parseFhirSearch(bundleResponse, queryResponse);

  // Query for encounters
  if (queryResponse.Condition && queryResponse.Condition.length > 0) {
    const conditionId = queryResponse.Condition[0].id;
    console.log("conditionId: ", conditionId);
    const encounterQuery = `/Encounter?subject=${patientId}&reason-reference=${conditionId}`;
    const encounterResponse = await fhirClient.get(encounterQuery);
    queryResponse = await parseFhirSearch(encounterResponse, queryResponse);
  }

  return queryResponse;
}

/**
 * Parse the response from a FHIR search query. If the response is successful and
 * contains data, return an array of resources.
 * @param response - The response from the FHIR server.
 * @param queryResponse - The response object to store the results.
 * @returns - The parsed response.
 */
async function parseFhirSearch_original(
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
        // Create resource array to handle Bundle & non-Bundle entries
        let resourceArray: any[];
        if (entry.resource.resourceType === "Bundle") {
          resourceArray = entry.resource.entry
            ? entry.resource.entry.map(
                (bundleEntry: any) => bundleEntry.resource,
              )
            : [];
        } else {
          // Handle non-Bundle entry
          resourceArray = [entry.resource];
        }

        for (const resource of resourceArray) {
          const resourceType = resource.resourceType as keyof QueryResponse;
          if (!queryResponse[resourceType]) {
            queryResponse[resourceType] = [resource];
          } else {
            queryResponse[resourceType]!.push(resource);
          }
        }
      }
    }
  }
  return queryResponse;
}

interface BundleRequest {
  method: string;
  url: string;
}

interface BundleEntry {
  request: BundleRequest;
}

export type Bundle = {
  resourceType: string;
  id: string;
  type: string;
  entry: BundleEntry[];
};

/**
 * Generate a request bundle for making batch requests from a list of URLs.
 * @param urls - The list of URLs to include in the bundle.
 * @returns - The generated bundle.
 */

async function generateQueryBundle(urls: Array<string>): Promise<Bundle> {
  const entry: BundleEntry[] = urls.map((url) => ({
    request: {
      method: "GET",
      url: url.trim(),
    },
  }));

  const bundle: Bundle = {
    resourceType: "Bundle",
    id: uuidv4(),
    type: "batch",
    entry,
  };

  return bundle;
}

async function fetchFHIRDataWithClient(
  urls: Array<string>,
  fhirClient: FHIRClient,
): Promise<Array<Bundle>> {
  const fetchPromises = urls.map((url) =>
    fhirClient.get(url).then((response) => {
      if (!response.ok) {
        console.error(`Failed to fetch ${url}: ${response.statusText}`);
      }
      return response.json();
    }),
  );

  return await Promise.all(fetchPromises);
}
