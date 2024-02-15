import { DataDisplay, DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
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
      <AccordianH4>
        <span id={socialHistoryConfig.id}>{socialHistoryConfig.title}</span>
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
