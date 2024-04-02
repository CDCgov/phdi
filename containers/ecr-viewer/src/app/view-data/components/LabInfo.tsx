import { DataDisplay, DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import React from "react";
import { LabReportElementData } from "@/app/labs/utils";

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
  console.log(labResults);
  const renderLabInfo = () => {
    return (
      <>
        {labResults.map((labResult: any) => (
          <>
            <AccordianH4 id={"lab-results-from"}>Lab Results from</AccordianH4>
            <AccordianDiv>
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
