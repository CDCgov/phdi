import { DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";

interface ClinicalProps {
  activeProblemsDetails: DisplayData[];
  vitalData: DisplayData[];
  immunizationsDetails: DisplayData[];
}

export const clinicalInfoConfig: SectionConfig = new SectionConfig(
  "Clinical Info",
  ["Symptoms and Problems"],
  // immunizationsDetails,
);

const ClinicalInfo = ({
  activeProblemsDetails,
  immunizationsDetails,
  vitalData,
}: ClinicalProps) => {
  const renderData = (item: any, index: number) => {
    return (
      <div key={index}>
        <div className="grid-row">
          <div className="data-title">
            <h4>{item.title}</h4>
          </div>
          <div className="grid-col-auto maxw7 text-pre-line">{item.value}</div>
        </div>
        <div className={"section__line_gray"} />
      </div>
    );
  };

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
        <AccordianH3>Symptoms and Problems</AccordianH3>
        <AccordianDiv>
          {data.map((item, index) => renderData(item, index))}
          {/* {renderTableDetails(tableData)} */}
        </AccordianDiv>
      </>
    );
  };

  const renderImmunizationsDetails = () => {
    return (
      <>
        <AccordianH3>Immunizations</AccordianH3>
        <AccordianDiv>{renderTableDetails(immunizationsDetails)}</AccordianDiv>
      </>
    );
  };

  const renderVitalDetails = () => {
    return (
      <>
        <AccordianH3>Diagnostic and Vital Signs</AccordianH3>
        <AccordianDiv>
          <div className="lh-18">
            {vitalData.map((item, index) => renderData(item, index))}
          </div>
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      {activeProblemsDetails.length > 0 && renderSymptomsAndProblems()}
      {immunizationsDetails.length > 0 && renderImmunizationsDetails()}
      {vitalData.length > 0 && renderVitalDetails()}
    </AccordianSection>
  );
};

export default ClinicalInfo;
