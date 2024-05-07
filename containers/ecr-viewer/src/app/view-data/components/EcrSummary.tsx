import { DataDisplay, DisplayDataProps } from "../../utils";
import { SectionConfig } from "./SideNav";
import React from "react";

interface EcrSummaryProps {
  patientDetails: DisplayDataProps[];
  encounterDetails: DisplayDataProps[];
  aboutTheCondition: DisplayDataProps[];
}

export const ecrSummaryConfig = new SectionConfig("eCR Summary", [
  "About the Patient",
  "About the Encounter",
  "About the Condition",
]);

/**
 * Generates a JSX element to display eCR viewer summary
 * @param props - Properties for the eCR Viewer Summary section
 * @param props.patientDetails - Array of title and values to be displayed in patient details section
 * @param props.encounterDetails - Array of title and values to be displayed in encounter details section
 * @param props.aboutTheCondition - Array of title and values to be displayed in about the condition section
 * @returns a react element for ECR Summary
 */
const EcrSummary: React.FC<EcrSummaryProps> = ({
  patientDetails,
  encounterDetails,
  aboutTheCondition,
}) => {
  return (
    <div className={"info-container"}>
      <div
        className="usa-summary-box padding-3"
        aria-labelledby="summary-box-key-information"
      >
        <div className="usa-summary-box__body margin-bottom-05">
          <h3
            className="summary-box-key-information side-nav-ignore"
            id={ecrSummaryConfig.subNavItems?.[0].id}
          >
            {ecrSummaryConfig.subNavItems?.[0].title}
          </h3>
          <div className="usa-summary-box__text">
            {patientDetails.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
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
            {encounterDetails.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
          </div>
        </div>
        <div className="usa-summary-box__body">
          <h3
            className={"summary-box-key-information side-nav-ignore"}
            id={ecrSummaryConfig.subNavItems?.[2].id}
          >
            {ecrSummaryConfig.subNavItems?.[2].title}
          </h3>
          <div className="usa-summary-box__text">
            {aboutTheCondition.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
            <div className={"grid-row"}>
              <div className={"text-bold width-full"}>
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
