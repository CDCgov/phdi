import { DataDisplay, DisplayData } from "@/app/utils";
import { AccordianSection } from "../component-utils";
import React from "react";

interface UnavailableInfoProps {
  demographicsUnavailableData: DisplayData[];
  socialUnavailableData: DisplayData[];
  encounterUnavailableData: DisplayData[];
  providerUnavailableData: DisplayData[];
  reasonForVisitUnavailableData: DisplayData[];
  activeProblemsUnavailableData: DisplayData[];
  vitalUnavailableData: DisplayData[];
  treatmentData: DisplayData[];
  clinicalNotesData: DisplayData[];
  immunizationsUnavailableData: DisplayData[];
}

const UnavailableInfo = ({
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
}: UnavailableInfoProps) => {
  const renderSection = (sectionTitle: string, data: DisplayData[]) => {
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
    <AccordianSection>
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
    </AccordianSection>
  );
};

export default UnavailableInfo;
