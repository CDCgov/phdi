// pages/index.js
"use client"
import EcrSummary from "@/app/view-data/components/EcrSummary";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from 'react';
import { Bundle } from "fhir/r4";
import { fhirPathMappings } from "../../../utils/fhirMappings";
import Demographics from "./components/Demographics";
import SocialHistory from "./components/SocialHistory";
import { Accordion } from '@trussworks/react-uswds'
import UnavailableInfo from "./components/UnavailableInfo";
import { PathMappings, evaluateSocialData, evaluateEncounterData, evaluateProviderData } from "../utils";
import EncounterDetails from "./components/Encounter";


const ECRViewerPage = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle>();
  const [mappings, setMappings] = useState<PathMappings>({});
  const [errors, setErrors] = useState<Error | unknown>(null);
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";

  useEffect(() => {
    // Fetch the appropriate bundle from Postgres database
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/data?id=${fhirId}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Internal Server Error');
        } else {
          const databaseBundle: Bundle = (await response.json()).fhirBundle;
          setFhirBundle(databaseBundle)
        }
      } catch (error) {
        setErrors(error)
        console.error('Error fetching data:', error);
      }
    };
    fetchData();

    //Load fhirPath mapping data
    fhirPathMappings.then(val => { setMappings(val) })
  }, []);

  const renderAccordion = () => {
    const social_data = evaluateSocialData(fhirBundle, mappings)
    const encounterData = evaluateEncounterData(fhirBundle, mappings)
    const providerData = evaluateProviderData(fhirBundle, mappings)
    const accordionItems: any[] = [
      {
        title: 'Patient Info',
        content: (
          <div>
            <Demographics fhirPathMappings={mappings} fhirBundle={fhirBundle} />
            {social_data.available_data.length > 0 && <SocialHistory socialData={social_data.available_data} />}
          </div>
        ),
        expanded: true,
        id: '1',
        headingLevel: 'h2',
      },
      {
        title: 'Encounter Data',
        content: (
          <div>
            <EncounterDetails encounterData={encounterData.available_data} providerData={providerData.available_data} />
          </div>
        ),
        expanded: true,
        id: '2',
        headingLevel: 'h2',
      },
      {
        title: 'Unavailable Info',
        content: (
          <div className="padding-top-105">
            <UnavailableInfo
              socialUnavailableData={social_data.unavailable_data}
              encounterUnavailableData={encounterData.unavailable_data}
              providerUnavailableData={providerData.unavailable_data}
            />
          </div>
        ),
        expanded: true,
        id: '2',
        headingLevel: 'h2',
      },
    ]

    return (
      <Accordion className="info-container" items={accordionItems} multiselectable={true} />
    )
  }

  if (errors) {
    return (
      <div>
        {`${errors}`}
      </div>
    )
  }
  else if (fhirBundle && mappings) {

    return (
      <div>
        <header><h1 className={"page-title"}>EZ eCR Viewer</h1></header>
        <div className={"ecr-viewer-container"}>
          <h2 className="margin-bottom-3">eCR Summary</h2>
          <EcrSummary fhirPathMappings={mappings} fhirBundle={fhirBundle} />
          <div className="margin-top-6">
            <h2 className="margin-bottom-3">eCR Document</h2>
            {renderAccordion()}
          </div>
        </div>
      </div >)
  } else {
    return <div>
      <h1>Loading...</h1>
    </div>
  }
};

export default ECRViewerPage;
