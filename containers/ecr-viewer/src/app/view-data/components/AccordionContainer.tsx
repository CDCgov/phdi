import {
  evaluateSocialData,
  evaluateEncounterData,
  evaluateProviderData,
  evaluateDemographicsData,
  PathMappings,
} from "../../utils";
import Demographics from "../components/Demographics";
import SocialHistory from "../components/SocialHistory";
import UnavailableInfo from "../components/UnavailableInfo";
import EcrMetadata from "../components/EcrMetadata";
import EncounterDetails from "../components/Encounter";
import { Bundle, FhirResource } from "fhir/r4";
import { ReactNode } from "react";
import { Accordion } from "@trussworks/react-uswds";

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
      id: "1",
      headingLevel: "h2",
    },
    {
      title: "eCR Metadata",
      content: (
        <>
          <EcrMetadata
            fhirPathMappings={fhirPathMappings}
            fhirBundle={fhirBundle}
          />
        </>
      ),
      expanded: true,
      id: "2",
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
      id: "3",
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
            providerUnavailableData={providerData.unavailableData}
          />
        </div>
      ),
      expanded: true,
      id: "4",
      headingLevel: "h2",
    },
  ];

  return (
    <Accordion
      className="info-container"
      items={accordionItems}
      multiselectable={true}
    />
  );
};
export default AccordianContainer;
