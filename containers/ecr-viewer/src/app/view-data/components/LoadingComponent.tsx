"use client";
import { Accordion, Grid, GridContainer } from "@trussworks/react-uswds";
import { ExpandCollapseButtons } from "./ExpandCollapseButtons";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";

/**
 * Temp
 * @returns The main eCR Viewer JSX component.
 */
export const EcrLoading = () => {
  const renderEcrDocumentFiller = (title: string, numberOfRows: number) => {
    return (
      <AccordianSection>
        <AccordianH4>
          <span id={title}>{title}</span>
        </AccordianH4>
        <AccordianDiv>{renderLoadingBlobs(numberOfRows)}</AccordianDiv>
      </AccordianSection>
    );
  };
  const renderLoadingBlobs = (numberOfRows: number, isGray: boolean = true) => {
    // Create an array of specified size to map over
    const rows = Array.from({ length: numberOfRows });
    const loadingBlobStyle = isGray ? "loading-blob-gray" : "loading-blob-blue";
    const sectionLineStyle = isGray ? "section__line_gray" : "section__line";
    // Map over the array to create multiple divs
    return (
      <>
        {rows.map((_, index) => (
          <div key={index}>
            <div className="grid-row">
              <div className="grid-col-4">
                <div className={`${loadingBlobStyle} margin-right-1`}>
                  &nbsp;
                </div>
              </div>
              <div className={`grid-col-8 ${loadingBlobStyle}`}>&nbsp;</div>
            </div>
            <div className={sectionLineStyle} />
          </div>
        ))}
      </>
    );
  };
  const accordionItems: any[] = [
    {
      title: "Patient Info",
      expanded: true,
      content: (
        <>
          {renderEcrDocumentFiller("Demographics", 10)}
          {renderEcrDocumentFiller("Social History", 3)}
        </>
      ),
      headingLevel: "h3",
    },
    {
      title: "Encounter Info",
      expanded: true,
      content: (
        <>
          {renderEcrDocumentFiller("Encounter Details", 7)}
          {renderEcrDocumentFiller("Provider Details", 2)}
        </>
      ),
      headingLevel: "h3",
    },
    {
      title: "Clinical Info",
      expanded: true,
      content: (
        <>
          {renderEcrDocumentFiller("Symptoms and Problems", 3)}
          {renderEcrDocumentFiller("Treatment Details", 4)}
          {renderEcrDocumentFiller("Immunizations", 1)}
          {renderEcrDocumentFiller("Diagnostic and Vital Signs", 2)}
        </>
      ),
      headingLevel: "h3",
    },
    {
      title: "Lab Info",
      expanded: true,
      content: <>{renderEcrDocumentFiller("Lab Results from", 4)}</>,
      headingLevel: "h3",
    },
    {
      title: "eCR Metadata",
      expanded: true,
      content: (
        <>
          {renderEcrDocumentFiller("RR Details", 1)}
          {renderEcrDocumentFiller("eICR Details", 1)}
          {renderEcrDocumentFiller("eCR Sender Details", 6)}
        </>
      ),
      headingLevel: "h3",
    },
    {
      title: "Unavailable Info",
      expanded: true,
      headingLevel: "h3",
    },
  ];

  return (
    <div>
      <div className="main-container">
        <div className="content-wrapper">
          <div className={"ecr-viewer-container"}>
            <div className="ecr-content">
              <h2 className="margin-bottom-3" id="ecr-summary">
                eCR Summary
              </h2>
              <div className={"info-container"}>
                <div
                  className="usa-summary-box padding-3"
                  aria-labelledby="summary-box-key-information"
                >
                  <h3 className="summary-box-key-information side-nav-ignore">
                    About the Patient
                  </h3>
                  {renderLoadingBlobs(4, false)}
                  <h3 className="summary-box-key-information side-nav-ignore">
                    About the Encounter
                  </h3>
                  {renderLoadingBlobs(4, false)}
                  <h3 className="summary-box-key-information side-nav-ignore">
                    About the Condition
                  </h3>
                  {renderLoadingBlobs(4, false)}
                </div>
              </div>
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
                <Accordion
                  className="info-container"
                  items={accordionItems}
                  multiselectable={true}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
