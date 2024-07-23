/**
 * @jest-environment node
 */

import { GET, POST } from "../../api/query/route";
import * as fs from "fs";

// Helper function to read JSON file
function readJsonFile(filePath: string): any {
  try {
    const data = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error reading JSON file from ${filePath}:`, error);
    return null;
  }
}
const PatientBundle = readJsonFile("./src/app/tests/assets/BundlePatient.json");
const PatientResource = PatientBundle?.entry[0].resource;

describe("GET Health Check", () => {
  it("should return status OK", async () => {
    const response = await GET();
    const body = await response.json();
    expect(response.status).toBe(200);
    expect(body.status).toBe("OK");
    console.log(PatientResource);
  });
});

describe("POST Query FHIR Server", () => {
  it("should return an OperationOutcome if the request body is not a Patient resource", async () => {
    const request = {
      json: async () => {
        return { resourceType: "Observation" };
      },
    };
    const response = await POST(request as any);
    const body = await response.json();
    expect(body.resourceType).toBe("OperationOutcome");
    expect(body.issue[0].diagnostics).toBe(
      "Request body is not a Patient resource.",
    );
  });

  it("should return an OperationOutcome if there are no patient identifiers to parse from the request body", async () => {
    const request = {
      json: async () => {
        return { resourceType: "Patient" };
      },
    };
    const response = await POST(request as any);
    const body = await response.json();
    expect(body.resourceType).toBe("OperationOutcome");
    expect(body.issue[0].diagnostics).toBe(
      "No patient identifiers to parse from requestBody.",
    );
  });

  it("should return an OperationOutcome if the use_case or fhir_server is missing", async () => {
    const request = {
      json: async () => {
        return PatientResource;
      },
      nextUrl: {
        searchParams: new URLSearchParams(),
      },
    };
    const response = await POST(request as any);
    const body = await response.json();
    expect(body.resourceType).toBe("OperationOutcome");
    expect(body.issue[0].diagnostics).toBe("Missing use_case or fhir_server.");
  });

  it("should return an OperationOutcome if the use_case is not valid", async () => {
    const request = {
      json: async () => {
        return PatientResource;
      },
      nextUrl: {
        searchParams: new URLSearchParams(
          "use_case=invalid&fhir_server=HELIOS Meld: Direct",
        ),
      },
    };
    const response = await POST(request as any);
    const body = await response.json();
    expect(body.resourceType).toBe("OperationOutcome");
    expect(body.issue[0].diagnostics).toBe(
      "Invalid use_case. Please provide a valid use_case. Valid use_cases include social-determinants,newborn-screening,syphilis,gonorrhea,chlamydia,cancer.",
    );
  });

  it("should return an OperationOutcome if the fhir_server is not valid", async () => {
    const request = {
      json: async () => {
        return PatientResource;
      },
      nextUrl: {
        searchParams: new URLSearchParams(
          "use_case=social-determinants&fhir_server=invalid",
        ),
      },
    };
    const response = await POST(request as any);
    const body = await response.json();
    expect(body.resourceType).toBe("OperationOutcome");
    expect(body.issue[0].diagnostics).toBe(
      "Invalid fhir_server. Please provide a valid fhir_server. Valid fhir_servers include HELIOS Meld: Direct,HELIOS Meld: eHealthExchange,JMC Meld: Direct,JMC Meld: eHealthExchange,Public HAPI: eHealthExchange,OpenEpic: eHealthExchange,CernerHelios: eHealthExchange.",
    );
  });
});
