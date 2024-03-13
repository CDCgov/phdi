import { DataDisplay, DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import React from "react";

interface LabInfoProps {
  labInfo: DisplayData[];
  rrInfo: React.JSX.Element[];
}

export const LabInfo = ({ labInfo, rrInfo }: LabInfoProps) => {
  const renderLabInfo = () => {
    return (
      <>
        <AccordianH4 id={"lab-results-from"}>Lab results from</AccordianH4>
        <AccordianDiv>
          {labInfo.map((item, index) => {
            return <DataDisplay item={item} key={index} />;
          })}
          {rrInfo}
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      {(labInfo.length > 0 || rrInfo.length > 0) && renderLabInfo()}
    </AccordianSection>
  );
};

export default LabInfo;
