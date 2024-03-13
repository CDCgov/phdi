import { DataDisplay, DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import React from "react";

interface LabInfoProps {
  labInfo: DisplayData[];
  labResults: React.JSX.Element[];
}

/**
 * Renders lab information and RR info in an accordion section.
 * @param {Object} props - The props object.
 * @param {DisplayData[]} props.labInfo - Array of lab information items.
 * @param {React.JSX.Element[]} props.labResults - Array of Lab result items.
 * @returns {React.JSX.Element} React element representing the LabInfo component.
 */
export const LabInfo = ({
  labInfo,
  labResults,
}: LabInfoProps): React.JSX.Element => {
  const renderLabInfo = () => {
    return (
      <>
        <AccordianH4 id={"lab-results-from"}>Lab Results from</AccordianH4>
        <AccordianDiv>
          {labInfo.map((item, index) => {
            return <DataDisplay item={item} key={index} />;
          })}
          {labResults}
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      {(labInfo.length > 0 || labResults.length > 0) && renderLabInfo()}
    </AccordianSection>
  );
};

export default LabInfo;
