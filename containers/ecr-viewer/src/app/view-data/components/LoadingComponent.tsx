"use client";
import { Accordion, Grid, GridContainer } from "@trussworks/react-uswds";
import { ExpandCollapseButtons } from "./ExpandCollapseButtons";
import SideNav from "./SideNav";
import {
  AccordionDiv,
  AccordionH4,
  AccordionSection,
} from "../component-utils";

/**
 * Renders the loading blobs in gray or in blue
 * @param numberOfRows - number of rows to render
 * @param isGray - whether you want the gray or blue version
 * @returns Rows of blobs.
 */
const renderLoadingBlobs = (numberOfRows: number, isGray: boolean = true) => {
  const rows = Array.from({ length: numberOfRows });
  const loadingBlobStyle = isGray ? "loading-blob-gray" : "loading-blob-blue";
  const sectionLineStyle = isGray ? "section__line_gray" : "section__line";

  return (
    <>
      {rows.map((_, index) => (
        <div key={index}>
          <div className="grid-row">
            <div className="grid-col-4">
              <div
                className={`${loadingBlobStyle}-small loading-blob margin-right-1 loading-blob`}
              >
                &nbsp;
              </div>
            </div>
            <div className={`loading-blob grid-col-8 ${loadingBlobStyle}-big`}>
              &nbsp;
            </div>
          </div>
          <div className={`${sectionLineStyle}`} />
        </div>
      ))}
    </>
  );
};

/**
 * Renders ECR Summary of the loading state
 * @returns A JSX component with rows of blobs.
 */
const EcrSummaryLoadingSkeleton = () => {
  return (
    <div className={"info-container"}>
      <div
        className="usa-summary-box padding-x-3 padding-y-0"
        aria-labelledby="summary-box-key-information"
      >
        <h3 className="summary-box-key-information side-nav-ignore font-sans-lg">
          About the Patient
        </h3>
        {renderLoadingBlobs(4, false)}
        <h3 className="summary-box-key-information side-nav-ignore font-sans-lg">
          About the Encounter
        </h3>
        {renderLoadingBlobs(4, false)}
        <h3 className="summary-box-key-information side-nav-ignore font-sans-lg">
          About the Condition
        </h3>
        {renderLoadingBlobs(4, false)}
      </div>
    </div>
  );
};

/**
 * Renders Accordion of the loading state
 * @returns A JSX component with rows of blobs.
 */
const AccordionLoadingSkeleton = () => {
  const renderEcrDocumentFiller = (title: string, numberOfRows: number) => {
    return (
      <AccordionSection>
        <AccordionH4>
          <span id={title}>{title}</span>
        </AccordionH4>
        <AccordionDiv>{renderLoadingBlobs(numberOfRows)}</AccordionDiv>
      </AccordionSection>
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
    <Accordion
      className="info-container"
      items={accordionItems}
      multiselectable={true}
    />
  );
};

/**
 * Creates the loading skeleton for the main ecr page
 * @returns ECR page loading skeleton
 */
export const EcrLoadingSkeleton = () => {
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
              <h2 className="margin-bottom-3 side-nav-ignore" id="ecr-summary">
                eCR Summary
              </h2>
              <EcrSummaryLoadingSkeleton />
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
                <AccordionLoadingSkeleton />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
