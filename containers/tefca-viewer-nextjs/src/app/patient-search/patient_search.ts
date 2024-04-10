"use server";
import { NextApiRequest, NextApiResponse } from "next";
import { v4 as uuidv4 } from "uuid";
import https from "https";
import fetch, { RequestInit } from "node-fetch";

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
};
type UseCaseQueryRequest = {
  use_case: USE_CASES;
} & PatientIdQueryRequest;

type PatientResourceRequest = {
  fhir_host: string;
  init: RequestInit;
  patient_id: string;
};

type PatientResourceQueryResponse = {
  entry: Record<string, unknown>[];
} & Record<string, unknown>;

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
  if (
    FHIR_SERVERS[input.fhir_server].username &&
    FHIR_SERVERS[input.fhir_server].password
  ) {
    const credentials = btoa(
      `${FHIR_SERVERS[input.fhir_server].username}:${
        FHIR_SERVERS[input.fhir_server].password || ""
      }`
    );
    headers.Authorization = `Basic ${credentials}`;
    init.agent = new https.Agent({
      rejectUnauthorized: false,
    });
  }

  // Query for Patient resource and ID
  const response = await fetch(fhir_host + patient_id_query, {
    headers: headers,
    ...init,
  });
  const use_case_query_response = await response.json();

  // Check for errors
  if (response.status !== 200) {
    console.log("response:", response);
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }

  if (use_case_query_response.total === 0) {
    throw new Error("No patient found.");
  }

  const patient_id = use_case_query_response.entry[0].resource.id;

  return { patient_id, fhir_host, init, use_case_query_response };
}

export async function use_case_query(input: UseCaseQueryRequest) {
  console.log("input:", input);
  // Get patient ID and patient resource
  const patient_resource_query_response = await patient_id_query({
    fhir_server: input.fhir_server,
    first_name: input.first_name,
    last_name: input.last_name,
    dob: input.dob,
  });
  const { patient_id, fhir_host, init, use_case_query_response } =
    patient_resource_query_response;

  if (input.use_case === "social-determinants") {
    // Query for social determinants
    const social_determinants_query_response = await social_determinants_query({
      fhir_host: fhir_host,
      init: init,
      patient_id: patient_id,
    });
    // Collect results
    use_case_query_response["entry"] = [
      ...use_case_query_response["entry"],
      ...social_determinants_query_response["entry"],
    ];
  } else if (input.use_case === "newborn-screening") {
    // Query for newborn screening
    const newborn_screening_query_response = await newborn_screening_query({
      fhir_host: fhir_host,
      init: init,
      patient_id: patient_id,
    });

    // Collect results
    use_case_query_response["entry"] = [
      ...use_case_query_response["entry"],
      ...newborn_screening_query_response["entry"],
    ];
  } else if (input.use_case === "syphilis") {
    // Query for syphilis
    const syphilis_query_response = await syphilis_query({
      fhir_host: fhir_host,
      init: init,
      patient_id: patient_id,
    });

    // Collect results
    use_case_query_response["entry"] = [
      ...use_case_query_response["entry"],
      ...syphilis_query_response["entry"],
    ];
  }

  return {
    patient_id: patient_id,
    use_case_query_response,
  };
}

async function social_determinants_query(
  input: PatientResourceRequest
): Promise<PatientResourceQueryResponse> {
  const query = `/Observation?subject=${input.patient_id}&category=social-history`;
  const query_response = await fetch(input.fhir_host + query, input.init);
  const response = await query_response.json();

  // Check for errors
  if (response.status !== 200) {
    console.log("response:", response);
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }

  if (response.total === 0) {
    throw new Error("No patient found.");
  }

  return response;
}

async function newborn_screening_query(
  input: PatientResourceRequest
): Promise<PatientResourceQueryResponse> {
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

  const query = `/Observation?subject=${input.patient_id}&code=${loincFilter}`;
  const query_response = await fetch(input.fhir_host + query, input.init);
  const response = await query_response.json();
  // Check for errors
  if (response.status !== 200) {
    console.log("response:", response);
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }

  if (response.total === 0) {
    throw new Error("No patient found.");
  }

  return response;
}

async function syphilis_query(
  input: PatientResourceRequest
): Promise<PatientResourceQueryResponse> {
  const loincs: Array<string> = ["LP70657-9", "98212-4"];
  const snomed: Array<string> = ["76272004"];
  const loincFilter: string = loincs.join(",");
  const snomedFilter: string = snomed.join(",");

  const query = `/Observation?subject=${input.patient_id}&code=${loincFilter}`;
  const query_response = await fetch(input.fhir_host + query, input.init);
  const response = await query_response.json();

  const diagnositic_report_query = `/DiagnosticReport?subject=${input.patient_id}&code=${loincFilter}`;
  const diagnositic_report_query_response = await fetch(
    input.fhir_host + diagnositic_report_query,
    input.init
  );
  const diagnostic_response = await diagnositic_report_query_response.json();

  const condition_query = `/Condition?subject=${input.patient_id}&code=${snomedFilter}`;
  const condition_query_response = await fetch(
    input.fhir_host + condition_query,
    input.init
  );
  const condition_response = await condition_query_response.json();
  const condition_id = condition_response.entry[0].resource.id;

  const encounter_query = `/Encounter?subject=${input.patient_id}&reason-reference=${condition_id}`;
  const encounter_query_response = await fetch(
    input.fhir_host + encounter_query,
    input.init
  );
  const encounter_response = await encounter_query_response.json();

  // // Check for errors
  // if (response.status !== 200) {
  //   console.log("response:", response);
  //   throw new Error(`Patient search failed. Status: ${response.status}`);
  // }

  // if (response.total === 0) {
  //   throw new Error("No patient found.");
  // }

  // Collect results
  console.log("response:", response);
  response["entry"] = [
    ...response["entry"],
    ...diagnostic_response["entry"],
    // ...condition_response["entry"],
    ...encounter_response["entry"],
  ];

  return response;
}

// async function add_loinc_filter(input: Array<string>): Promise<string> {
//   const loincFilter: string = "code=" + input.join(",");

//   return loincFilter;
// }

// async function use_case_sub_query() {
//   let
//   // use input.use_case to determine if there are LOINCS
//   // if there are LOINCS, join them together and query for the appropriate resources
//   // Check for errors
//   if (response.status !== 200) {
//     console.log("response:", response);
//     throw new Error(`Patient search failed. Status: ${response.status}`);
//   }

//   if (response.total === 0) {
//     throw new Error("No patient found.");
//   }
// }
