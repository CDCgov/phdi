import {
  Patient,
  Observation,
  DiagnosticReport,
  Condition,
  Encounter,
  Medication,
  MedicationAdministration,
  MedicationRequest,
} from "fhir/r4";

/**
 * The use cases that can be used in the app
 */
export const UseCases = [
  "social-determinants",
  "newborn-screening",
  "syphilis",
  "gonorrhea",
  "chlamydia",
  "cancer",
] as const;
export type USE_CASES = (typeof UseCases)[number];

/**
 * The FHIR servers that can be used in the app
 =
 */
export const FhirServers = [
  "HELIOS Meld: Direct",
  "HELIOS Meld: eHealthExchange",
  "JMC Meld: Direct",
  "JMC Meld: eHealthExchange",
  "Public HAPI: eHealthExchange",
  "OpenEpic: eHealthExchange",
  "CernerHelios: eHealthExchange",
] as const;
export type FHIR_SERVERS = (typeof FhirServers)[number];

/**
 * The sources that a query request can come from. This is used to determine if the
 * response should be of type ViewerQueryResponse or ApiQueryResponse.
 */
export const RequestSources = ["api", "viewer"] as const;
export type REQUEST_SOURCES = (typeof RequestSources)[number];

/**
 * The query response when the request source is from the Viewer UI.
 */
export type QueryResponse = {
  Patient?: Patient[];
  Observation?: Observation[];
  DiagnosticReport?: DiagnosticReport[];
  Condition?: Condition[];
  Encounter?: Encounter[];
  Medication?: Medication[];
  MedicationAdministration?: MedicationAdministration[];
  MedicationRequest?: MedicationRequest[];
};
