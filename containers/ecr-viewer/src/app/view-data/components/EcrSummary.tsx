import { evaluate } from "fhirpath";
import { Bundle } from "fhir/r4";
import {
  extractFacilityAddress,
  extractPatientAddress,
  evaluatePatientName,
  PathMappings,
  evaluateEncounterDate,
  evaluatePatientContactInfo,
} from "../../utils";
import { SectionConfig } from "./SideNav";
import React, { FC } from "react";

interface EcrViewerProps {
  fhirPathMappings: PathMappings;
  fhirBundle: Bundle;
}

export const ecrSummaryConfig = new SectionConfig("eCR Summary", [
  "About the Patient",
  "About the Encounter",
  "About the Condition",
]);

interface DisplayProps {
  title: string;
  value: any[] | string;
  classNames: string;
}

/**
 * Generates a JSX element to display the provided value.
 * If the value is null, undefined, an empty array, or an empty string,
 * it returns null. Otherwise, it renders the provided value as JSX.
 * @param props - The props object.
 * @param props.title - Title of the display section.
 * @param props.value - Value to be displayed.
 * @param [props.classNames] - Class names to be applied to the value.
 * @returns The JSX element representing the provided value or null if the value is empty.
 */
const Display: FC<DisplayProps> = ({
  title,
  value,
  classNames,
}: DisplayProps) => {
  if (!value || (Array.isArray(value) && value.length === 0)) {
    return null;
  }
  return (
    <>
      <div className="grid-row">
        <div className="data-title">{title}</div>
        <div className={classNames}>{value}</div>
      </div>
      <div className={"section__line"} />
    </>
  );
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
            <Display
              title="Patient Name"
              value={evaluatePatientName(fhirBundle, fhirPathMappings)}
              classNames="grid-col-auto"
            />
            <Display
              title="DOB"
              value={evaluate(fhirBundle, fhirPathMappings.patientDOB)}
              classNames="grid-col-auto text-pre-line"
            />
            <Display
              title="Patient Address"
              value={extractPatientAddress(fhirBundle, fhirPathMappings)}
              classNames="grid-col-auto text-pre-line"
            />
            <Display
              title="Patient Contact"
              value={evaluatePatientContactInfo(fhirBundle, fhirPathMappings)}
              classNames="grid-col-auto text-pre-line"
            />
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
            <Display
              title="Facility Name"
              value={evaluate(fhirBundle, fhirPathMappings.facilityName)}
              classNames="grid-col-auto"
            />
            <Display
              title="Facility Address"
              value={extractFacilityAddress(fhirBundle, fhirPathMappings)}
              classNames="grid-col-auto text-pre-line"
            />
            <Display
              title="Facility Contact"
              value={evaluate(fhirBundle, fhirPathMappings.facilityContact)}
              classNames="grid-col-auto"
            />
            <Display
              title="Encounter Date/Time"
              value={evaluateEncounterDate(fhirBundle, fhirPathMappings)}
              classNames="grid-col-auto text-pre-line"
            />
            <Display
              title="Encounter Type"
              value={evaluate(fhirBundle, fhirPathMappings.encounterType)}
              classNames="grid-col-auto"
            />
          </div>
        </div>
        <div className="usa-summary-box__body">
          <h3
            className={"margin-bottom-105 margin-top-205 side-nav-ignore"}
            id={ecrSummaryConfig.subNavItems?.[2].id}
          >
            {ecrSummaryConfig.subNavItems?.[2].title}
          </h3>
          <div className="usa-summary-box__text">
            <Display
              title="Reportable Condition"
              value={evaluate(fhirBundle, fhirPathMappings.rrDisplayNames)[0]}
              classNames="grid-col-fill"
            />
            <Display
              title="RCKMS Rule Summary"
              value={
                evaluate(fhirBundle, fhirPathMappings.rckmsTriggerSummaries)[0]
              }
              classNames="grid-col-fill text-pre-line"
            />
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
