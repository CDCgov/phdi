/**
 * A Data Class designed to store and manipulate various code values used
 * to create a fully customized FHIR query. The class holds instance variables
 * for each of four types of input codes (lab LOINCs, SNOMED/conditions, RXNorm,
 * and Class/System-Type); the class uses these to automatically compile query
 * strings for each subtype of eCR query that can be built using those codes'
 * information.
 */
export class CustomQuery {
  // Store four types of input codes
  labCodes: string[] = [];
  snomedCodes: string[] = [];
  rxnormCodes: string[] = [];
  classTypeCodes: string[] = [];

  // Need default initialization of query strings outstide constructor,
  // since the `try` means we might not find the JSON spec
  observationQuery: string = "";
  diagnosticReportQuery: string = "";
  conditionQuery: string = "";
  medicationRequestQuery: string = "";
  socialHistoryQuery: string = "";
  encounterQuery: string = "";
  encounterClassTypeQuery: string = "";

  // Some queries need to be batched in waves because their encounter references
  // might depend on demographic information
  hasSecondEncounterQuery: boolean = false;

  /**
   * Creates a CustomQuery Object. The constructor accepts a JSONspec, a
   * DIBBs-defined JSON structure consisting of four keys corresponding to
   * the four types of codes this data class encompasses. These Specs are
   * currently located in the `customQueries` directory of the app.
   * @param jsonSpec A JSON Object containing four code fields to load.
   * @param patientId The ID of the patient to build into query strings.
   */
  constructor(jsonSpec: any, patientId: string) {
    try {
      this.labCodes = jsonSpec?.labCodes || [];
      this.snomedCodes = jsonSpec?.snomedCodes || [];
      this.rxnormCodes = jsonSpec?.rxnormCodes || [];
      this.classTypeCodes = jsonSpec?.classTypeCodes || [];
      this.hasSecondEncounterQuery = jsonSpec?.hasSecondEncounterQuery || false;
      this.compileQueries(patientId);
    } catch (error) {
      console.error("Could not create CustomQuery Object: ", error);
    }
  }

  /**
   * Compile the stored code information and given patientID into all applicable
   * query strings for later use. If a particular code category has no values in
   * the provided spec (e.g. a Newborn Screening case will have no rxnorm codes),
   * any query built using those codes' filter will be left as the empty string.
   * @param patientId The ID of the patient to query for.
   */
  compileQueries(patientId: string): void {
    const labsFilter = this.labCodes.join(",");
    const snomedFilter = this.snomedCodes.join(",");
    const rxnormFilter = this.rxnormCodes.join(",");
    const classTypeFilter = this.classTypeCodes.join(",");

    this.observationQuery =
      labsFilter !== ""
        ? `/Observation?subject=Patient/${patientId}&code=${labsFilter}`
        : "";
    this.diagnosticReportQuery =
      labsFilter !== ""
        ? `/DiagnosticReport?subject=${patientId}&code=${labsFilter}`
        : "";
    this.conditionQuery =
      snomedFilter !== ""
        ? `/Condition?subject=${patientId}&code=${snomedFilter}`
        : "";
    this.medicationRequestQuery =
      rxnormFilter !== ""
        ? `/MedicationRequest?subject=${patientId}&code=${rxnormFilter}&_include=MedicationRequest:medication&_include=MedicationRequest:medication.administration`
        : "";
    this.socialHistoryQuery = `/Observation?subject=${patientId}&category=social-history`;
    this.encounterQuery =
      snomedFilter !== ""
        ? `/Encounter?subject=${patientId}&reason-code=${snomedFilter}`
        : "";
    this.encounterClassTypeQuery =
      classTypeFilter !== ""
        ? `/Encounter?subject=${patientId}&class=${classTypeFilter}`
        : "";
  }

  /**
   * Yields all non-empty-string queries compiled using the stored codes.
   * @returns A list of queries.
   */
  getAllQueries(): string[] {
    const queryRequests: string[] = [
      this.observationQuery,
      this.diagnosticReportQuery,
      this.conditionQuery,
      this.medicationRequestQuery,
      this.socialHistoryQuery,
      this.encounterQuery,
      this.encounterClassTypeQuery,
    ];
    const filteredRequests = queryRequests.filter((q) => q !== "");
    return filteredRequests;
  }

  /**
   * Sometimes, only a single query is desired rather than a full list. In
   * those cases, this function returns a single specified query string.
   * @param desiredQuery The type of query the user wants.
   * @returns The compiled query string for that type.
   */
  getQuery(desiredQuery: string): string {
    switch (desiredQuery) {
      case "observation":
        return this.observationQuery;
      case "diagnostic":
        return this.diagnosticReportQuery;
      case "condition":
        return this.conditionQuery;
      case "medicationRequest":
        return this.medicationRequestQuery;
      case "social":
        return this.socialHistoryQuery;
      case "encounter":
        return this.encounterQuery;
      case "encounterClass":
        return this.encounterClassTypeQuery;
      default:
        return "";
    }
  }
}
