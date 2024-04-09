'use server';
import { NextApiRequest, NextApiResponse } from 'next';
import { v4 as uuidv4 } from "uuid";
import https from 'https';
import fetch, { RequestInit } from 'node-fetch';

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

// Expected requests to the FHIR server
type PatientIdQueryRequest = {
  fhir_server: FHIR_SERVERS;
  first_name: string;
  last_name: string;
  dob: string;
}
type UseCaseQueryRequest = {
  use_case: USE_CASES;
} & PatientIdQueryRequest;

type PatientResourceRequest = {
  patient_id: string;
} & PatientIdQueryRequest;

// Expected responses from the FHIR server
export type UseCaseQueryResponse = Awaited<ReturnType<typeof use_case_query>>;

async function patient_id_query(input: PatientIdQueryRequest) {
  // Set up and logging
  const fhir_host = FHIR_SERVERS[input.fhir_server].hostname;
  const patient_id_query = `Patient?given=${input.first_name}&family=${input.last_name}&birthdate=${input.dob}`;
  const headers = FHIR_SERVERS[input.fhir_server].headers || {};
  // Set up init object for eHealth Exchange
  const init: RequestInit = {};

  // Add username to headers if it exists in input.fhir_server
  if (FHIR_SERVERS[input.fhir_server].username && FHIR_SERVERS[input.fhir_server].password) {
    const credentials = btoa(`${FHIR_SERVERS[input.fhir_server].username}:${FHIR_SERVERS[input.fhir_server].password || ''}`);
    headers.Authorization = `Basic ${credentials}`;
    init.agent = new https.Agent({
      rejectUnauthorized: false
    });
  }
  const response = await fetch(fhir_host + patient_id_query, {
    headers: headers,
    ...init
  });
  const data = await response.json();

  if (response.status !== 200) {
    console.log("response:", response);
    console.log("data:", data);
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }


  if (data.total === 0) {
    throw new Error('No patient found.');
  }

  const patient_id = data.entry[0].resource.id;

  return { patient_id, fhir_host, init };
}

export async function use_case_query(input: UseCaseQueryRequest) {
  // Set up and logging
  console.log("use_case_query input:", input);

  // Get patient ID
  const patient_id_query_response = await patient_id_query({
    fhir_server: input.fhir_server,
    first_name: input.first_name,
    last_name: input.last_name,
    dob: input.dob,
  });
  const { fhir_host, init, patient_id } = patient_id_query_response;


  // Use patient id to query based on use_case 
   const patient_query = `/Patient?_id=${patient_id}`
  const patient_response = await fetch(fhir_host + patient_query, init);
  const use_case_query_response = await patient_response.json();

  // Query for social determinants
  const social_determinants_query = `/Observation?subject=Patient/${patient_id}&category=survey`
  const response = await fetch(fhir_host + social_determinants_query, init);
  const social_determinants_response = await response.json();

  // Collect results
  use_case_query_response["entry"] = [...use_case_query_response["entry"], ...social_determinants_response["entry"]];

  return {
    patient_id: patient_id,
    use_case_query_response
  };
}

async function patient_resource_query(input:PatientResourceRequest) {

}