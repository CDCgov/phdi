import { SectionConfig } from "./SideNav";
import React, { FC } from "react";

interface EcrSummaryProps {
  patientDetails: DisplayProps[];
  encounterDetails: DisplayProps[];
  aboutTheCondition: DisplayProps[];
}

export const ecrSummaryConfig = new SectionConfig("eCR Summary", [
  "About the Patient",
  "About the Encounter",
  "About the Condition",
]);

interface DisplayProps {
  title: string;
  value: any[] | string;
}

/**
 * Generates a JSX element to display the provided value.
 * If the value is null, undefined, an empty array, or an empty string,
 * it returns null. Otherwise, it renders the provided value as JSX.
 * @param props - The props object.
 * @param props.title - Title of the display section.
 * @param props.value - Value to be displayed.
 * @returns The JSX element representing the provided value or null if the value is empty.
 */
const Display: FC<DisplayProps> = ({ title, value }: DisplayProps) => {
  if (!value || (Array.isArray(value) && value.length === 0)) {
    return null;
  }
  return (
    <>
      <div className="grid-row">
        <div className="data-title">{title}</div>
        <div className={"grid-col-auto maxw7 text-pre-line"}>{value}</div>
      </div>
      <div className={"section__line"} />
    </>
  );
};

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
            {patientDetails.map(({ title, value }) => (
              <Display title={title} value={value} />
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
            {encounterDetails.map(({ title, value }) => (
              <Display title={title} value={value} />
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
            {aboutTheCondition.map(({ title, value }) => (
              <Display title={title} value={value} />
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
            <div className={"grid-row"}>
              <div className={"text-bold width-full"}>
                Lab results relevant to reportable condition
              </div>
              <div className={"padding-top-05"}>
                No matching lab results found in this eCR (temp)
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EcrSummary;
