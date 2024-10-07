"use client";
import {
  Accordion,
  Grid,
  GridContainer,
  SideNav,
} from "@trussworks/react-uswds";
import { ExpandCollapseButtons } from "./ExpandCollapseButtons";
import {
  AccordionDiv,
  AccordionH4,
  AccordionSection,
} from "../component-utils";
import Header from "@/app/Header";
import classNames from "classnames";
import PatientBanner from "./PatientBanner";
import { BackButton } from "./BackButton";

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
    <div>
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
          {numberOfRows > 1 ? (
            <div className={`${sectionLineStyle}`}></div>
          ) : (
            ""
          )}
        </div>
      ))}
    </div>
  );
};

const renderSideNavLoadingItems = () => {
  const loadingBlobStyle = "loading-blob-gray";

  return (
    <div>
      <div className="grid-row">
        <div
          className={`loading-blob grid-col-8 ${loadingBlobStyle}-big width-full`}
        >
          &nbsp;
        </div>
      </div>
    </div>
  );
};

const SideNavLoadingSkeleton = ({
  isNonIntegratedViewer,
}: {
  isNonIntegratedViewer: boolean;
}) => {
  const sideNavLoadingItems = [
    <a>eCR Summary</a>,
    <a>eCR Document</a>,
    <SideNav
      items={[
        <a>Patient Info</a>,
        <SideNav
          items={[<a>{renderSideNavLoadingItems()}</a>]}
          isSubnav={true}
        ></SideNav>,
        <a>Clinical Info</a>,
        <SideNav
          items={[<a>{renderSideNavLoadingItems()}</a>]}
          isSubnav={true}
        ></SideNav>,
        <a>Lab Info</a>,
        <SideNav
          items={[<a>{renderSideNavLoadingItems()}</a>]}
          isSubnav={true}
        ></SideNav>,
        <a>eCR Metadata</a>,
        <SideNav
          items={[<a>{renderSideNavLoadingItems()}</a>]}
          isSubnav={true}
        ></SideNav>,
        <a>Unavailable Info</a>,
        <SideNav
          items={[<a>{renderSideNavLoadingItems()}</a>]}
          isSubnav={true}
        ></SideNav>,
      ]}
      isSubnav={true}
    />,
  ];

  return (
    <div className="nav-wrapper">
      <BackButton />
      <nav
        className={classNames("sticky-nav", {
          "top-0": !isNonIntegratedViewer,
          "top-550": isNonIntegratedViewer,
        })}
      >
        <SideNav items={sideNavLoadingItems} />
      </nav>
    </div>
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
          Patient Summary
        </h3>
        {renderLoadingBlobs(4, false)}
        <h3 className="summary-box-key-information side-nav-ignore font-sans-lg">
          Encounter Summary
        </h3>
        {renderLoadingBlobs(4, false)}
        <h3 className="summary-box-key-information side-nav-ignore font-sans-lg">
          Condition Summary
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
          {renderEcrDocumentFiller("eICR Details", 5)}
          {renderEcrDocumentFiller("eICR Custodian Details", 4)}
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
  const _isNonIntegratedViewer =
    process.env.NEXT_PUBLIC_NON_INTEGRATED_VIEWER === "true";
  return (
    <main className={"width-full minw-main"}>
      <Header />
      {_isNonIntegratedViewer ? (
        <PatientBanner bundle={undefined} mappings={undefined} />
      ) : (
        ""
      )}
      <div className="main-container">
        <div className={"width-main padding-main"}>
          <div className="content-wrapper">
            <div>
              <SideNavLoadingSkeleton
                isNonIntegratedViewer={_isNonIntegratedViewer ? true : false}
              />
            </div>
            <div className={"ecr-viewer-container"}>
              <div className="margin-bottom-3">
                <h2 className="margin-bottom-05 margin-top-3" id="ecr-summary">
                  eCR Summary
                </h2>
                <div className="text-base-darker line-height-sans-5">
                  Provides key info upfront to help you understand the eCR at a
                  glance
                </div>
              </div>
              <EcrSummaryLoadingSkeleton />
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
                  <div className="text-base-darker line-height-sans-5">
                    Displays entire eICR and RR documents to help you dig
                    further into eCR data
                  </div>
                </GridContainer>
                <AccordionLoadingSkeleton />
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
};
