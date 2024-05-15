import {
  AccordionSection,
  AccordionH4,
  AccordionDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";
import { DataDisplay, DisplayDataProps } from "@/app/DataDisplay";

interface SocialHistoryProps {
  socialData: DisplayDataProps[];
}

export const socialHistoryConfig: SectionConfig = {
  id: "social-history",
  title: "Social History",
};

/**
 * Functional component for displaying social history.
 * @param props - Props for social history.
 * @param props.socialData - The fields to be displayed.
 * @returns The JSX element representing social history.
 */
const SocialHistory: React.FC<SocialHistoryProps> = ({ socialData }) => {
  return (
    <AccordionSection>
      <AccordionH4>
        <span id={socialHistoryConfig.id}>{socialHistoryConfig.title}</span>
      </AccordionH4>
      <AccordionDiv>
        {socialData.map((item, index) => (
          <DataDisplay item={item} key={index} />
        ))}
      </AccordionDiv>
    </AccordionSection>
  );
};

export default SocialHistory;
