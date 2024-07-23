import React from "react";
import {
  DataDisplay,
  DataTableDisplay,
  DisplayDataProps,
} from "@/app/DataDisplay";
import { Tag } from "@trussworks/react-uswds";

interface EcrSummaryProps {
  patientDetails: DisplayDataProps[];
  encounterDetails: DisplayDataProps[];
  aboutTheCondition: DisplayDataProps[];
  relevantClinical: DisplayDataProps[];
  relevantLabs: DisplayDataProps[];
}

/**
 * Generates a JSX element to display eCR viewer summary
 * @param props - Properties for the eCR Viewer Summary section
 * @param props.patientDetails - Array of title and values to be displayed in patient details section
 * @param props.encounterDetails - Array of title and values to be displayed in encounter details section
 * @param props.aboutTheCondition - Array of title and values to be displayed about the condition section
 * @param props.relevantClinical - Array of title and tables to be displayed about the relevant clinical details
 * @param props.relevantLabs - Array of title and tables to be displayed about the relevant lab results
 * @returns a react element for ECR Summary
 */
const EcrSummary: React.FC<EcrSummaryProps> = ({
  patientDetails,
  encounterDetails,
  aboutTheCondition,
  relevantClinical,
  relevantLabs,
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
            id={"patient-summary"}
          >
            Patient Summary
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
            id="encounter-summary"
          >
            Encounter Summary
          </h2>
          <div className="usa-summary-box__text">
            {encounterDetails.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
          </div>
        </div>
        <div className="usa-summary-box__body">
          <h2
            className={
              "summary-box-key-information side-nav-ignore header-with-tag"
            }
            id={"condition-summary"}
          >
            <div>Condition Summary</div>
            <div>
              <Tag className="tag-info">
                {numConditionsText(aboutTheCondition)}
              </Tag>
            </div>
          </h2>
          <div className="usa-summary-box__text">
            {aboutTheCondition.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
            <div className="ecr-summary-title-long" id={"relevant-clinical"}>
              {"Clinical Sections Relevant to Reportable Condition"}
            </div>
            {relevantClinical &&
              relevantClinical.length > 0 &&
              relevantClinical.map((item, index) => (
                <div key={index}>
                  <DataTableDisplay item={item} />
                </div>
              ))}
            <div className="ecr-summary-title-long" id={"relevant-labs"}>
              {"Lab Results Relevant to Reportable Condition"}
            </div>
            {relevantLabs &&
              relevantLabs.length > 0 &&
              relevantLabs.map((item, index) => (
                <div key={index}>
                  <DataTableDisplay item={item} />
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Returns a formatted string indicating the number of reportable conditions.
 * @param conditionDetails - An array of objects representing the relevant condition details.
 * @returns A formatted string that specifies the number of conditions found.
 */
export const numConditionsText = (conditionDetails: DisplayDataProps[]) => {
  let numConditions = 0;
  const reportableConditions = conditionDetails.find(
    (item) => item.title === "Reportable Condition",
  );
  if (
    reportableConditions &&
    React.isValidElement(reportableConditions.value)
  ) {
    numConditions = reportableConditions.value.props.children.length;
  }
  const conditionsText =
    numConditions === 1
      ? `${numConditions} CONDITION FOUND`
      : `${numConditions} CONDITIONS FOUND`;
  return conditionsText;
};

export default EcrSummary;
