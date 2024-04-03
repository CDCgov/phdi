'use server';
import { NextApiRequest, NextApiResponse } from 'next';
import { v4 as uuidv4 } from "uuid";

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


type PatientQueryRequest = {
  fhir_server: "meld" | "ehealthexchange";
  first_name: string;
  last_name: string;
  dob?: string;
}


export async function use_case_query(input: PatientQueryRequest) {
  console.log("Input:", input);

  const fhir_host = FHIR_SERVERS[input.fhir_server].hostname;
  const patient_query = `Patient?given=${input.first_name}&family=${input.last_name}&birthdate=${input.dob}`;
  const response = await fetch(fhir_host + patient_query, {
    headers: FHIR_SERVERS[input.fhir_server].headers || {},
  });

  const data = await response.json();

  if (response.status !== 200) {
    throw new Error(`Patient search failed. Status: ${response.status}`);
  }


  if (data.total === 0) {
    throw new Error('No patient found.');
  }

  const patient_id = data.entry[0].resource.id;

  return patient_id;
}

