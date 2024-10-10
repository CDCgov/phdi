import { PathMappings } from "../utils/utils";
import Demographics from "./Demographics";
import SocialHistory from "./SocialHistory";
import UnavailableInfo from "./UnavailableInfo";
import EcrMetadata from "./EcrMetadata";
import EncounterDetails from "./Encounter";
import ClinicalInfo from "./ClinicalInfo";
import { Bundle } from "fhir/r4";
import React, { ReactNode } from "react";
import LabInfo from "@/app/view-data/components/LabInfo";
import { evaluateEcrMetadata } from "../../services/ecrMetadataService";
import { evaluateLabInfoData } from "@/app/services/labsService";
import {
  evaluateDemographicsData,
  evaluateSocialData,
  evaluateEncounterData,
  evaluateProviderData,
  evaluateFacilityData,
} from "@/app/services/evaluateFhirDataService";
import { evaluateClinicalData } from "./common";
import AccordionContainer from "@repo/ui/accordionContainer";
import { evaluate } from "@/app/view-data/utils/evaluate";

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
const AccordionContent: React.FC<AccordionContainerProps> = ({
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
  const facilityData = evaluateFacilityData(fhirBundle, fhirPathMappings);
  const labInfoData = evaluateLabInfoData(
    fhirBundle,
    evaluate(fhirBundle, fhirPathMappings["diagnosticReports"]),
    fhirPathMappings,
  );
  const hasUnavailableData = () => {
    const unavailableDataArrays = [
      demographicsData.unavailableData,
      social_data.unavailableData,
      encounterData.unavailableData,
      clinicalData.reasonForVisitDetails.unavailableData,
      clinicalData.activeProblemsDetails.unavailableData,
      providerData.unavailableData,
      clinicalData.vitalData.unavailableData,
      clinicalData.immunizationsDetails.unavailableData,
      clinicalData.treatmentData.unavailableData,
      clinicalData.clinicalNotes.unavailableData,
      ...ecrMetadata.eicrDetails.unavailableData,
      ...ecrMetadata.ecrCustodianDetails.unavailableData,
      ecrMetadata.eRSDWarnings,
      ecrMetadata.eicrAuthorDetails.map((details) => details.unavailableData),
    ];
    return unavailableDataArrays.some(
      (array) => Array.isArray(array) && array.length > 0,
    );
  };

  const accordionItems: any[] = [
    {
      title: "Patient Info",
      content: (
        <>
          {demographicsData.availableData.length > 0 ||
          social_data.availableData.length > 0 ? (
            <>
              <Demographics demographicsData={demographicsData.availableData} />
              {social_data.availableData.length > 0 && (
                <SocialHistory socialData={social_data.availableData} />
              )}
            </>
          ) : (
            <p className="text-italic padding-bottom-05">
              No patient information was found in this eCR.
            </p>
          )}
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Encounter Info",
      content: (
        <>
          {encounterData.availableData.length > 0 ||
          facilityData.availableData.length > 0 ||
          providerData.availableData.length > 0 ? (
            <EncounterDetails
              encounterData={encounterData.availableData}
              facilityData={facilityData.availableData}
              providerData={providerData.availableData}
            />
          ) : (
            <p className="text-italic padding-bottom-05">
              No encounter information was found in this eCR.
            </p>
          )}
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Clinical Info",
      content: Object.values(clinicalData).some(
        (section) => section.availableData.length > 0,
      ) ? (
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
      ) : (
        <p className="text-italic padding-bottom-05">
          No clinical information was found in this eCR.
        </p>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Lab Info",
      content:
        labInfoData.length > 0 ? (
          <LabInfo labResults={labInfoData} />
        ) : (
          <p className="text-italic padding-bottom-05">
            No lab information was found in this eCR.
          </p>
        ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "eCR Metadata",
      content: (
        <>
          {Object.keys(ecrMetadata.rrDetails).length > 0 ||
          ecrMetadata.eRSDWarnings.length > 0 ||
          ecrMetadata.eicrDetails.availableData.length > 0 ||
          ecrMetadata.eicrAuthorDetails.find(
            (authorDetails) => authorDetails.availableData.length > 0,
          ) ||
          ecrMetadata.ecrCustodianDetails.availableData.length > 0 ? (
            <EcrMetadata
              eicrDetails={ecrMetadata.eicrDetails.availableData}
              eCRCustodianDetails={
                ecrMetadata.ecrCustodianDetails.availableData
              }
              rrDetails={ecrMetadata.rrDetails}
              eRSDWarnings={ecrMetadata.eRSDWarnings}
              eicrAuthorDetails={ecrMetadata.eicrAuthorDetails.map(
                (details) => details.availableData,
              )}
            />
          ) : (
            <p className="text-italic padding-bottom-05">
              No eCR metadata was found in this eCR.
            </p>
          )}
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Unavailable Info",
      content: (
        <div>
          {hasUnavailableData() ? (
            <UnavailableInfo
              demographicsUnavailableData={demographicsData.unavailableData}
              socialUnavailableData={social_data.unavailableData}
              encounterUnavailableData={encounterData.unavailableData}
              facilityUnavailableData={facilityData.unavailableData}
              symptomsProblemsUnavailableData={[
                ...clinicalData.reasonForVisitDetails.unavailableData,
                ...clinicalData.activeProblemsDetails.unavailableData,
              ]}
              providerUnavailableData={providerData.unavailableData}
              vitalUnavailableData={clinicalData.vitalData.unavailableData}
              immunizationsUnavailableData={
                clinicalData.immunizationsDetails.unavailableData
              }
              treatmentData={clinicalData.treatmentData.unavailableData}
              clinicalNotesData={clinicalData.clinicalNotes.unavailableData}
              ecrMetadataUnavailableData={[
                ...ecrMetadata.eicrDetails.unavailableData,
                ...(ecrMetadata.eRSDWarnings.length === 0
                  ? [{ title: "eRSD Warnings", value: "" }]
                  : []),
                ...ecrMetadata.ecrCustodianDetails.unavailableData,
              ]}
              eicrAuthorDetails={ecrMetadata.eicrAuthorDetails.map(
                (authorDetails) => authorDetails.unavailableData,
              )}
            />
          ) : (
            <p className="text-italic padding-bottom-105 margin-0">
              All possible information was found in this eCR.
            </p>
          )}
        </div>
      ),
      expanded: true,
      headingLevel: "h3",
    },
  ];

  return <AccordionContainer accordionItems={accordionItems} />;
};
export default AccordionContent;
