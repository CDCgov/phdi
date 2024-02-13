import { DataDisplay, DisplayData, DataTableDisplay } from "@/app/utils";
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
  treatmentData: DisplayData[];
  clinicalNotes: DisplayData[];
}

export const clinicalInfoConfig: SectionConfig = new SectionConfig(
  "Clinical Info",
  ["Clinical Notes", "Symptoms and Problems"],
);

const ClinicalInfo = ({
  activeProblemsDetails,
  vitalData,
  treatmentData,
  clinicalNotes
}: ClinicalProps) => {
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
          {data.map((item, index) => (
            <DataDisplay item={item} key={index} />
          ))}
          {renderTableDetails(tableData)}
        </AccordianDiv>
      </>
    );
  };

  const renderTreatmentDetails = () => {
    const tableData = treatmentData.filter((item) =>
      React.isValidElement(item),
    );
    const data = treatmentData.filter((item) => !React.isValidElement(item));
    return (
      <>
        <AccordianH3>Treatment Details</AccordianH3>
        <AccordianDiv>
          {data.map((item, index) => (
            <DataTableDisplay item={item} key={index} />
          ))}
          <div className={"section__line_gray margin-y-2"} />
        </AccordianDiv>
      </>
    );
  };

  const renderVitalDetails = () => {
    return (
      <>
        <AccordianH3>Diagnostic and Vital Signs</AccordianH3>
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

  const renderClinicalNotes = () => {
    return(<>
      <AccordianH3><span id={"clinical-notes"}>Clinical Notes</span></AccordianH3>
      <AccordianDiv>
        {clinicalNotes.map((item, index) => (
          <DataDisplay item={item} key={index} />
        ))}
      </AccordianDiv>
    </>)
  }

  return (
    <AccordianSection>
      {clinicalNotes?.length > 0 && renderClinicalNotes()}
      {activeProblemsDetails.length > 0 && renderSymptomsAndProblems()}
      {treatmentData.length > 0 && renderTreatmentDetails()}
      {vitalData.length > 0 && renderVitalDetails()}
    </AccordianSection>
  );
};

export default ClinicalInfo;
