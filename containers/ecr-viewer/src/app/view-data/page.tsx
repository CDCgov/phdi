import { processSnomedCode } from "@/app/view-data/service";
import { loadYamlConfig } from "@/app/api/services/utils";
import { getEcrData } from "@/app/api/services/ecrDataService";
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

/**
 * Functional component for rendering a page based on provided search parameters.
 * @param props - Component props.
 * @param props.searchParams - Search parameters object.
 * @returns - functional component for view-data
 */
export default async function Page({
  searchParams,
}: Readonly<{ searchParams: { [key: string]: string | undefined } }>) {
  const fhirId = searchParams["id"] ?? "";
  const snomedCode = searchParams["snomed-code"] ?? "";
  processSnomedCode(snomedCode);
  const fhirBundle = await getEcrData(fhirId);
  const mappings = loadYamlConfig();
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
}
