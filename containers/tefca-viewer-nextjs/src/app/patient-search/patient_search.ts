'use server';
import { NextApiRequest, NextApiResponse } from 'next';
import { v4 as uuidv4 } from "uuid";
import https from 'https';
import fetch, { RequestInit } from 'node-fetch';

// Create a custom agent with SSL certificate verification disabled
const agent = new https.Agent({
  rejectUnauthorized: false
});

// Create a custom fetch function that uses the custom agent
const customFetch = (url: string, options: RequestInit = {}) => {
  if (!options.agent) {
    options.agent = agent;
  }
  return fetch(url, options);
};


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
  meld: { hostname: "https://gw.interop.community/skylightsandbox/open/" },
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
  fhir_host: string;
  fhir_server: FHIR_SERVERS;
  first_name: string;
  last_name: string;
  dob: string;
}

// Expected responses from the FHIR server
export type PatientIdQueryResponse = { patient_id: string, first_name: string };
export type UseCaseQueryResponse = { use_case_response: any }; // need to update any to TS dict

export async function patient_id_query(input: PatientIdQueryRequest): Promise<PatientIdQueryResponse> {
  // Set up and logging
  console.log("patient_id_query input:", input);
  const fhir_host = FHIR_SERVERS[input.fhir_server].hostname;
  const patient_id_query = `Patient?given=${input.first_name}&family=${input.last_name}&birthdate=${input.dob}`;
  const headers = FHIR_SERVERS[input.fhir_server].headers || {};
  // Add username to headers if it exists in input.fhir_server
  if (FHIR_SERVERS[input.fhir_server].username && FHIR_SERVERS[input.fhir_server].password) {
    {
      const credentials = btoa(`${FHIR_SERVERS[input.fhir_server].username}:${FHIR_SERVERS[input.fhir_server].password || ''}`);
      headers.Authorization = `Basic ${credentials}`;
    }
  }

  const response = await customFetch(fhir_host + patient_id_query, {
    headers: headers,
  });

  const data = await response.json();

  if (response.status !== 200) {
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }


  if (data.total === 0) {
    throw new Error('No patient found.');
  }

  const patient_id = data.entry[0].resource.id;

  return { patient_id, first_name: input.first_name };
}

// export async function use_case_query(input: UseCaseQueryRequest): Promise<UseCaseQueryResponse> {
//   // Set up and logging
//   console.log("use_case_query input:", input);

//   // Get patient ID
//   const patient_id_query_response = await patient_id_query({
//     fhir_server: input.fhir_server,
//     first_name: input.first_name,
//     last_name: input.last_name,
//     dob: input.dob,
//   });

//   // Use patient id to query based on use_case

//   // const response = await fetch(input.fhir_host + use_case_query, {
//   //   headers: input.headers,
//   // });

//   // const data = await response.json();

//   // if (response.status !== 200) {
//   //   throw new Error(`Use case query failed. Status: ${response.status}`);
//   // }
//   const use_case_response = "Hello, World!";

//   return { use_case_response };
// }