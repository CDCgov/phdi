import React from "react";
import {
  DataDisplay,
  DataTableDisplay,
  DisplayDataProps,
} from "@/app/DataDisplay";
import { AccordionItemProps } from "@trussworks/react-uswds/lib/components/Accordion/Accordion";
import { Accordion } from "@trussworks/react-uswds";

interface EcrSummaryProps {
  patientDetails: DisplayDataProps[];
  encounterDetails: DisplayDataProps[];
  conditionSummary: ConditionSummary[];
  snomed?: string;
}

export interface ConditionSummary {
  title: string;
  snomed: string;
  conditionDetails: DisplayDataProps[];
  clinicalDetails: DisplayDataProps[];
  labDetails: DisplayDataProps[];
}

/**
 * Generates a JSX element to display eCR viewer summary
 * @param props - Properties for the eCR Viewer Summary section
 * @param props.patientDetails - Array of title and values to be displayed in patient details section
 * @param props.encounterDetails - Array of title and values to be displayed in encounter details section
 * @param props.conditionSummary - Array of condition details
 * @param props.snomed - SNOMED code being requested
 * @returns a react element for ECR Summary
 */
const EcrSummary: React.FC<EcrSummaryProps> = ({
  patientDetails,
  encounterDetails,
  conditionSummary,
  snomed,
}) => {
  const conditionSummaryAccordionItems: AccordionItemProps[] =
    conditionSummary.map((condition) => {
      return {
        title: condition.title,
        id: condition.title.replaceAll(" ", "-"),
        headingLevel: "h3",
        className: "side-nav-ignore",
        expanded: snomed === condition.snomed || conditionSummary.length === 1,
        content: (
          <>
            {condition.conditionDetails.map((item) => (
              <DataDisplay item={item} key={item.title} />
            ))}
            <div className="ecr-summary-title-long" id={"relevant-clinical"}>
              {"Clinical Sections Relevant to Reportable Condition"}
            </div>
            {condition.clinicalDetails.map((item) => (
              <DataTableDisplay item={item} key={item.title} />
            ))}
            <div className="ecr-summary-title-long" id={"relevant-labs"}>
              {"Lab Results Relevant to Reportable Condition"}
            </div>
            {condition.labDetails.map((item) => (
              <DataTableDisplay item={item} key={item.title} />
            ))}
          </>
        ),
      };
    });
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
            className={"summary-box-key-information side-nav-ignore"}
            id={"condition-summary"}
          >
            Condition Summary
          </h2>
          <div className="usa-summary-box__text">
            <Accordion items={conditionSummaryAccordionItems} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EcrSummary;
