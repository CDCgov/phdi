// pages/index.js
"use client"
import EcrSummary from "@/app/view-data/EcrSummary";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from 'react';
import {Bundle} from "fhir/r4";
import {fhirPathMappings} from "../../../utils/fhirMappings";


const ECRViewerPage = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle | null>(null);
  const [mappings, setMappings] = useState(null);
  const [errors, setErrors] = useState<Error | unknown>(null)
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";

  useEffect(() => {
    // Fetch the appropriate bundle from Postgres database
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/data?id=${fhirId}`);
        if(!response.ok ){
          const errorData = await response.json();
          throw new Error( errorData.message || 'Internal Server Error');
        } else{
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
    fhirPathMappings.then(val => {setMappings(val)})
  }, []);
    if(errors){
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
              <EcrSummary fhirPathMappings={mappings} fhirBundle={fhirBundle}/>
            </div>
          </div>)
    } else {
      return <div>
      <h1>Loading...</h1>
      </div>
    }

};

export default ECRViewerPage;