import {
  AccordionSection,
  AccordionH4,
  AccordionDiv,
} from "../component-utils";
import React from "react";
import { DataDisplay, DisplayDataProps } from "@/app/DataDisplay";

interface DemographicsProps {
  demographicsData: DisplayDataProps[];
}

/**
 * Functional component for displaying demographic data
 * @param demographicsData - Props for demographic data
 * @param demographicsData.demographicsData - The details of fields to be displayed of demographic data
 * @returns The JSX element representing demographic data
 */
const Demographics = ({ demographicsData }: DemographicsProps) => {
  return (
    <AccordionSection>
      <AccordionH4 id={"demographics"}>Demographics</AccordionH4>
      <AccordionDiv>
        {demographicsData.map((item, index) => (
          <DataDisplay item={item} key={index} />
        ))}
      </AccordionDiv>
    </AccordionSection>
  );
};

export default Demographics;
