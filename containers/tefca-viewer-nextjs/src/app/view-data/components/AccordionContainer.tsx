import {
  evaluateSocialData,
  evaluateEncounterData,
  evaluateProviderData,
  evaluateClinicalData,
  evaluateDemographicsData,
  PathMappings,
  evaluateLabInfoData,
} from "../../utils";
import Demographics from "./Demographics";
import SocialHistory from "./SocialHistory";
import ClinicalInfo from "./ClinicalInfo";
import { Bundle, FhirResource } from "fhir/r4";
import React, { ReactNode } from "react";
import { Accordion } from "@trussworks/react-uswds";
import LabInfo from "@/app/view-data/components/LabInfo";
import { formatString } from "@/app/format-service";

type AccordionContainerProps = {
  children?: ReactNode;
  fhirBundle: Bundle<FhirResource>;
  fhirPathMappings: PathMappings;
};

const AccordianContainer: React.FC<AccordionContainerProps> = ({
  fhirBundle,
  fhirPathMappings,
}) => {
  const demographicsData = evaluateDemographicsData(
    fhirBundle,
    fhirPathMappings,
  );
  const social_data = evaluateSocialData(fhirBundle, fhirPathMappings);
  const encounterData = evaluateEncounterData(fhirBundle, fhirPathMappings);
  const providerData = evaluateProviderData(fhirBundle, fhirPathMappings);
  const clinicalData = evaluateClinicalData(fhirBundle, fhirPathMappings);
  const labInfoData = evaluateLabInfoData(fhirBundle, fhirPathMappings);
  const accordionItems: any[] = [
    {
      title: "Patient Info",
      content: (
        <>
          <Demographics demographicsData={demographicsData.availableData} />
          {social_data.availableData.length > 0 && (
            <SocialHistory socialData={social_data.availableData} />
          )}
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Clinical Info",
      content: (
        <>
          <ClinicalInfo
            clinicalNotes={clinicalData.clinicalNotes.availableData}
            reasonForVisitDetails={
              clinicalData.reasonForVisitDetails.availableData
            }
            activeProblemsDetails={
              clinicalData.activeProblemsDetails.availableData
            }
            vitalData={clinicalData.vitalData.availableData}
            immunizationsDetails={
              clinicalData.immunizationsDetails.availableData
            }
            treatmentData={clinicalData.treatmentData.availableData}
          />
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Lab Info",
      content: (
        <LabInfo
          labInfo={labInfoData.labInfo.availableData}
          labResults={labInfoData.labResults}
        />
      ),
      expanded: true,
      headingLevel: "h3",
    },
  ];

  //Add id, adjust title
  accordionItems.forEach((item, index) => {
    let formattedTitle = formatString(item["title"]);
    item["id"] = `${formattedTitle}_${index + 1}`;
    item["title"] = <span id={formattedTitle}>{item["title"]}</span>;
    accordionItems[index] = item;
  });

  return (
    <Accordion
      className="info-container"
      items={accordionItems}
      multiselectable={true}
    />
  );
};
export default AccordianContainer;
