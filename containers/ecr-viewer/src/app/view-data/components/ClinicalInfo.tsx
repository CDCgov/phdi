import { DataDisplay, DisplayData, DataTableDisplay } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";

interface ClinicalProps {
  reasonForVisitDetails: DisplayData[];
  activeProblemsDetails: DisplayData[];
  vitalData: DisplayData[];
  immunizationsDetails: DisplayData[];
  treatmentData: DisplayData[];
  clinicalNotes: DisplayData[];
}

export const clinicalInfoConfig: SectionConfig = new SectionConfig(
  "Clinical Info",
  [
    "Clinical Notes",
    "Symptoms and Problems",
    "Immunizations",
    "Diagnostics and Vital Signs",
    "Treatment Details",
  ],
);

export const ClinicalInfo = ({
  reasonForVisitDetails,
  activeProblemsDetails,
  immunizationsDetails,
  vitalData,
  treatmentData,
  clinicalNotes,
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
    return (
      <>
        <AccordianH3>
          <span id={clinicalInfoConfig.subNavItems?.[0].id}>
            {clinicalInfoConfig.subNavItems?.[0].title}
          </span>
        </AccordianH3>
        <AccordianDiv>
          <div data-testid="reason-for-visit">
            {reasonForVisitDetails.map((item, index) => (
              <DataDisplay item={item} key={index} />
            ))}
          </div>
          <div data-testid="active-problems">
            {renderTableDetails(activeProblemsDetails)}
          </div>
        </AccordianDiv>
      </>
    );
  };

  const renderImmunizationsDetails = () => {
    return (
      <>
        <AccordianH3>
          <span id={clinicalInfoConfig.subNavItems?.[1].id}>
            {clinicalInfoConfig.subNavItems?.[1].title}
          </span>
        </AccordianH3>
        <AccordianDiv>
          <div data-testid="immunization-history">
            {renderTableDetails(immunizationsDetails)}
          </div>
        </AccordianDiv>
      </>
    );
  };

  const renderVitalDetails = () => {
    return (
      <>
        <AccordianH3>
          <span id={clinicalInfoConfig.subNavItems?.[2].id}>
            {clinicalInfoConfig.subNavItems?.[2].title}
          </span>
        </AccordianH3>
        <AccordianDiv>
          <div className="lh-18" data-testid="vital-signs">
            {vitalData.map((item, index) => (
              <DataDisplay item={item} key={index} />
            ))}
          </div>
        </AccordianDiv>
      </>
    );
  };

  const renderTreatmentDetails = () => {
    const data = treatmentData.filter((item) => !React.isValidElement(item));
    return (
      <>
        <AccordianH3>
          <span id={clinicalInfoConfig.subNavItems?.[3].id}>
            {clinicalInfoConfig.subNavItems?.[3].title}
          </span>
        </AccordianH3>
        <AccordianDiv>
          <div data-testid="treatment-details">
            {data.map((item, index) => (
              <DataTableDisplay item={item} key={index} />
            ))}
          </div>
          <div className={"section__line_gray margin-y-2"} />
        </AccordianDiv>
      </>
    );
  };

  const renderClinicalNotes = () => {
    return (
      <>
        <AccordianH3>
          <span id={"clinical-notes"}>Clinical Notes</span>
        </AccordianH3>
        <AccordianDiv className={"clinical_info_container"}>
          {clinicalNotes.map((item, index) => (
            <DataDisplay item={item} key={index} className={"maxw-full"}/>
          ))}
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      {clinicalNotes?.length > 0 && renderClinicalNotes()}
      {(reasonForVisitDetails.length > 0 || activeProblemsDetails.length > 0) &&
        renderSymptomsAndProblems()}
      {treatmentData.length > 0 && renderTreatmentDetails()}
      {immunizationsDetails.length > 0 && renderImmunizationsDetails()}
      {vitalData.length > 0 && renderVitalDetails()}
    </AccordianSection>
  );
};

export default ClinicalInfo;
