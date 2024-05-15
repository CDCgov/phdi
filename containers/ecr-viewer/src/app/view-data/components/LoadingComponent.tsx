"use client";
import { Accordion } from "@trussworks/react-uswds";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";

/**
 * Renders the loading blobs in gray or in blue
 * @param numberOfRows - number of rows to render
 * @param isGray - whether you want the gray or blue version
 * @returns Rows of blobs.
 */
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
              <div className={`${loadingBlobStyle} margin-right-1`}>&nbsp;</div>
            </div>
            <div className={`grid-col-8 ${loadingBlobStyle}`}>&nbsp;</div>
          </div>
          <div className={sectionLineStyle} />
        </div>
      ))}
    </>
  );
};

/**
 * Renders ECR Summary of the loading state
 * @returns A JSX component with rows of blobs.
 */
export const EcrSummaryLoadingSkeleton = () => {
  return (
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
  );
};

/**
 * Renders Accordion of the loading state
 * @returns A JSX component with rows of blobs.
 */
export const AccordionLoadingSkeleton = () => {
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
