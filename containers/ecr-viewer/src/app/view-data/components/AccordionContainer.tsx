import { PathMappings } from "../../utils";
import Demographics from "./Demographics";
import SocialHistory from "./SocialHistory";
import UnavailableInfo from "./UnavailableInfo";
import EcrMetadata from "./EcrMetadata";
import EncounterDetails from "./Encounter";
import ClinicalInfo from "./ClinicalInfo";
import { Bundle } from "fhir/r4";
import React, { ReactNode } from "react";
import { Accordion } from "@trussworks/react-uswds";
import LabInfo from "@/app/view-data/components/LabInfo";
import { formatString } from "@/app/services/formatService";
import { evaluateEcrMetadata } from "../../services/ecrMetadataService";
import { evaluateLabInfoData } from "@/app/services/labsService";
import {
  evaluateDemographicsData,
  evaluateSocialData,
  evaluateEncounterData,
  evaluateProviderData,
} from "@/app/services/evaluateFhirDataService";
import { evaluateClinicalData } from "./common";

type AccordionContainerProps = {
  children?: ReactNode;
  fhirBundle: Bundle;
  fhirPathMappings: PathMappings;
};

/**
 * Functional component for an accordion container displaying various sections of eCR information.
 * @param props - Props containing FHIR bundle and path mappings.
 * @param props.fhirBundle - The FHIR bundle containing patient information.
 * @param props.fhirPathMappings - The path mappings used to extract information from the FHIR bundle.
 * @returns The JSX element representing the accordion container.
 */
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
  const ecrMetadata = evaluateEcrMetadata(fhirBundle, fhirPathMappings);
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
      title: "Encounter Info",
      content: (
        <EncounterDetails
          encounterData={encounterData.availableData}
          providerData={providerData.availableData}
        />
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Clinical Info",
      content: (
        <ClinicalInfo
          clinicalNotes={clinicalData.clinicalNotes.availableData}
          reasonForVisitDetails={
            clinicalData.reasonForVisitDetails.availableData
          }
          activeProblemsDetails={
            clinicalData.activeProblemsDetails.availableData
          }
          vitalData={clinicalData.vitalData.availableData}
          immunizationsDetails={clinicalData.immunizationsDetails.availableData}
          treatmentData={clinicalData.treatmentData.availableData}
        />
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Lab Info",
      content: <LabInfo labResults={labInfoData} />,
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "eCR Metadata",
      content: (
        <EcrMetadata
          eicrDetails={ecrMetadata.eicrDetails.availableData}
          eCRSenderDetails={ecrMetadata.ecrSenderDetails.availableData}
          rrDetails={ecrMetadata.rrDetails}
        />
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Unavailable Info",
      content: (
        <div className="padding-top-105">
          <UnavailableInfo
            demographicsUnavailableData={demographicsData.unavailableData}
            socialUnavailableData={social_data.unavailableData}
            encounterUnavailableData={encounterData.unavailableData}
            reasonForVisitUnavailableData={
              clinicalData.reasonForVisitDetails.unavailableData
            }
            activeProblemsUnavailableData={
              clinicalData.activeProblemsDetails.unavailableData
            }
            providerUnavailableData={providerData.unavailableData}
            vitalUnavailableData={clinicalData.vitalData.unavailableData}
            immunizationsUnavailableData={
              clinicalData.immunizationsDetails.unavailableData
            }
            treatmentData={clinicalData.treatmentData.unavailableData}
            clinicalNotesData={clinicalData.clinicalNotes.unavailableData}
            ecrMetadataUnavailableData={[
              ...ecrMetadata.eicrDetails.unavailableData,
              ...ecrMetadata.ecrSenderDetails.unavailableData,
            ]}
          />
        </div>
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
