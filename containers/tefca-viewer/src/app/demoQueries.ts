export type QueryStruct = {
  labCodes: string[];
  snomedCodes: string[];
  rxnormCodes: string[];
  classTypeCodes: string[];
  hasSecondEncounterQuery: boolean;
};

export const SOCIAL_DETERMINANTS_QUERY: QueryStruct = {
  labCodes: [],
  snomedCodes: [],
  rxnormCodes: [],
  classTypeCodes: [],
  hasSecondEncounterQuery: false,
};

export const CANCER_QUERY: QueryStruct = {
  labCodes: [],
  snomedCodes: ["92814006"],
  rxnormCodes: ["828265"],
  classTypeCodes: [],
  hasSecondEncounterQuery: true,
};

export const CHLAMYDIA_QUERY: QueryStruct = {
  labCodes: ["24111-7", "72828-7", "21613-5", "82810-3", "11350-6", "83317-8"],
  snomedCodes: ["2339001", "72531000052105", "102874004", "A74.9"],
  rxnormCodes: ["434692", "82122", "1649987", "1665005"],
  classTypeCodes: ["54", "441"],
  hasSecondEncounterQuery: true,
};

export const GONORRHEA_QUERY: QueryStruct = {
  labCodes: ["24111-7", "11350-6", "21613-5", "82810-3", "83317-8"],
  snomedCodes: ["15628003", "2339001", "72531000052105", "102874004"],
  rxnormCodes: ["1665005", "434692"],
  classTypeCodes: ["54", "441"],
  hasSecondEncounterQuery: true,
};

export const NEWBORN_SCREENING_QUERY: QueryStruct = {
  labCodes: [
    "73700-7",
    "73698-3",
    "54108-6",
    "54109-4",
    "58232-0",
    "57700-7",
    "73739-5",
    "73742-9",
    "2708-6",
    "8336-0",
  ],
  snomedCodes: [],
  rxnormCodes: [],
  classTypeCodes: [],
  hasSecondEncounterQuery: false,
};

export const SYPHILIS_QUERY: QueryStruct = {
  labCodes: ["LP70657-9", "53605-2"],
  snomedCodes: ["76272004", "186847001"],
  rxnormCodes: ["2671695"],
  classTypeCodes: ["54", "441"],
  hasSecondEncounterQuery: true,
};
