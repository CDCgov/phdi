import { DataDisplay } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import React from "react";

interface LabInfoProps {
  labResults: any[];
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
        {labResults.map((orgRrData: any) => (
          <>
            <AccordianH4 id={"lab-results-from"}>Lab Results from</AccordianH4>
            <AccordianDiv>
              {orgRrData.orgData.map((item: any, index: any) => (
                <DataDisplay item={item} key={index} />
              ))}
              {orgRrData.rrData}
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
