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

export const UseCaseToQueryName: {
  [key in USE_CASES]: string;
} = {
  "social-determinants": "Social Determinants of Health",
  "newborn-screening": "Newborn Screening",
  syphilis: "Congenital syphilis (disorder)",
  gonorrhea: "Gonorrhea (disorder)",
  chlamydia: "Chlamydia trachomatis infection (disorder)",
  cancer: "Cancer (Leukemia)",
};

/**
 * Labels and values for the query options dropdown on the query page
 */
export const demoQueryOptions = [
  { value: "cancer", label: "Cancer case investigation" },
  { value: "chlamydia", label: "Chlamydia case investigation" },
  { value: "gonorrhea", label: "Gonorrhea case investigation" },
  { value: "newborn-screening", label: "Newborn screening follow-up" },
  {
    value: "social-determinants",
    label: "Gather social determinants of health",
  },
  { value: "syphilis", label: "Syphilis case investigation" },
];

/*
 * Map between the queryType property used to define a demo use case's options,
 * and the name of that query for purposes of searching the DB.
 */
const demoQueryLabels = demoQueryOptions.map((dqo) => dqo.label);
export const QueryTypeToQueryName: {
  [key in (typeof demoQueryLabels)[number]]: string;
} = {
  "Gather social determinants of health": "Social Determinants of Health",
  "Newborn screening follow-up": "Newborn Screening",
  "Syphilis case investigation": "Congenital syphilis (disorder)",
  "Gonorrhea case investigation": "Gonorrhea (disorder)",
  "Chlamydia case investigation": "Chlamydia trachomatis infection (disorder)",
  "Cancer case investigation": "Cancer (Leukemia)",
};

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
  "OPHDST Meld: Direct",
] as const;
export type FHIR_SERVERS = (typeof FhirServers)[number];

//Create type to specify the demographic data fields for a patient
export type DemoDataFields = {
  FirstName: string;
  LastName: string;
  DOB: string;
  MRN: string;
  Phone: string;
  FhirServer: FHIR_SERVERS;
  UseCase: USE_CASES;
};

/*Type to specify the different patient types*/
export type PatientType =
  | "cancer"
  | "sti-chlamydia-positive"
  | "sti-gonorrhea-positive"
  | "newborn-screening-technical-fail"
  | "newborn-screening-referral"
  | "newborn-screening-pass"
  | "social-determinants"
  | "sti-syphilis-positive";

/*
Demo patient data used to populate the form fields with each value being a type of DemoDataFields
*/
export const demoData: Record<PatientType, DemoDataFields> = {
  cancer: {
    FirstName: "Lee",
    LastName: "Shaw",
    DOB: "1975-12-06",
    MRN: "8692756",
    Phone: "517-425-1398",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "cancer",
  },
  "sti-chlamydia-positive": {
    FirstName: "Chlamydia",
    LastName: "JMC",
    DOB: "2001-05-07",
    MRN: "b50z-wayszq-ofib",
    Phone: "",
    FhirServer: "JMC Meld: Direct",
    UseCase: "chlamydia",
  },
  "sti-gonorrhea-positive": {
    FirstName: "GC",
    LastName: "JMC",
    DOB: "1998-05-31",
    MRN: "JMC-1002",
    Phone: "",
    FhirServer: "JMC Meld: Direct",
    UseCase: "gonorrhea",
  },
  "newborn-screening-technical-fail": {
    FirstName: "Mango",
    LastName: "Smith",
    DOB: "2024-07-12",
    MRN: "67890",
    Phone: "555-123-4567",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "newborn-screening",
  },
  "newborn-screening-referral": {
    FirstName: "Watermelon",
    LastName: "McGee",
    DOB: "2024-07-12",
    MRN: "18091",
    Phone: "5555555555",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "newborn-screening",
  },
  "newborn-screening-pass": {
    FirstName: "Cucumber",
    LastName: "Hill",
    DOB: "2023-08-29",
    MRN: "18091",
    Phone: "",
    FhirServer: "CernerHelios: eHealthExchange",
    UseCase: "newborn-screening",
  },
  "social-determinants": {
    FirstName: "Veronica",
    LastName: "Blackstone",
    DOB: "1998-06-18",
    MRN: "34972316",
    Phone: "937-379-3497",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "social-determinants",
  },
  "sti-syphilis-positive": {
    FirstName: "Veronica",
    LastName: "Blackstone",
    DOB: "1998-06-18",
    MRN: "34972316",
    Phone: "937-379-3497",
    FhirServer: "HELIOS Meld: Direct",
    UseCase: "syphilis",
  },
};

type Option = {
  value: string;
  label: string;
};

