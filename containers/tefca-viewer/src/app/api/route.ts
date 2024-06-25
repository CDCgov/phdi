import { NextResponse, NextRequest } from "next/server";
import {
  UseCaseQuery,
  USE_CASES,
  UseCaseQueryRequest,
  QueryResponse,
} from "../query-service";
import { FHIR_SERVERS } from "../fhir-servers";
import { parsePatientIdentifiers } from "./parsing-service";

const USE_CASES_VALUES: USE_CASES[] = [
  "social-determinants",
  "newborn-screening",
  "syphilis",
  "gonorrhea",
  "chlamydia",
  "cancer",
];

const FHIR_SERVER_VALUES: FHIR_SERVERS[] = [
  "HELIOS Meld: Direct",
  "HELIOS Meld: eHealthExchange",
  "JMC Meld: Direct",
  "JMC Meld: eHealthExchange",
  "Public HAPI: eHealthExchange",
  "OpenEpic: eHealthExchange",
  "CernerHelios: eHealthExchange",
];

export async function POST(request: NextRequest) {
  let requestBody;
  let PatientIdentifiers;
  // TODO: Add error handling that checks if the body is a patient resource
  try {
    requestBody = await request.json();
  } catch (error: any) {
    console.error("Error reading request body:", error);
    return NextResponse.json(
      { message: "Error reading request body. " + error.message },
      { status: error.status }
    );
  }

  // Parse patient identifiers from requestBody
  try {
    PatientIdentifiers = await parsePatientIdentifiers(requestBody);
  } catch (error: any) {
    console.error("Error parsing patient identifiers from requestBody:", error);
    return NextResponse.json(
      {
        message:
          "Error parsing patient identifiers from requestBody. " +
          error.message,
      },
      { status: error.status }
    );
  }

  // Extract use_case and fhir_server from nextUrl
  const params = request.nextUrl.searchParams;
  const use_case = params.get("use_case");
  const fhir_server = params.get("fhir_server");
  if (!use_case || !fhir_server) {
    return NextResponse.json(
      {
        message:
          "Error reading request params. Please provide valid use_case and fhir_server params.",
      },
      { status: 400 }
    );
  } else if (!Object.values(USE_CASES_VALUES).includes(use_case as USE_CASES)) {
    return NextResponse.json(
      {
        message: "Invalid use_case. Please provide a valid use_case.",
      },
      { status: 400 }
    );
  } else if (
    !Object.values(FHIR_SERVER_VALUES).includes(fhir_server as FHIR_SERVERS)
  ) {
    return NextResponse.json(
      {
        message: "Invalid fhir_server. Please provide a valid fhir_server.",
      },
      { status: 400 }
    );
  }

  // Add params & patient identifiers to UseCaseRequest
  const UseCaseRequest: UseCaseQueryRequest = {
    use_case: use_case as USE_CASES,
    fhir_server: fhir_server as FHIR_SERVERS,
    ...(PatientIdentifiers.first_name && {
      first_name: PatientIdentifiers.first_name,
    }),
    ...(PatientIdentifiers.last_name && {
      last_name: PatientIdentifiers.last_name,
    }),
    ...(PatientIdentifiers.dob && { dob: PatientIdentifiers.dob }),
    ...(PatientIdentifiers.mrn && { mrn: PatientIdentifiers.mrn }),
  };

  const UseCaseQueryResponse: QueryResponse =
    await UseCaseQuery(UseCaseRequest);

  return NextResponse.json({
    message: "success!",
    UseCaseRequest: UseCaseRequest,
    UseCaseResponse: UseCaseQueryResponse,
  });
}
