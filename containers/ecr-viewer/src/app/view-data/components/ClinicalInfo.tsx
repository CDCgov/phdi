import { DataDisplay, DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";

interface ClinicalProps {
  activeProblemsDetails: DisplayData[];
  vitalData: DisplayData[];
}

export const clinicalInfoConfig: SectionConfig = new SectionConfig(
  "Clinical Info",
  ["Symptoms and Problems"],
);

const ClinicalInfo = ({ activeProblemsDetails, vitalData }: ClinicalProps) => {
  const renderTableDetails = (tableDetails: DisplayData[]) => {
    return (
      <div>
        {tableDetails.map((item, index) => (
          <div key={index}>
            <div className="grid-col-auto text-pre-line">{item.value}</div>
            <div className={"section__line_gray"} />
          </div>
        ))}
      </div>
    );
  };

  const renderSymptomsAndProblems = () => {
    const tableData = activeProblemsDetails.filter((item) =>
      React.isValidElement(item),
    );
    const data = activeProblemsDetails.filter(
      (item) => !React.isValidElement(item),
    );
    return (
      <>
        <AccordianH4>
          <span id="symptoms-and-problems">Symptoms and Problems</span>
        </AccordianH4>
        <AccordianDiv>
          {data.map((item, index) => (
            <DataDisplay item={item} key={index} />
          ))}
          {renderTableDetails(tableData)}
        </AccordianDiv>
      </>
    );
  };

  const renderVitalDetails = () => {
    return (
      <>
        <AccordianH4>Diagnostic and Vital Signs</AccordianH4>
        <AccordianDiv>
          <div className="lh-18">
            {vitalData.map((item, index) => (
              <DataDisplay item={item} key={index} />
            ))}
          </div>
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      {activeProblemsDetails.length > 0 && renderSymptomsAndProblems()}
      {vitalData.length > 0 && renderVitalDetails()}
    </AccordianSection>
  );
};

export default ClinicalInfo;
