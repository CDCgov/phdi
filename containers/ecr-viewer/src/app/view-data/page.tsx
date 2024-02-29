"use client";
import EcrSummary from "@/app/view-data/components/EcrSummary";
import AccordionContainer from "@/app/view-data/components/AccordionContainer";
import { useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { Bundle } from "fhir/r4";
import { PathMappings } from "../utils";
import SideNav from "./components/SideNav";
import { processSnomedCode } from "./service";

// string constants to match with possible .env values
const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";

const assignApiPath = () => {
  if (process.env.NEXT_PUBLIC_SOURCE === S3_SOURCE) {
    return "s3";
  } else if (process.env.NEXT_PUBLIC_SOURCE === POSTGRES_SOURCE) {
    return "fhir-data";
  }
};

const ECRViewerPage = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle>();
  const [mappings, setMappings] = useState<PathMappings>({});
  const [errors, setErrors] = useState<Error | unknown>(null);
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";
  const apiPath = assignApiPath();
  const snomedCode = searchParams.get("snomed-code") ?? "";

  type ApiResponse = {
    fhirBundle: Bundle;
    fhirPathMappings: PathMappings;
  };

  useEffect(() => {
    // Fetch the appropriate bundle from Postgres database
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/${apiPath}?id=${fhirId}`);
        if (!response.ok) {
          const errorData = response.statusText;
          throw new Error(errorData || "Internal Server Error");
        } else {
          const bundle: ApiResponse = await response.json();
          processSnomedCode(snomedCode);
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
    return (
      <div>
        <pre>
          <code>{`${errors}`}</code>
        </pre>
      </div>
    );
  } else if (fhirBundle && mappings) {
    return (
      <div>
        <header>
          <h1 className="page-title">EZ eCR Viewer</h1>
        </header>
        <div className="main-container">
          <div className="content-wrapper">
            <div className="nav-wrapper">
              <nav className="sticky-nav">
                <SideNav />
              </nav>
            </div>
            <div className={"ecr-viewer-container"}>
              <div className="ecr-content">
                <h2 className="margin-bottom-3" id="ecr-summary">
                  eCR Summary
                </h2>
                <EcrSummary
                  fhirPathMappings={mappings}
                  fhirBundle={fhirBundle}
                />
                <div className="margin-top-6">
                  <h2 className="margin-bottom-3" id="ecr-document">
                    eCR Document
                  </h2>
                  <AccordionContainer
                    fhirPathMappings={mappings}
                    fhirBundle={fhirBundle}
                  />
                </div>
              </div>
            </div>
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
