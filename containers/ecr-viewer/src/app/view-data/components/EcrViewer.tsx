"use client";
import { Bundle, FhirResource } from "fhir/r4";
import { PathMappings } from "@/app/utils";
import SideNav from "@/app/view-data/components/SideNav";
import EcrSummary from "@/app/view-data/components/EcrSummary";
import {
  evaluateEcrSummaryAboutTheConditionDetails,
  evaluateEcrSummaryEncounterDetails,
  evaluateEcrSummaryPatientDetails,
} from "@/app/services/ecrSummaryService";
import { Grid, GridContainer } from "@trussworks/react-uswds";
import { ExpandCollapseButtons } from "@/app/view-data/components/ExpandCollapseButtons";
import AccordionContainer from "@/app/view-data/components/AccordionContainer";
import React from "react";

interface EcrViewerProps {
  fhirBundle: Bundle<FhirResource>;
  mappings: PathMappings;
}

/**
 * Renders an eCR Viewer component.
 * @param props - The props object.
 * @param props.fhirBundle - The FHIR bundle containing data.
 * @param props.mappings - The mappings object for FHIR paths.
 * @returns - Returns the JSX element for the eCR Viewer.
 */
export default function EcrViewer({ fhirBundle, mappings }: EcrViewerProps) {
  return (
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
                    <Grid className={"flex-align-self-center margin-left-auto"}>
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
  );
}
