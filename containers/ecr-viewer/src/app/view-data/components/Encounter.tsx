import { DataDisplay, DisplayDataProps } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import React from "react";

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
        <AccordianH4 id={"encounter-details"}>Encounter Details</AccordianH4>
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
        <AccordianH4 id={"provider-details"}>Provider Details</AccordianH4>
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
