import { DataDisplay, DisplayData, DataTableDisplay } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
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
    "Symptoms and Problems",
    "Immunizations",
    "Diagnostics and Vital Signs",
    "Treatment Details",
    "Clinical Notes",
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

  const renderClinicalNotes = () => {
    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[4].id}>
            {clinicalInfoConfig.subNavItems?.[4].title}
          </span>
        </AccordianH4>
        <AccordianDiv className={"clinical_info_container"}>
          {clinicalNotes.map((item, index) => {
            let className = "";
            if (
              React.isValidElement(item.value) &&
              item.value.type == "table"
            ) {
              className = "maxw-full grid-col-12 margin-top-1";
            }
            return (
              <DataDisplay item={item} key={index} className={className} />
            );
          })}
        </AccordianDiv>
      </>
    );
  };

  const renderSymptomsAndProblems = () => {
    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[0].id}>
            {clinicalInfoConfig.subNavItems?.[0].title}
          </span>
        </AccordianH4>
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
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[1].id}>
            {clinicalInfoConfig.subNavItems?.[1].title}
          </span>
        </AccordianH4>
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
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[2].id}>
            {clinicalInfoConfig.subNavItems?.[2].title}
          </span>
        </AccordianH4>
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

  // TODO: HERE
  const renderTreatmentDetails = () => {
    const data = treatmentData.filter((item) => !React.isValidElement(item));
    return (
      <>
        <AccordianH4>
          <span id={clinicalInfoConfig.subNavItems?.[3].id}>
            {clinicalInfoConfig.subNavItems?.[3].title}
          </span>
        </AccordianH4>
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
