import React from "react";
import { AccordionSection } from "@/app/view-data/component-utils";
import { DataDisplay, DisplayDataProps } from "@/app/DataDisplay";

interface UnavailableInfoProps {
  demographicsUnavailableData: DisplayDataProps[];
  socialUnavailableData: DisplayDataProps[];
  encounterUnavailableData: DisplayDataProps[];
  providerUnavailableData: DisplayDataProps[];
  reasonForVisitUnavailableData: DisplayDataProps[];
  activeProblemsUnavailableData: DisplayDataProps[];
  vitalUnavailableData: DisplayDataProps[];
  treatmentData: DisplayDataProps[];
  clinicalNotesData: DisplayDataProps[];
  immunizationsUnavailableData: DisplayDataProps[];
  ecrMetadataUnavailableData: DisplayDataProps[];
}

/**
 * Function component for displaying data that is unavailable in the eCR viewer.
 * @param props The properties for unavailable information
 * @param props.demographicsUnavailableData The unavailable demographic data
 * @param props.socialUnavailableData The unavailable social data
 * @param props.encounterUnavailableData The unavailable encounter data
 * @param props.providerUnavailableData The unavailable provider data
 * @param props.reasonForVisitUnavailableData The unavailable reason for visit data
 * @param props.activeProblemsUnavailableData The unavailable active problems data
 * @param props.immunizationsUnavailableData The unavailable immunizations data
 * @param props.vitalUnavailableData The unavailable vital data
 * @param props.treatmentData The unavailable treatment data
 * @param props.clinicalNotesData The unavailable clinical notes
 * @param props.ecrMetadataUnavailableData The unavailable ecr meta data
 * @returns The JSX element representing all unavailable data.
 */
const UnavailableInfo: React.FC<UnavailableInfoProps> = ({
  demographicsUnavailableData,
  socialUnavailableData,
  encounterUnavailableData,
  providerUnavailableData,
  reasonForVisitUnavailableData,
  activeProblemsUnavailableData,
  immunizationsUnavailableData,
  vitalUnavailableData,
  treatmentData,
  clinicalNotesData,
  ecrMetadataUnavailableData,
}) => {
  const renderSection = (sectionTitle: string, data: DisplayDataProps[]) => {
    return (
      <div className="margin-bottom-4">
        <h3 className="usa-summary-box__heading padding-bottom-205 unavailable-info">
          {sectionTitle}
        </h3>
        <div className="usa-summary-box__text">
          {data.map((item, index) => (
            <DataDisplay
              item={{ ...item, value: "No data" }}
              className={"text-italic text-base"}
              key={index}
            />
          ))}
        </div>
      </div>
    );
  };

  return (
    <AccordionSection>
      {demographicsUnavailableData?.length > 0 &&
        renderSection("Demographics", demographicsUnavailableData)}
      {socialUnavailableData?.length > 0 &&
        renderSection("Social History", socialUnavailableData)}
      {encounterUnavailableData?.length > 0 &&
        renderSection("Encounter Details", encounterUnavailableData)}
      {clinicalNotesData?.length > 0 &&
        renderSection("Clinical Notes", clinicalNotesData)}
      {providerUnavailableData.length > 0 &&
        renderSection("Provider Details", providerUnavailableData)}
      {(reasonForVisitUnavailableData?.length > 0 ||
        activeProblemsUnavailableData?.length > 0) &&
        renderSection("Symptoms and Problems", activeProblemsUnavailableData)}
      {vitalUnavailableData?.length > 0 &&
        renderSection("Diagnostics and Vital Signs", vitalUnavailableData)}
      {immunizationsUnavailableData?.length > 0 &&
        renderSection("Immunizations", immunizationsUnavailableData)}
      {treatmentData?.length > 0 &&
        renderSection("Treatment Details", treatmentData)}
      {ecrMetadataUnavailableData?.length > 0 &&
        renderSection("eCR Metadata", ecrMetadataUnavailableData)}
    </AccordionSection>
  );
};

export default UnavailableInfo;
