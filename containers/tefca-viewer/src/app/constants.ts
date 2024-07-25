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
  "demo-sti-chlamydia-positive": {
    FirstName: "Chlamydia",
    LastName: "JMC",
    DOB: "2001-05-07",
    MRN: "b50z-wayszq-ofib",
    Phone: "+83 606 312380",
    FhirServer: "JMC Meld: Direct",
    UseCase: "chlamydia",
  },
  "demo-sti-gonorrhea-positive": {
    FirstName: "GC",
    LastName: "JMC",
    DOB: "1998-05-31",
    MRN: "JMC-1002",
    Phone: "+91 35551643",
    FhirServer: "JMC Meld: Direct",
    UseCase: "gonorrhea",
  },
  "demo-newborn-screening-technical-fail": {
    FirstName: "Mango",
    LastName: "Smith",
    DOB: "2024-07-12",
    MRN: "67890",
    Phone: "555-123-4567",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "newborn-screening",
  },
  "demo-newborn-screening-referral": {
    FirstName: "Watermelon",
    LastName: "McGee",
    DOB: "2024-07-12",
    MRN: "18091",
    Phone: "5555555555",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "newborn-screening",
  },
  "demo-newborn-screening-pass": {
    FirstName: "Cucumber",
    LastName: "Hill",
    DOB: "2023-08-29",
    MRN: "18091",
    Phone: "8161112222",
    FhirServer: "CernerHelios: eHealthExchange",
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
  "demo-sti-syphilis-positive": {
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

export const demoQueryOptions = [
  { value: "demo-cancer", label: "Cancer case investigation" },
  { value: "demo-sti-chlamydia", label: "Chlamydia case investigation" },
  { value: "demo-sti-gonorrhea", label: "Gonorrhea case investigation" },
  { value: "demo-newborn-screening", label: "Newborn screening follow-up" },
  {
    value: "demo-social-determinants",
    label: "Gather social determinants of health",
  },
  { value: "demo-sti-syphilis", label: "Syphilis case investigation" },
];

type Option = {
  value: string;
  label: string;
};

export const patientOptions: Record<string, Option[]> = {
  "demo-cancer": [{ value: "demo-cancer", label: "A patient with leukemia" }],
  "demo-sti-chlamydia": [
    {
      value: "demo-sti-chlamydia-positive",
      label: "A male patient with a positive chlamydia lab test",
    },
  ],
  "demo-sti-gonorrhea": [
    {
      value: "demo-sti-gonorrhea-positive",
      label: "A male patient with a positive gonorrhea lab test",
    },
  ],
  "demo-newborn-screening": [
    {
      value: "demo-newborn-screening-technical-fail",
      label: "A newborn with a technical failures on screening",
    },
    {
      value: "demo-newborn-screening-referral",
      label: "A newborn with a hearing referral & risk indicator",
    },
    {
      value: "demo-newborn-screening-pass",
      label: "A newborn with a passed screening",
    },
  ],
  "demo-social-determinants": [
    {
      value: "demo-social-determinants",
      label: "A patient with housing insecurity",
    },
  ],
  "demo-sti-syphilis": [
    {
      value: "demo-sti-syphilis-positive",
      label: "A patient with a positive syphilis lab test",
    },
  ],
};
