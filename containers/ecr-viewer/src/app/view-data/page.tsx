"use client";
import AccordionContainer from "@/app/view-data/components/AccordionContainer";
import { useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { Bundle } from "fhir/r4";
import { PathMappings } from "../utils";
import SideNav from "./components/SideNav";
import { processSnomedCode } from "./service";
import { Grid, GridContainer } from "@trussworks/react-uswds";
import { ExpandCollapseButtons } from "@/app/view-data/components/ExpandCollapseButtons";
import EcrSummary from "./components/EcrSummary";
import {
  evaluateEcrSummaryPatientDetails,
  evaluateEcrSummaryEncounterDetails,
  evaluateEcrSummaryAboutTheConditionDetails,
} from "../services/ecrSummaryService";
import { metrics } from "@opentelemetry/api";

// string constants to match with possible .env values
const basePath = process.env.NODE_ENV === "production" ? "/ecr-viewer" : "";

/**
 * Functional component for rendering the eCR Viewer page.
 * @returns The main eCR Viewer JSX component.
 */
const ECRViewerPage: React.FC = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle>();
  const [mappings, setMappings] = useState<PathMappings>({});
  const [errors, setErrors] = useState<Error>();
  const searchParams = useSearchParams();
  const fhirId = searchParams.get("id") ?? "";
  const snomedCode = searchParams.get("snomed-code") ?? "";

  type ApiResponse = {
    fhirBundle: Bundle;
    fhirPathMappings: PathMappings;
  };
  const meterProvider = metrics.getMeterProvider();
  const metric = meterProvider.getMeter("view-data");
  const visitors = metric.createCounter("visitors");
  visitors.add(1, { fhirId });
  const dummyHistogram = metric.createHistogram("histogram");
  dummyHistogram.record(Math.random() * 100);
  dummyHistogram.record(Math.random() * 100);

  useEffect(() => {
    // Fetch the appropriate bundle from Postgres database

    const fetchData = async () => {
      try {
        const response = await fetch(`${basePath}/api/fhir-data?id=${fhirId}`);
        if (!response.ok) {
          if (response.status == 404) {
            throw new Error(
              "Sorry, we couldn't find this eCR ID. Please try again with a different ID.",
            );
          } else {
            const errorData = response.statusText;
            throw new Error(errorData || "Internal Server Error");
          }
        } else {
          const bundle: ApiResponse = await response.json();
          processSnomedCode(snomedCode);
          setFhirBundle(bundle.fhirBundle);
          setMappings(bundle.fhirPathMappings);
        }
      } catch (error: any) {
        setErrors(error);
        console.error("Error fetching data:", error);
      }
    };
    fetchData();

    // this does not work :(
    const startViewTime = performance.now();
    const timeSpentHistogram = metric.createHistogram("timeSpent");
    const handleBeforeUnload = () => {
      timeSpentHistogram.record(performance.now() - startViewTime || 0, {
        fhirId,
      });
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
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
      <main>
        <div>
          <div className="main-container">
            <div className="content-wrapper">
              <div className="nav-wrapper">
                <nav className="sticky-nav">
                  <SideNav />
                </nav>
              </div>
              <div className={"ecr-viewer-container"}>
                <div className="ecr-content">
                  <h1 className="margin-bottom-3" id="ecr-summary">
                    eCR Summary
                  </h1>
                  <EcrSummary
                    patientDetails={evaluateEcrSummaryPatientDetails(
                      fhirBundle,
                      mappings,
                    )}
                    encounterDetails={evaluateEcrSummaryEncounterDetails(
                      fhirBundle,
                      mappings,
                    )}
                    aboutTheCondition={evaluateEcrSummaryAboutTheConditionDetails(
                      fhirBundle,
                      mappings,
                    )}
                  />
                  <div className="margin-top-10">
                    <GridContainer className={"padding-0 margin-bottom-3"}>
                      <Grid row>
                        <Grid>
                          <h2 className="margin-bottom-0" id="ecr-document">
                            eCR Document
                          </h2>
                        </Grid>
                        <Grid
                          className={"flex-align-self-center margin-left-auto"}
                        >
                          <ExpandCollapseButtons
                            id={"main"}
                            buttonSelector={"h3 > .usa-accordion__button"}
                            accordionSelector={
                              ".info-container > .usa-accordion__content"
                            }
                            expandButtonText={"Expand all sections"}
                            collapseButtonText={"Collapse all sections"}
                          />
                        </Grid>
                      </Grid>
                    </GridContainer>
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
      </main>
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
