import { DataDisplay, DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";

interface EncounterProps {
  encounterData: DisplayData[];
  providerData: DisplayData[];
}

export const encounterConfig: SectionConfig = new SectionConfig(
  "Encounter Details",
  ["Encounter Details", "Provider Details"],
);

const EncounterDetails = ({ encounterData, providerData }: EncounterProps) => {
  const renderEncounterDetails = () => {
    return (
      <>
        <AccordianH4>
          <span id={encounterConfig.subNavItems?.[0].id}>
            {encounterConfig.subNavItems?.[0].title}
          </span>
        </AccordianH4>
        <AccordianDiv>
          {encounterData.map((item, index) => (
            <DataDisplay item={item} key={index} />
          ))}
        </AccordianDiv>
      </>
    );
  };

  const renderProviderDetails = () => {
    return (
      <>
        <AccordianH4>
          <span id={encounterConfig.subNavItems?.[1].id}>
            {encounterConfig.subNavItems?.[1].title}
          </span>
        </AccordianH4>
        <AccordianDiv>
          {providerData.map((item, index) => (
            <DataDisplay item={item} key={index} />
          ))}
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      <div>{encounterData.length > 0 && renderEncounterDetails()}</div>
      <div className="margin-top-3">
        {providerData.length > 0 && renderProviderDetails()}
      </div>
    </AccordianSection>
  );
};

export default EncounterDetails;
