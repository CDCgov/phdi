import { evaluate } from "fhirpath";
import { Bundle } from "fhir/r4";
import {
  extractFacilityAddress,
  extractPatientAddress,
  evaluatePatientName,
  PathMappings,
  evaluateEncounterDate,
  evaluatePatientContactInfo,
  noData,
} from "../../utils";
import { SectionConfig } from "./SideNav";

interface EcrViewerProps {
  fhirPathMappings: PathMappings;
  fhirBundle: Bundle;
}

export const ecrSummaryConfig = new SectionConfig("eCR Summary", [
  "About the Patient",
  "About the Encounter",
  "About the Condition",
]);

/**
 * Generates a JSX element to display the provided value.
 * If the value is null, undefined, an empty array, or an empty string,
 * it renders a predefined 'noData' JSX element.
 * Otherwise, it renders the provided value as JSX.
 * @param value - The value to be displayed. It can be an array of any type or a string.
 * @returns The JSX element representing the provided value or a 'noData' JSX element if the value is empty.
 */
const display = (value: any[] | string): JSX.Element => {
  if (!value || (Array.isArray(value) && value.length === 0)) {
    return noData;
  }
  return <>{value}</>;
};

const EcrSummary = ({ fhirPathMappings, fhirBundle }: EcrViewerProps) => {
  return (
    <div className={"info-container"}>
      <div
        className="usa-summary-box padding-3"
        aria-labelledby="summary-box-key-information"
      >
        <div className="usa-summary-box__body">
          <h3
            className="summary-box-key-information side-nav-ignore"
            id={ecrSummaryConfig.subNavItems?.[0].id}
          >
            {ecrSummaryConfig.subNavItems?.[0].title}
          </h3>
          <div className="usa-summary-box__text">
            <div className="grid-row">
              <div className="data-title">Patient Name</div>
              <div className="grid-col-auto">
                {display(evaluatePatientName(fhirBundle, fhirPathMappings))}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="data-title">DOB</div>
              <div className="grid-col-auto text-pre-line">
                {display(evaluate(fhirBundle, fhirPathMappings.patientDOB))}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="data-title">Patient Address</div>
              <div className="grid-col-auto text-pre-line">
                {display(extractPatientAddress(fhirBundle, fhirPathMappings))}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="data-title">Patient Contact</div>
              <div className="grid-col-auto text-pre-line">
                {display(
                  evaluatePatientContactInfo(fhirBundle, fhirPathMappings),
                )}
              </div>
            </div>
            <div className={"section__line"} />
          </div>
        </div>
        <div className="usa-summary-box__body">
          <h3
            className="summary-box-key-information side-nav-ignore"
            id={ecrSummaryConfig.subNavItems?.[1].id}
          >
            {ecrSummaryConfig.subNavItems?.[1].title}
          </h3>
          <div className="usa-summary-box__text">
            <div className="grid-row">
              <div className="data-title">Facility Name</div>
              <div className="grid-col-auto">
                {display(evaluate(fhirBundle, fhirPathMappings.facilityName))}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="data-title">Facility Address</div>
              <div className="grid-col-auto text-pre-line">
                {display(extractFacilityAddress(fhirBundle, fhirPathMappings))}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="data-title">Facility Contact</div>
              <div className="grid-col-auto">
                {display(
                  evaluate(fhirBundle, fhirPathMappings.facilityContact),
                )}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="data-title">Encounter Date/Time</div>
              <div className="grid-col-auto text-pre-line">
                {display(evaluateEncounterDate(fhirBundle, fhirPathMappings))}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="data-title">Encounter Type</div>
              <div className="grid-col-auto">
                {display(evaluate(fhirBundle, fhirPathMappings.encounterType))}
              </div>
            </div>
          </div>
          <div className={"section__line"} />
        </div>
        <div className="usa-summary-box__body">
          <h3
            className={"margin-bottom-105 margin-top-205 side-nav-ignore"}
            id={ecrSummaryConfig.subNavItems?.[2].id}
          >
            {ecrSummaryConfig.subNavItems?.[2].title}
          </h3>
          <div className="usa-summary-box__text">
            <div className="grid-row">
              <div className="data-title">Reportable Condition</div>
              <div className="grid-col-fill">
                {display(
                  evaluate(fhirBundle, fhirPathMappings.rrDisplayNames)[0],
                )}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="data-title">RCKMS Rule Summary</div>
              <div className="grid-col-fill text-pre-line">
                {display(
                  evaluate(
                    fhirBundle,
                    fhirPathMappings.rckmsTriggerSummaries,
                  )[0],
                )}
              </div>
            </div>
            <div className={"section__line"} />
            <div className={"grid-row"}>
              <div className={"text-bold"}>
                Clinical sections relevant to reportable condition
              </div>
              <div className={"padding-top-05"}>
                No matching clinical data found in this eCR (temp)
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className={"text-bold"}>
                Lab results relevant to reportable condition
              </div>
              <div className="usa-card__container margin-left-0 margin-right-0 margin-top-1">
                <div className="usa-card__header padding-top-2 padding-bottom-2 padding-left-3">
                  <p>
                    Hepatitis C IgG w/Rfx PCR (temp)
                    <span className="usa-tag margin-left-1 bg-error-dark text-white">
                      Abnormal
                    </span>
                  </p>
                </div>
                <div className={"card__line "} />
                <div className="usa-card__body padding-0">
                  <table className="usa-table usa-table--borderless ecrTable">
                    <thead>
                      <tr>
                        <th scope="col">Component</th>
                        <th scope="col">Value</th>
                        <th scope="col">Ref Range</th>
                        <th scope="col">Specimen</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Hepatitis C Antibody (temp)</td>
                        <td>Positive (A) (temp)</td>
                        <td>Not Detected (temp)</td>
                        <td>Blood (temp)</td>
                      </tr>
                    </tbody>
                  </table>
                  <div className={"card__line"} />
                  <div
                    className={
                      "padding-left-3 padding-right-3 padding-top-205 padding-bottom-205"
                    }
                  >
                    <div className="grid-row">
                      <div className="data-title">Analysis time</div>
                      <div className="grid-col-fill text-pre-line">
                        N/A (temp)
                      </div>
                    </div>
                    <div className={"section__line_gray"} />
                    <div className="grid-row">
                      <div className="data-title">Collection time</div>
                      <div className="grid-col-fill text-pre-line">
                        05/12/2022 6:00 AM CDT (temp)
                      </div>
                    </div>
                    <div className={"section__line_gray"} />
                    <div className="grid-row">
                      <div className="data-title">Received time</div>
                      <div className="grid-col-fill text-pre-line">
                        05/12/2022 11:30 AM CDT (temp)
                      </div>
                    </div>
                    <div className={"section__line_gray"} />
                    <div className="grid-row">
                      <div className="data-title">Notes</div>
                      <div className="grid-col-fill text-pre-line">
                        A detected result is positive and indicates the presence
                        of the virus in the sample. A not detected result
                        indicates that the test did not detect the virus in the
                        sample. This test was performed using a multiplexed
                        nucleic acid amplification test that is labeled
                        Emergence Use Only by the U.S. FDA. Results of this test
                        should not be used as the sole basis for diagnosis,
                        treatment, or other management decisions. (temp)
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EcrSummary;
