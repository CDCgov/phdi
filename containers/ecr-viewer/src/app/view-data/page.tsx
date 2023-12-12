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
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";

  useEffect(() => {
    // Fetch the appropriate bundle from Postgres database
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/data?id=${fhirId}`);
        const databaseBundle: Bundle = await response.json();
        setFhirBundle(databaseBundle)
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
    
    //Load fhirPath mapping data
    fhirPathMappings.then(val => {setMappings(val)})
  }, []);

    if (fhirBundle && mappings) {
      return <div>
        <EcrSummary fhirPathMappings={mappings} fhirBundle={fhirBundle}/>
      </div>
    } else {
      return <div>
        <h1>This FHIR bundle could not be found.</h1>
      </div>
    }

};

export default ECRViewerPage;