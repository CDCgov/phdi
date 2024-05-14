import { DataDisplay, DisplayDataProps } from "../../utils";
import {
  AccordionSection,
  AccordionH4,
  AccordionDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";

interface DemographicsProps {
  demographicsData: DisplayDataProps[];
}

export const demographicsConfig = new SectionConfig("Demographics");

/**
 * Functional component for displaying demographic data
 * @param demographicsData - Props for demographic data
 * @param demographicsData.demographicsData - The details of fields to be displayed of demographic data
 * @returns The JSX element representing demographic data
 */
const Demographics = ({ demographicsData }: DemographicsProps) => {
  return (
    <AccordionSection>
      <AccordionH4>
        <span id={demographicsConfig.id}>{demographicsConfig.title}</span>
      </AccordionH4>
      <AccordionDiv>
        {demographicsData.map((item, index) => (
          <DataDisplay item={item} key={index} />
        ))}
      </AccordionDiv>
    </AccordionSection>
  );
};

export default Demographics;