/* Labels and values for the patient options that are available based on the query option selected */
export const patientOptions: Record<string, Option[]> = {
  cancer: [{ value: "cancer", label: "A patient with leukemia" }],
  chlamydia: [
    {
      value: "sti-chlamydia-positive",
      label: "A male patient with a positive chlamydia lab test",
    },
  ],
  gonorrhea: [
    {
      value: "sti-gonorrhea-positive",
      label: "A male patient with a positive gonorrhea lab test",
    },
  ],
  "newborn-screening": [
    {
      value: "newborn-screening-technical-fail",
      label: "A newborn with a technical failure on screening",
    },
    {
      value: "newborn-screening-referral",
      label: "A newborn with a hearing referral & risk indicator",
    },
    {
      value: "newborn-screening-pass",
      label: "A newborn with a passed screening",
    },
  ],
  "social-determinants": [
    {
      value: "social-determinants",
      label: "A patient with housing insecurity",
    },
  ],
  syphilis: [
    {
      value: "sti-syphilis-positive",
      label: "A patient with a positive syphilis lab test",
    },
  ],
};

/*Labels and values for the state options dropdown on the query page*/
export const stateOptions = [
  { value: "AL", label: "AL - Alabama" },
  { value: "AK", label: "AK - Alaska" },
  { value: "AS", label: "AS - American Samoa" },
  { value: "AZ", label: "AZ - Arizona" },
  { value: "AR", label: "AR - Arkansas" },
  { value: "CA", label: "CA - California" },
  { value: "CO", label: "CO - Colorado" },
  { value: "CT", label: "CT - Connecticut" },
  { value: "DE", label: "DE - Delaware" },
  { value: "DC", label: "DC - District of Columbia" },
  { value: "FL", label: "FL - Florida" },
  { value: "GA", label: "GA - Georgia" },
  { value: "GU", label: "GU - Guam" },
  { value: "HI", label: "HI - Hawaii" },
  { value: "ID", label: "ID - Idaho" },
  { value: "IL", label: "IL - Illinois" },
  { value: "IN", label: "IN - Indiana" },
  { value: "IA", label: "IA - Iowa" },
  { value: "KS", label: "KS - Kansas" },
  { value: "KY", label: "KY - Kentucky" },
  { value: "LA", label: "LA - Louisiana" },
  { value: "ME", label: "ME - Maine" },
  { value: "MD", label: "MD - Maryland" },
  { value: "MA", label: "MA - Massachusetts" },
  { value: "MI", label: "MI - Michigan" },
  { value: "MN", label: "MN - Minnesota" },
  { value: "MS", label: "MS - Mississippi" },
  { value: "MO", label: "MO - Missouri" },
  { value: "MT", label: "MT - Montana" },
  { value: "NE", label: "NE - Nebraska" },
  { value: "NV", label: "NV - Nevada" },
  { value: "NH", label: "NH - New Hampshire" },
  { value: "NJ", label: "NJ - New Jersey" },
  { value: "NM", label: "NM - New Mexico" },
  { value: "NY", label: "NY - New York" },
  { value: "NC", label: "NC - North Carolina" },
  { value: "ND", label: "ND - North Dakota" },
  { value: "MP", label: "MP - Northern Mariana Islands" },
  { value: "OH", label: "OH - Ohio" },
  { value: "OK", label: "OK - Oklahoma" },
  { value: "OR", label: "OR - Oregon" },
  { value: "PA", label: "PA - Pennsylvania" },
  { value: "PR", label: "PR - Puerto Rico" },
  { value: "RI", label: "RI - Rhode Island" },
  { value: "SC", label: "SC - South Carolina" },
  { value: "SD", label: "SD - South Dakota" },
  { value: "TN", label: "TN - Tennessee" },
  { value: "TX", label: "TX - Texas" },
  { value: "UM", label: "UM - United States Minor Outlying Islands" },
  { value: "UT", label: "UT - Utah" },
  { value: "VT", label: "VT - Vermont" },
  { value: "VI", label: "VI - Virgin Islands" },
  { value: "VA", label: "VA - Virginia" },
  { value: "WA", label: "WA - Washington" },
  { value: "WV", label: "WV - West Virginia" },
  { value: "WI", label: "WI - Wisconsin" },
  { value: "WY", label: "WY - Wyoming" },
  { value: "AA", label: "AA - Armed Forces Americas" },
  { value: "AE", label: "AE - Armed Forces Africa" },
  { value: "AE", label: "AE - Armed Forces Canada" },
  { value: "AE", label: "AE - Armed Forces Europe" },
  { value: "AE", label: "AE - Armed Forces Middle East" },
  { value: "AP", label: "AP - Armed Forces Pacific" },
];

/* Mode that pages can be in; determines what is displayed to the user */
export type Mode =
  | "search"
  | "results"
  | "customize-queries"
  | "select-query"
  | "patient-results";

/*Type to specify the expected components for each item in a value set that will be 
displayed in the CustomizeQuery component*/
export interface ValueSetItem {
  code: string;
  display: string;
  system: string;
  include: boolean;
  author: string;
  clinicalServiceType: string;
  valueSetName: string;
}

/*Type to specify the expected expected types of valueset items that will be displayed 
as separate tabs in the CusomizeQuery component*/
export interface ValueSet {
  labs: ValueSetItem[];
  medications: ValueSetItem[];
  conditions: ValueSetItem[];
}

export type ValueSetType = keyof ValueSet;

export const valueSetTypeToClincalServiceTypeMap = {
  labs: ["ostc", "lotc", "lrtc"],
  medications: ["mrtc"],
  conditions: ["dxtc", "sdtc"],
};
