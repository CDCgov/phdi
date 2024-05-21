import {
  AccordionSection,
  AccordionH4,
  AccordionDiv,
} from "../component-utils";
import React from "react";
import { DataDisplay, DisplayDataProps } from "@/app/DataDisplay";

interface EncounterProps {
  encounterData: DisplayDataProps[];
  providerData: DisplayDataProps[];
}

/**
 * Functional component for displaying encounter details.
 * @param props - Props containing encounter details.
 * @param props.encounterData - The encounter data to be displayed.
 * @param props.providerData - The provider details to be displayed.
 * @returns The JSX element representing the encounter details.
 */
const EncounterDetails = ({ encounterData, providerData }: EncounterProps) => {
  const renderEncounterDetails = () => {
    return (
      <>
        <AccordionH4 id={"encounter-details"}>Encounter Details</AccordionH4>
        <AccordionDiv>
          {encounterData.map((item, index) => (
            <DataDisplay item={item} key={index} />
          ))}
        </AccordionDiv>
      </>
    );
  };

  const renderProviderDetails = () => {
    return (
      <>
        <AccordionH4 id={"provider-details"}>Provider Details</AccordionH4>
        <AccordionDiv>
          {providerData.map((item, index) => (
            <DataDisplay item={item} key={index} />
          ))}
        </AccordionDiv>
      </>
    );
  };

  return (
    <AccordionSection>
      <div>{encounterData.length > 0 && renderEncounterDetails()}</div>
      <div className="margin-top-3">
        {providerData.length > 0 && renderProviderDetails()}
      </div>
    </AccordionSection>
  );
};

export default EncounterDetails;
