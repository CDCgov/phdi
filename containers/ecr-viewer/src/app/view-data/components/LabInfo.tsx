import {
  AccordionSection,
  AccordionH4,
  AccordionDiv,
} from "../component-utils";
import React from "react";
import { ExpandCollapseButtons } from "@/app/view-data/components/ExpandCollapseButtons";
import {
  truncateLabNameWholeWord,
  formatString,
} from "@/app/services/formatService";
import { LabReportElementData } from "@/app/services/labsService";
import { DataDisplay, DisplayDataProps } from "@/app/DataDisplay";

interface LabInfoProps {
  labResults: LabReportElementData[];
}

/**
 * Renders lab information and RR info in an accordion section.
 * @param props - The props object.
 * @param props.labResults - Array of Lab result items.
 * @returns React element representing the LabInfo component.
 */
export const LabInfo = ({ labResults }: LabInfoProps): React.JSX.Element => {
  const renderLabInfo = () => {
    return (
      <>
        {labResults.map((labResult, labIndex) => {
          // This is to build the selector based off if orgId exists
          // Sometimes it doesn't, so we default to the base class
          // the orgId makes it so that when you have multiple, it can distinguish
          // which org it is modifying
          const accordionSelectorClass = labResult.organizationId
            ? `.accordion_${labResult.organizationId}`
            : ".accordion-rr";
          const buttonSelectorClass = labResult.organizationId
            ? `.acc_item_${labResult.organizationId}`
            : "h5";
          const labName = `Lab Results from 
                ${truncateLabNameWholeWord(
                  labResult.organizationDisplayDataProps[0].value as string,
                )}`;
          return (
            <div key={`${labResult.organizationId}${labIndex}`}>
              <AccordionH4 id={formatString(labName)}>{labName}</AccordionH4>
              <AccordionDiv>
                {labResult?.organizationDisplayDataProps?.map(
                  (item: DisplayDataProps, index: any) => {
                    if (item.value)
                      return <DataDisplay item={item} key={index} />;
                  },
                )}
                <div className="display-flex">
                  <div className={"margin-left-auto padding-top-1"}>
                    <ExpandCollapseButtons
                      id={"lab-info"}
                      buttonSelector={`${buttonSelectorClass} > .usa-accordion__button`}
                      accordionSelector={`${accordionSelectorClass} > .usa-accordion__content`}
                      expandButtonText={"Expand all labs"}
                      collapseButtonText={"Collapse all labs"}
                    />
                  </div>
                </div>
                {labResult.diagnosticReportDataElements}
              </AccordionDiv>
            </div>
          );
        })}
      </>
    );
  };

  return (
    <AccordionSection>
      {labResults.length > 0 && renderLabInfo()}
    </AccordionSection>
  );
};

export default LabInfo;
