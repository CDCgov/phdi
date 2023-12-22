// pages/index.js
"use client"
import EcrSummary from "@/app/view-data/components/EcrSummary";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from 'react';
import { Bundle } from "fhir/r4";
import Demographics from "./components/Demographics";
import SocialHistory from "./components/SocialHistory";
import { Accordion } from '@trussworks/react-uswds'
import UnavailableInfo from "./components/UnavailableInfo";
import {PathMappings, evaluateSocialData} from "../utils";


const ECRViewerPage = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle>();
  const [mappings, setMappings] = useState<PathMappings>({});
  const [errors, setErrors] = useState<Error | unknown>(null);
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";

  type FhirMappings = { [key: string]: string };

  type ApiResponse = {
    fhirBundle: Bundle,
    fhirPathMappings: FhirMappings
  }

  useEffect(() => {
    // Fetch the appropriate bundle from Postgres database
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/data?id=${fhirId}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error( errorData.message || 'Internal Server Error');
        } else{
          const bundle: ApiResponse = (await response.json());
          setFhirBundle(bundle.fhirBundle)
          setMappings(bundle.fhirPathMappings)
        }
      } catch (error) {
        setErrors(error)
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, []);

  const renderAccordion = () => {
    const social_data = evaluateSocialData(fhirBundle, mappings)
    const accordionItems: any[] = [
      {
        title: 'Patient Info',
        content: (
          <div>
            <Demographics fhirPathMappings={mappings} fhirBundle={fhirBundle} />
            {social_data.available_data && <SocialHistory socialData={social_data.available_data} />}
          </div>
        ),
        expanded: true,
        id: '1',
        headingLevel: 'h2',
      },
      {
        title: 'Unavailable Info',
        content: (
          <div>
            <UnavailableInfo unavailableData={social_data.unavailable_data} />
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
          <h2>eCR Summary</h2>
          <EcrSummary fhirPathMappings={mappings} fhirBundle={fhirBundle} />
          <h2>Additional Details</h2>
          {renderAccordion()}
        </div>
      </div>)
  } else {
    return <div>
      <h1>Loading...</h1>
    </div>
  }
};

export default ECRViewerPage;
