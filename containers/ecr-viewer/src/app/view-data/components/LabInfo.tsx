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
  const truncateLabName = (input_str: string, character_limit: number = 30) => {
    if (input_str.length <= character_limit) {
      return input_str;
    }

    const trimStr = input_str.substring(0, 30);
    const lastSpaceIndex = trimStr.lastIndexOf(" ");

    if (lastSpaceIndex === -1) {
      return input_str.length <= character_limit ? input_str : "";
    }

    // Truncate to the last full word within the limit
    return input_str.substring(0, lastSpaceIndex);
  };
  const renderLabInfo = () => {
    return (
      <>
        {labResults.map((labResult, labIndex) => (
          <div key={`${labResult.organizationId}${labIndex}`}>
            <AccordianH4 id={"lab-results-from"}>
              Lab Results from{" "}
              {truncateLabName(
                labResult.organizationDisplayData[0].value as string,
              )}
            </AccordianH4>
            <AccordianDiv>
              {labResult?.organizationDisplayData?.map(
                (item: DisplayData, index: any) => {
                  if (item.value)
                    return <DataDisplay item={item} key={index} />;
                },
              )}
              <div className="display-flex">
                <div className={"margin-left-auto padding-top-1"}>
                  <ExpandCollapseButtons
                    id={"lab-info"}
                    buttonSelector={"h5 > .usa-accordion__button"}
                    accordionSelector={`.${labResult.organizationId} > .usa-accordion__content`}
                    expandButtonText={"Expand all labs"}
                    collapseButtonText={"Collapse all labs"}
                  />
                </div>
              </div>
              {labResult.diagnosticReportDataElements}
            </AccordianDiv>
          </div>
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
