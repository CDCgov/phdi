import { NextResponse, NextRequest } from "next/server";
import {
  UseCaseQuery,
  UseCaseQueryRequest,
  QueryResponse,
  createBundle,
  APIQueryResponse,
} from "../../query-service";
import { parsePatientDemographics } from "./parsing-service";
import {
  USE_CASES,
  FHIR_SERVERS,
  FhirServers,
  UseCases,
} from "../../constants";

import { handleRequestError } from "./error-handling-service";

/**
 * Health check for TEFCA Viewer
 * @returns Response with status OK.
 */
export async function GET() {
  return NextResponse.json({ status: "OK" }, { status: 200 });
}

/**
 * Handles a POST request to query a given FHIR server for a given use case. The
 * use_case and fhir_server are provided as query parameters in the request URL. The
 * request body contains the FHIR patient resource to be queried.
 * @param request - The incoming Next.js request object.
 * @returns Response with UseCaseResponse.
 */
export async function POST(request: NextRequest) {
  let requestBody;
  let PatientIdentifiers;

  try {
    requestBody = await request.json();

    // Check if requestBody is a patient resource
    if (requestBody.resourceType !== "Patient") {
      const diagnostics_message = "Request body is not a Patient resource.";
      const OperationOutcome = await handleRequestError(diagnostics_message);
      return NextResponse.json(OperationOutcome);
    }
  } catch (error: any) {
    const diagnostics_message = `${error.message}`;
    const OperationOutcome = await handleRequestError(diagnostics_message);
    return NextResponse.json(OperationOutcome);
  }

  // Parse patient identifiers from requestBody
  PatientIdentifiers = await parsePatientDemographics(requestBody);
  // Check if PatientIdentifiers is empty or there was an error parsing patient identifiers
  if (Object.keys(PatientIdentifiers).length === 0) {
    const diagnostics_message =
      "No patient identifiers to parse from requestBody.";
    const OperationOutcome = await handleRequestError(diagnostics_message);
    return NextResponse.json(OperationOutcome);
  }

  // Extract use_case and fhir_server from nextUrl
  const params = request.nextUrl.searchParams;
  const use_case = params.get("use_case");
  const fhir_server = params.get("fhir_server");

  if (!use_case || !fhir_server) {
    const diagnostics_message = "Missing use_case or fhir_server.";
    const OperationOutcome = await handleRequestError(diagnostics_message);
    return NextResponse.json(OperationOutcome);
  } else if (!Object.values(UseCases).includes(use_case as USE_CASES)) {
    const diagnostics_message = `Invalid use_case. Please provide a valid use_case. Valid use_cases include ${UseCases}.`;
    const OperationOutcome = await handleRequestError(diagnostics_message);
    return NextResponse.json(OperationOutcome);
  } else if (
    !Object.values(FhirServers).includes(fhir_server as FHIR_SERVERS)
  ) {
    const diagnostics_message = `Invalid fhir_server. Please provide a valid fhir_server. Valid fhir_servers include ${FhirServers}.`;
    const OperationOutcome = await handleRequestError(diagnostics_message);
    return NextResponse.json(OperationOutcome);
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
    ...(PatientIdentifiers.phone && { phone: PatientIdentifiers.phone }),
  };

  const UseCaseQueryResponse: QueryResponse =
    await UseCaseQuery(UseCaseRequest);

  // Bundle data
  const bundle: APIQueryResponse = await createBundle(UseCaseQueryResponse);

  return NextResponse.json(bundle);
}
