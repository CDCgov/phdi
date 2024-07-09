import fetch from "node-fetch";
import FHIRClient from "@/app/fhir-servers";
import { USE_CASES, FHIR_SERVERS } from "@/app/constants";
import {
  patientQuery,
  UseCaseQuery,
  socialDeterminantsQuery,
  newbornScreeningQuery,
  parseFhirSearch,
  QueryResponse,
} from "@/app/query-service";

jest.mock("node-fetch");
const { Response } = jest.requireActual("node-fetch");

describe("FHIR Queries", () => {
  let fhirClient: FHIRClient;

  beforeEach(() => {
    fhirClient = new FHIRClient("HELIOS Meld: Direct" as FHIR_SERVERS);
  });

  test("patientQuery - success", async () => {
    const mockResponse = new Response(
      JSON.stringify({
        entry: [{ resource: { resourceType: "Patient", id: "1" } }],
      }),
      { status: 200 },
    );

    (fetch as jest.Mock).mockResolvedValue(mockResponse);

    let queryResponse: QueryResponse = {};
    const request = {
      use_case: "syphilis" as USE_CASES,
      fhir_server: "HELIOS Meld: Direct" as FHIR_SERVERS,
      first_name: "John",
      last_name: "Doe",
      dob: "1990-01-01",
    };

    await patientQuery(request, fhirClient, queryResponse);

    expect(queryResponse.Patient).toHaveLength(1);
    expect(queryResponse.Patient![0].id).toBe("1");
  });

  test("UseCaseQuery - social-determinants", async () => {
    const request = {
      use_case: "social-determinants" as USE_CASES,
      fhir_server: "HELIOS Meld: Direct" as FHIR_SERVERS,
      first_name: "John",
      last_name: "Doe",
      dob: "1990-01-01",
    };

    const mockPatientResponse = new Response(
      JSON.stringify({
        entry: [{ resource: { resourceType: "Patient", id: "1" } }],
      }),
      { status: 200 },
    );

    const mockObservationResponse = new Response(
      JSON.stringify({
        entry: [{ resource: { resourceType: "Observation", id: "obs1" } }],
      }),
      { status: 200 },
    );

    (fetch as jest.Mock).mockResolvedValueOnce(mockPatientResponse);
    (fetch as jest.Mock).mockResolvedValueOnce(mockObservationResponse);

    const queryResponse = await UseCaseQuery(request);

    expect(queryResponse.Patient).toHaveLength(1);
    expect(queryResponse.Observation).toHaveLength(1);
    expect(queryResponse.Observation![0].id).toBe("obs1");
  });

  test("socialDeterminantsQuery - success", async () => {
    const mockResponse = new Response(
      JSON.stringify({
        entry: [{ resource: { resourceType: "Observation", id: "obs1" } }],
      }),
      { status: 200 },
    );

    (fetch as jest.Mock).mockResolvedValue(mockResponse);

    const queryResponse: QueryResponse = {};
    const result = await socialDeterminantsQuery(
      "1",
      fhirClient,
      queryResponse,
    );

    expect(result.Observation).toHaveLength(1);
    expect(result.Observation![0].id).toBe("obs1");
  });

  test("newbornScreeningQuery - success", async () => {
    const mockResponse = new Response(
      JSON.stringify({
        entry: [{ resource: { resourceType: "Observation", id: "obs1" } }],
      }),
      { status: 200 },
    );

    (fetch as jest.Mock).mockResolvedValue(mockResponse);

    const queryResponse: QueryResponse = {};
    const result = await newbornScreeningQuery("1", fhirClient, queryResponse);

    expect(result.Observation).toHaveLength(1);
    expect(result.Observation![0].id).toBe("obs1");
  });

  test("parseFhirSearch - single response", async () => {
    const mockResponse = new Response(
      JSON.stringify({
        entry: [{ resource: { resourceType: "Observation", id: "obs1" } }],
      }),
      { status: 200 },
    );

    const queryResponse: QueryResponse = {};
    const result = await parseFhirSearch(mockResponse, queryResponse);

    expect(result.Observation).toHaveLength(1);
    expect(result.Observation![0].id).toBe("obs1");
  });

  test("parseFhirSearch - batch response", async () => {
    const mockResponses = [
      new Response(
        JSON.stringify({
          entry: [{ resource: { resourceType: "Observation", id: "obs1" } }],
        }),
        { status: 200 },
      ),
      new Response(
        JSON.stringify({
          entry: [{ resource: { resourceType: "Condition", id: "cond1" } }],
        }),
        { status: 200 },
      ),
    ];

    const queryResponse: QueryResponse = {};
    const result = await parseFhirSearch(mockResponses, queryResponse);

    expect(result.Observation).toHaveLength(1);
    expect(result.Observation![0].id).toBe("obs1");
    expect(result.Condition).toHaveLength(1);
    expect(result.Condition![0].id).toBe("cond1");
  });
});
