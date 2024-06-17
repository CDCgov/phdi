import React from "react";
import {
  DataDisplay,
  DataTableDisplay,
  DisplayDataProps,
} from "@/app/DataDisplay";

interface EcrSummaryProps {
  patientDetails: DisplayDataProps[];
  encounterDetails: DisplayDataProps[];
  aboutTheCondition: DisplayDataProps[];
  relevantClinical: DisplayDataProps[];
}

/**
 * Generates a JSX element to display eCR viewer summary
 * @param props - Properties for the eCR Viewer Summary section
 * @param props.patientDetails - Array of title and values to be displayed in patient details section
 * @param props.encounterDetails - Array of title and values to be displayed in encounter details section
 * @param props.aboutTheCondition - Array of title and values to be displayed about the condition section
 * @param props.relevantClinical - Array of title and tables to be displayed about the relevant clinical details
 * @returns a react element for ECR Summary
 */
const EcrSummary: React.FC<EcrSummaryProps> = ({
  patientDetails,
  encounterDetails,
  aboutTheCondition,
  relevantClinical,
}) => {
  return (
    <div className={"info-container"}>
      <div
        className="usa-summary-box padding-3"
        aria-labelledby="summary-box-key-information"
      >
        <div className="usa-summary-box__body margin-bottom-05">
          <h2
            className="summary-box-key-information side-nav-ignore"
            id={"about-the-patient"}
          >
            About the Patient
          </h2>
          <div className="usa-summary-box__text">
            {patientDetails.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
          </div>
        </div>
        <div className="usa-summary-box__body">
          <h2
            className="summary-box-key-information side-nav-ignore"
            id="about-the-encounter"
          >
            About the Encounter
          </h2>
          <div className="usa-summary-box__text">
            {encounterDetails.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
          </div>
        </div>
        <div className="usa-summary-box__body">
          <h2
            className={"summary-box-key-information side-nav-ignore"}
            id={"about-the-condition"}
          >
            About the Condition
          </h2>
          <div className="usa-summary-box__text">
            {aboutTheCondition.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
            <div className="ecr-summary-title-long">
              {"Clinical Sections Relevant to Reportable Condition"}
            </div>
            {relevantClinical.map((item) => (
              <DataTableDisplay item={item} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EcrSummary;
