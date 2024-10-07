"use client";
import AccordionContent from "@/app/view-data/components/AccordionContent";
import { useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { Bundle } from "fhir/r4";
import { PathMappings } from "./utils/utils";
import SideNav from "./components/SideNav";
import { Grid, GridContainer } from "@trussworks/react-uswds";
import { ExpandCollapseButtons } from "@/app/view-data/components/ExpandCollapseButtons";
import EcrSummary from "./components/EcrSummary";
import {
  evaluateEcrSummaryPatientDetails,
  evaluateEcrSummaryEncounterDetails,
  evaluateEcrSummaryConditionSummary,
} from "../services/ecrSummaryService";
import { metrics } from "./component-utils";
import { EcrLoadingSkeleton } from "./components/LoadingComponent";
import Header from "../Header";
import PatientBanner from "./components/PatientBanner";

/**
 * Functional component for rendering the eCR Viewer page.
 * @returns The main eCR Viewer JSX component.
 */
const ECRViewerPage: React.FC = () => {
  const [fhirBundle, setFhirBundle] = useState<Bundle>();
  const [mappings, setMappings] = useState<PathMappings>({});
  const [errors, setErrors] = useState<Error>();
  const searchParams = useSearchParams();
  const fhirId = searchParams ? (searchParams.get("id") ?? "") : "";
  const snomedCode = searchParams
    ? (searchParams.get("snomed-code") ?? "")
    : "";
  const isNonIntegratedViewer =
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER === "true";

  type ApiResponse = {
    fhirBundle: Bundle;
    fhirPathMappings: PathMappings;
  };

  useEffect(() => {
    const startTime = performance.now();
    window.addEventListener("beforeunload", function (_e) {
      metrics("", {
        startTime: startTime,
        endTime: performance.now(),
        fhirId: `${fhirId}`,
      });
    });
    const fetchData = async () => {
      try {
        const response = await fetch(`api/fhir-data?id=${fhirId}`);
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
          setFhirBundle(bundle.fhirBundle);
          setMappings(bundle.fhirPathMappings);
        }
      } catch (error: any) {
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
      <main className={"width-full minw-main"}>
        <Header />
        {isNonIntegratedViewer ? (
          <PatientBanner bundle={fhirBundle} mappings={mappings} />
        ) : (
          ""
        )}
        <div className="main-container">
          <div className={"width-main padding-main"}>
            <div className="content-wrapper">
              <SideNav />
              <div className={"ecr-viewer-container"}>
                <div className="margin-bottom-3">
                  <h2
                    className="margin-bottom-05 margin-top-3"
                    id="ecr-summary"
                  >
                    eCR Summary
                  </h2>
                  <div className="text-base-darker line-height-sans-5">
                    Provides key info upfront to help you understand the eCR at
                    a glance
                  </div>
                </div>
                <EcrSummary
                  patientDetails={
                    evaluateEcrSummaryPatientDetails(fhirBundle, mappings)
                      .availableData
                  }
                  encounterDetails={
                    evaluateEcrSummaryEncounterDetails(fhirBundle, mappings)
                      .availableData
                  }
                  conditionSummary={evaluateEcrSummaryConditionSummary(
                    fhirBundle,
                    mappings,
                    snomedCode,
                  )}
                  snomed={snomedCode}
                />
                <div className="margin-top-10">
                  <GridContainer
                    className={"padding-0 margin-bottom-3 maxw-none"}
                  >
                    <Grid row className="margin-bottom-05">
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
                    <div className="text-base-darker line-height-sans-5">
                      Displays entire eICR and RR documents to help you dig
                      further into eCR data
                    </div>
                  </GridContainer>
                  <AccordionContent
                    fhirPathMappings={mappings}
                    fhirBundle={fhirBundle}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        <a
          className="usa-button position-fixed right-3 bottom-0"
          target="_blank"
          title="External link opens in new window"
          href="https://touchpoints.app.cloud.gov/touchpoints/e93de6ae/submit"
        >
          How can we improve eCR Viewer?
        </a>
      </main>
    );
  } else {
    return (
      <div>
        <EcrLoadingSkeleton />
      </div>
    );
  }
};

export default ECRViewerPage;
