import { NextResponse, NextRequest } from "next/server";
import {
  UseCaseQuery,
  USE_CASES,
  UseCaseQueryRequest,
  QueryResponse,
} from "../query-service";
import { FHIR_SERVERS } from "../fhir-servers";
import { parsePatientIdentifiers } from "./parsing-service";

export async function POST(request: NextRequest) {
  const body = await request.json();
  // TODO: Function to validate body is a valid patient resource
  const PatientIdentifiers = await parsePatientIdentifiers(body);

  const params = request.nextUrl.searchParams;
  const use_case = params.get("use_case");

  const fhir_server = params.get("fhir_server");
  // TODO: Function to validate params, e.g., required params are present, usecase is valid, and fhirserver is valid
  // TODO: Create if/elif/else statement to handle invalid params/body

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
