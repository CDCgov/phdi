import fetch from "node-fetch";

import {
  createBundle,
  QueryResponse,
  processResponse,
  parseFhirSearch,
} from "@/app/query-service";
import { readJsonFile } from "../shared_utils/readJsonFile";
import { DiagnosticReport, Observation, Patient } from "fhir/r4";

describe("create bundle", () => {
  it("should turn a collection of resource arrays into a search set FHIR bundle", async () => {
    const patientBundle = readJsonFile(
      "./src/app/tests/assets/BundlePatient.json",
    );
    const PatientResource = patientBundle?.entry[0].resource;
    const labsBundle = readJsonFile(
      "./src/app/tests/assets/BundleLabInfo.json",
    );
    const diagnosticReportResource = labsBundle?.entry.filter(
      (e: any) => e?.resource?.resourceType === "DiagnosticReport",
    );
    const observationResources = labsBundle?.entry.filter(
      (e: any) => e?.resource?.resourceType === "Observation",
    );
    const queryResponse: QueryResponse = {
      Patient: [PatientResource as Patient],
      DiagnosticReport: diagnosticReportResource as DiagnosticReport[],
      Observation: observationResources as Observation[],
    };

    const fhirBundle = await createBundle(queryResponse);
    expect(fhirBundle.resourceType).toEqual("Bundle");
    expect(fhirBundle.type).toEqual("searchset");
    expect(fhirBundle.total).toEqual(4);
    expect(fhirBundle.entry?.length).toEqual(4);
  });
});

describe("process response", () => {
  it("should unpack a response from the server into an array of resources", async () => {
    const patientBundle = readJsonFile(
      "./src/app/tests/assets/BundlePatient.json",
    );
    const labsBundle = readJsonFile(
      "./src/app/tests/assets/BundleLabInfo.json",
    );
    const diagnosticReportResource = labsBundle?.entry.filter(
      (e: any) => e?.resource?.resourceType === "DiagnosticReport",
    );
    const observationResources = labsBundle?.entry.filter(
      (e: any) => e?.resource?.resourceType === "Observation",
    );
    patientBundle?.entry?.push(diagnosticReportResource[0]);
    observationResources.forEach((or: any) => {
      patientBundle?.entry?.push(or);
    });

    const response = {
      status: 200,
      json: async () => patientBundle,
    } as unknown as fetch.Response;
    const resourceArray = await processResponse(response);
    expect(resourceArray.length).toEqual(4);
    expect(resourceArray.find((r) => r.resourceType === "Patient")) ===
      patientBundle?.entry[0].resource;
    expect(
      resourceArray.filter((r) => r.resourceType === "Observation").length,
    ).toEqual(2);
  });
});

describe("parse fhir search", () => {
  it("should turn the FHIR server's response into a QueryResponse struct", async () => {
    const patientBundle = readJsonFile(
      "./src/app/tests/assets/BundlePatient.json",
    );
    const labsBundle = readJsonFile(
      "./src/app/tests/assets/BundleLabInfo.json",
    );
    const diagnosticReportEntry = labsBundle?.entry.filter(
      (e: any) => e?.resource?.resourceType === "DiagnosticReport",
    );
    const observationEntries = labsBundle?.entry.filter(
      (e: any) => e?.resource?.resourceType === "Observation",
    );
    patientBundle?.entry?.push(diagnosticReportEntry[0]);
    observationEntries.forEach((or: any) => {
      patientBundle?.entry?.push(or);
    });

    const response = {
      status: 200,
      json: async () => patientBundle,
    } as unknown as fetch.Response;
    const queryResponse: QueryResponse = await parseFhirSearch(response);
    expect((queryResponse.Patient || [{}])[0]).toEqual(
      patientBundle?.entry[0]?.resource,
    );
    expect((queryResponse.DiagnosticReport || [{}])[0]).toEqual(
      diagnosticReportEntry[0]?.resource,
    );
    expect(queryResponse.Observation?.length).toEqual(2);
    const observationResources: Observation[] = observationEntries.map(
      (oe: any) => oe.resource,
    );
    queryResponse.Observation?.forEach((o: Observation) => {
      expect(observationResources).toContain(o);
    });
  });
});
