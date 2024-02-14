import {
  evaluateSocialData,
  evaluateEncounterData,
  evaluateProviderData,
  evaluateClinicalData,
  evaluateDemographicsData,
  evaluateEcrMetadata,
  PathMappings,
  formatString,
} from "../../utils";
import Demographics from "./Demographics";
import SocialHistory from "./SocialHistory";
import UnavailableInfo from "./UnavailableInfo";
import EcrMetadata from "./EcrMetadata";
import EncounterDetails, { encounterConfig } from "./Encounter";
import ClinicalInfo from "./ClinicalInfo";
import { Bundle, FhirResource } from "fhir/r4";
import React, { ReactNode } from "react";
import { Accordion } from "@trussworks/react-uswds";
import { format } from "path";

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
  const ecrMetadata = evaluateEcrMetadata(fhirBundle, fhirPathMappings);
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
      headingLevel: "h2",
    },
    {
      title: "Encounter Info",
      content: (
        <div>
          <EncounterDetails
            encounterData={encounterData.availableData}
            providerData={providerData.availableData}
          />
        </div>
      ),
      expanded: true,
      headingLevel: "h2",
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
      headingLevel: "h2",
    },
    {
      title: "eCR Metadata",
      content: (
        <>
          <EcrMetadata
            eicrDetails={ecrMetadata.eicrDetails.availableData}
            eCRSenderDetails={ecrMetadata.ecrSenderDetails.availableData}
            rrDetails={ecrMetadata.rrDetails.availableData}
          />
        </>
      ),
      expanded: true,
      headingLevel: "h2",
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
          />
        </div>
      ),
      expanded: true,
      headingLevel: "h2",
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
