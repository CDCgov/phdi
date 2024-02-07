import { DataDisplay, DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";

interface SocialHistoryProps {
  socialData: DisplayData[];
}

export const socialHistoryConfig: SectionConfig = {
  id: "social-history",
  title: "Social History",
};

const SocialHistory = ({ socialData }: SocialHistoryProps) => {
  return (
    <AccordianSection>
      <AccordianH3>
        <span id={socialHistoryConfig.id}>{socialHistoryConfig.title}</span>
      </AccordianH3>
      <AccordianDiv>
        {socialData.map((item, index) => (
          <DataDisplay item={item} key={index} />
        ))}
      </AccordianDiv>
    </AccordianSection>
  );
};

export default SocialHistory;
