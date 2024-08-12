import { PathMappings } from "../../utils";
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
  const labInfoData = evaluateLabInfoData(
    fhirBundle,
    evaluate(fhirBundle, fhirPathMappings["diagnosticReports"]),
    fhirPathMappings,
  );
  // TODO ANGELA: DELETE
  // demographicsData.availableData = [];
  // encounterData.availableData = [];
  // providerData.availableData = [];

  // const emptyClinicalData = {
  //   clinicalNotes: { availableData: [] },
  //   reasonForVisitDetails: { availableData: [] },
  //   activeProblemsDetails: { availableData: [] },
  //   vitalData: { availableData: [] },
  //   immunizationsDetails: { availableData: [] },
  //   treatmentData: { availableData: [] },
  // };

  // const ecrMetadata = {
  //   rrDetails: {},
  //   eicrDetails: {
  //     availableData: [],
  //     unavailableData: [] // Ensure this is an empty array
  //   },
  //   ecrSenderDetails: {
  //     availableData: [],
  //     unavailableData: [] // Ensure this is an empty array
  //   },
  // }

  // const testFixtureNoData = {
  //   demographicsData: {
  //     unavailableData: []
  //   },
  //   social_data: {
  //     unavailableData: []
  //   },
  //   encounterData: {
  //     unavailableData: []
  //   },
  //   clinicalData: {
  //     reasonForVisitDetails: { unavailableData: [] },
  //     activeProblemsDetails: { unavailableData: [] },
  //     vitalData: { unavailableData: [] },
  //     immunizationsDetails: { unavailableData: [] },
  //     treatmentData: { unavailableData: [] },
  //     clinicalNotes: { unavailableData: [] }
  //   },
  //   providerData: {
  //     unavailableData: []
  //   },
  //   ecrMetadata: {
  //     eicrDetails: { unavailableData: [] },
  //     ecrSenderDetails: { unavailableData: [] }
  //   }
  // };

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
            <p>No patient information was found in this eCR.</p>
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
          providerData.availableData.length > 0 ? (
            <EncounterDetails
              encounterData={encounterData.availableData}
              providerData={providerData.availableData}
            />
          ) : (
            <p>No encounter information was found in this eCR.</p>
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
        <p>No clinical information was found in this eCR.</p>
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
          <p>No lab information was found in this eCR.</p>
        ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "eCR Metadata",
      content: (
        <>
          {Object.keys(ecrMetadata.rrDetails).length > 0 ||
          ecrMetadata.eicrDetails.availableData.length > 0 ||
          ecrMetadata.ecrSenderDetails.availableData.length > 0 ? (
            <EcrMetadata
              eicrDetails={ecrMetadata.eicrDetails.availableData}
              eCRSenderDetails={ecrMetadata.ecrSenderDetails.availableData}
              rrDetails={ecrMetadata.rrDetails}
            />
          ) : (
            <p>No clinical information was found in this eCR.</p>
          )}
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    {
      title: "Unavailable Info",
      content: (
        <div className="padding-top-105">
          {[
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
            ...ecrMetadata.ecrSenderDetails.unavailableData,
          ].some((array) => Array.isArray(array) && array.length > 0) ? (
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
          ) : (
            <p>All possible information was found in this eCR.</p>
          )}
        </div>
      ),
      expanded: true,
      headingLevel: "h3",
    },
    // { // TODO ANGELA: DELETE LATER
    // title: "Unavailable Info",
    // content: (
    //   <div className="padding-top-105">
    //     {[
    //       testFixtureNoData.demographicsData.unavailableData,
    //       testFixtureNoData.social_data.unavailableData,
    //       testFixtureNoData.encounterData.unavailableData,
    //       testFixtureNoData.clinicalData.reasonForVisitDetails.unavailableData,
    //       testFixtureNoData.clinicalData.activeProblemsDetails.unavailableData,
    //       testFixtureNoData.providerData.unavailableData,
    //       testFixtureNoData.clinicalData.vitalData.unavailableData,
    //       testFixtureNoData.clinicalData.immunizationsDetails.unavailableData,
    //       testFixtureNoData.clinicalData.treatmentData.unavailableData,
    //       testFixtureNoData.clinicalData.clinicalNotes.unavailableData,
    //       ...testFixtureNoData.ecrMetadata.eicrDetails.unavailableData,
    //       ...testFixtureNoData.ecrMetadata.ecrSenderDetails.unavailableData,
    //     ].some(array => Array.isArray(array) && array.length > 0) ? (
    //       <UnavailableInfo
    //         demographicsUnavailableData={testFixtureNoData.demographicsData.unavailableData}
    //         socialUnavailableData={testFixtureNoData.social_data.unavailableData}
    //         encounterUnavailableData={testFixtureNoData.encounterData.unavailableData}
    //         reasonForVisitUnavailableData={
    //           testFixtureNoData.clinicalData.reasonForVisitDetails.unavailableData
    //         }
    //         activeProblemsUnavailableData={
    //           testFixtureNoData.clinicalData.activeProblemsDetails.unavailableData
    //         }
    //         providerUnavailableData={testFixtureNoData.providerData.unavailableData}
    //         vitalUnavailableData={testFixtureNoData.clinicalData.vitalData.unavailableData}
    //         immunizationsUnavailableData={
    //           testFixtureNoData.clinicalData.immunizationsDetails.unavailableData
    //         }
    //         treatmentData={testFixtureNoData.clinicalData.treatmentData.unavailableData}
    //         clinicalNotesData={testFixtureNoData.clinicalData.clinicalNotes.unavailableData}
    //         ecrMetadataUnavailableData={[
    //           ...testFixtureNoData.ecrMetadata.eicrDetails.unavailableData,
    //           ...testFixtureNoData.ecrMetadata.ecrSenderDetails.unavailableData,
    //         ]}
    //       />
    //     ) : (
    //       <p>All possible information was found in this eCR.</p>
    //     )}
    //   </div>
    // ),
    // expanded: true,
    // headingLevel: "h3",
    // }
  ];

  return <AccordionContainer accordionItems={accordionItems} />;
};
export default AccordionContent;
