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
