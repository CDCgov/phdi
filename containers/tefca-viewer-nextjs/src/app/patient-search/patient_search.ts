// import { NextRequest, NextResponse } from "next/server";
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
  meld: { hostname: "https://gw.interop.community/HeliosConnectathonSa/open" },
  ehealthexchange: {
    hostname: "https://concept01.ehealthexchange.org:52780/fhirproxy/r4/",
    username: "svc_eHxFHIRSandbox",
    password: "willfulStrongStandurd7",
    headers: {
      Accept: "application/json, application/*+json, */*",
      "Accept-Encoding": "gzip, deflate, br",
      "Content-Type": "application/fhir+json; charset=UTF-8",
      "X-DESTINATION": "CernerHelios",
      "X-POU": "TREAT",
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
