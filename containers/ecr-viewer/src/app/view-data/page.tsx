"use client";
import EcrSummary from "@/app/view-data/components/EcrSummary";
import AccordionContainer from "@/app/view-data/components/AccordionContainer";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Bundle } from "fhir/r4";
import { PathMappings } from "../utils";

const ECRViewerPage = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle>();
  const [mappings, setMappings] = useState<PathMappings>({});
  const [errors, setErrors] = useState<Error | unknown>(null);
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";

  type ApiResponse = {
    fhirBundle: Bundle;
    fhirPathMappings: PathMappings;
  };

  useEffect(() => {
    // Fetch the appropriate bundle from Postgres database
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/fhir-data?id=${fhirId}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || "Internal Server Error");
        } else {
          const bundle: ApiResponse = await response.json();
          setFhirBundle(bundle.fhirBundle);
          setMappings(bundle.fhirPathMappings);
        }
      } catch (error) {
        setErrors(error);
        console.error("Error fetching data:", error);
      }
    };
    fetchData();
  }, []);

  if (errors) {
    return <div>{`${errors}`}</div>;
  } else if (fhirBundle && mappings) {
    return (
      <div>
        <header>
          <h1 className={"page-title"}>EZ eCR Viewer</h1>
        </header>
        <div className={"ecr-viewer-container"}>
          <h2 className="margin-bottom-3">eCR Summary</h2>
          <EcrSummary fhirPathMappings={mappings} fhirBundle={fhirBundle} />
          <div className="margin-top-6">
            <h2 className="margin-bottom-3">eCR Document</h2>
            <AccordionContainer
              fhirPathMappings={mappings}
              fhirBundle={fhirBundle}
            />
          </div>
        </div>
      </div>
    );
  } else {
    return (
      <div>
        <h1>Loading...</h1>
      </div>
    );
  }
};

export default ECRViewerPage;
