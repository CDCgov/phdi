import { DataDisplay, DisplayData } from "../../utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";

interface DemographicsProps {
  demographicsData: DisplayData[];
}

export const demographicsConfig = new SectionConfig("Demographics");

const Demographics = ({ demographicsData }: DemographicsProps) => {
  return (
    <AccordianSection>
      <AccordianH4>
        <span id={demographicsConfig.id}>{demographicsConfig.title}</span>
      </AccordianH4>
      <AccordianDiv>
        {demographicsData.map((item, index) => (
          <DataDisplay item={item} key={index} />
        ))}
      </AccordianDiv>
    </AccordianSection>
  );
};

export default Demographics;
