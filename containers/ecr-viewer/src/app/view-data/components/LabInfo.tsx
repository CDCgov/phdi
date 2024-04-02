import { DataDisplay, DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import React from "react";
import { LabReportElementData } from "@/app/labs/utils";
import { ExpandCollapseButtons } from "@/app/view-data/components/ExpandCollapseButtons";

interface LabInfoProps {
  labResults: LabReportElementData[];
}

/**
 * Renders lab information and RR info in an accordion section.
 * @param {Object} props - The props object.
 * @param {DisplayData[]} props.labInfo - Array of lab information items.
 * @param {React.JSX.Element[]} props.labResults - Array of Lab result items.
 * @returns {React.JSX.Element} React element representing the LabInfo component.
 */
export const LabInfo = ({ labResults }: LabInfoProps): React.JSX.Element => {
  const renderLabInfo = () => {
    return (
      <>
        {labResults.map((labResult: any) => (
          <>
            <AccordianH4 id={"lab-results-from"}>Lab Results from</AccordianH4>
            <AccordianDiv>
              <div className={"display-flex"}>
                <div className={"margin-left-auto"}>
                  <ExpandCollapseButtons
                    id={"lab-info"}
                    buttonSelector={"h5 > .usa-accordion__button"}
                    accordionSelector={".accordion-rr > .usa-accordion__content"}
                    expandButtonText={"Expand all labs"}
                    collapseButtonText={"Collapse all labs"}
                  />
                </div>
              </div>
              {labResult?.organizationDisplayData?.map(
                (item: DisplayData, index: any) => {
                  if (item.value)
                    return <DataDisplay item={item} key={index} />;
                },
              )}
              {labResult.diagnosticReportDataElements}
            </AccordianDiv>
          </>
        ))}
      </>
    );
  };

  return (
    <AccordianSection>
      {labResults.length > 0 && renderLabInfo()}
    </AccordianSection>
  );
};

export default LabInfo;
