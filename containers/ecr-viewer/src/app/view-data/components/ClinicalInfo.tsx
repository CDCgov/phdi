import { DataDisplay, DisplayDataProps, DataTableDisplay } from "@/app/utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import React from "react";
import { addCaptionToTable } from "@/app/format-service";

interface ClinicalProps {
  reasonForVisitDetails: DisplayDataProps[];
  activeProblemsDetails: DisplayDataProps[];
  vitalData: DisplayDataProps[];
  immunizationsDetails: DisplayDataProps[];
  treatmentData: DisplayDataProps[];
  clinicalNotes: DisplayDataProps[];
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

/**
 * Functional component for displaying clinical information.
 * @param props - Props containing clinical information.
 * @param props.reasonForVisitDetails - The details of the reason for visit.
 * @param props.activeProblemsDetails - The details of active problems.
 * @param props.immunizationsDetails - The details of immunizations.
 * @param props.vitalData - The vital signs data.
 * @param props.treatmentData - The details of treatments.
 * @param props.clinicalNotes - The clinical notes data.
 * @returns The JSX element representing the clinical information.
 */
export const ClinicalInfo = ({
  reasonForVisitDetails,
  activeProblemsDetails,
  immunizationsDetails,
  vitalData,
  treatmentData,
  clinicalNotes,
}: ClinicalProps) => {
  const renderTableDetails = (tableDetails: DisplayDataProps[]) => {
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
            if (
              React.isValidElement(item.value) &&
              item.value.type == "table"
            ) {
              const modItem = {
                ...item,
                value: addCaptionToTable(
                  item.value,
                  "Miscellaneous Notes",
                  "Clinical notes from various parts of a medical record. Type of note found here depends on how the provider's EHR system onboarded to send eCR.",
                ),
              };
              return (
                <React.Fragment key={index}>
                  {renderTableDetails([modItem])}
                </React.Fragment>
              );
            }
            return <DataDisplay item={item} key={index} />;
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
          <div
            className="immunization_table"
            data-testid="immunization-history"
          >
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
