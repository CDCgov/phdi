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

export const demoData = {
  "demo-cancer": {
    FirstName: "Lee",
    LastName: "Shaw",
    DOB: "1975-12-06",
    MRN: "8692756",
    Phone: "517-425-1398",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "cancer",
  },
  "demo-sti-chlamydia": {
    FirstName: "Chlamydia",
    LastName: "JMC",
    DOB: "2001-05-07",
    MRN: "b50z-wayszq-ofib",
    Phone: "+83 606 312380",
    FhirServer: "JMC Meld: Direct",
    UseCase: "chlamydia",
  },
  "demo-sti-gonorrhea": {
    FirstName: "GC",
    LastName: "JMC",
    DOB: "1998-05-31",
    MRN: "JMC-1002",
    Phone: "+91 35551643",
    FhirServer: "JMC Meld: Direct",
    UseCase: "gonorrhea",
  },
  "demo-newborn-screening": {
    FirstName: "Mango",
    LastName: "Smith",
    DOB: "2024-07-12",
    MRN: "67890",
    Phone: "555-123-4567",
    FhirServer: "HELIOS Meld: eHealthExchange",
    UseCase: "newborn-screening",
  },
  "demo-social-determinants": {
    FirstName: "Veronica",
    LastName: "Blackstone",
    DOB: "1998-06-18",
    MRN: "34972316",
    Phone: "937-379-3497",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "social-determinants",
  },
  "demo-sti-syphilis": {
    FirstName: "Veronica",
    LastName: "Blackstone",
    DOB: "1998-06-18",
    MRN: "34972316",
    Phone: "937-379-3497",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "syphilis",
  },
};
export type demoDataUseCase = keyof typeof demoData;
