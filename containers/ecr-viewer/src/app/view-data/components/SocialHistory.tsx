import { DataDisplay, DisplayDataProps } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import React from "react";

interface SocialHistoryProps {
  socialData: DisplayDataProps[];
}

/**
 * Functional component for displaying social history.
 * @param props - Props for social history.
 * @param props.socialData - The fields to be displayed.
 * @returns The JSX element representing social history.
 */
const SocialHistory: React.FC<SocialHistoryProps> = ({ socialData }) => {
  return (
    <AccordianSection>
      <AccordianH4>
        <span id={"social-history"}>Social History</span>
      </AccordianH4>
      <AccordianDiv>
        {socialData.map((item, index) => (
          <DataDisplay item={item} key={index} />
        ))}
      </AccordianDiv>
    </AccordianSection>
  );
};

export default SocialHistory;
