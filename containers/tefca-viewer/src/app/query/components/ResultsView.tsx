import { UseCaseQueryResponse } from "../../query-service";
import AccordionContainer from "./AccordionContainer";
import SideNav from "./SideNav";
import React, { useEffect } from "react";
import { Alert, Icon } from "@trussworks/react-uswds";

type ResultsViewProps = {
  useCaseQueryResponse: UseCaseQueryResponse;
  goBack: () => void;
  backLabel?: string;
  goBackToMultiplePatients?: () => void;
};

/**
 * The QueryView component to render the query results.
 * @param props - The props for the QueryView component.
 * @param props.useCaseQueryResponse - The response from the query service.
 * @param props.goBack - The function to go back to the previous page.
 * @param props.backLabel - The label for the back button.
 * @param props.goBackToMultiplePatients
 * @returns The QueryView component.
 */
const ResultsView: React.FC<ResultsViewProps> = ({
  useCaseQueryResponse,
  goBack,
  goBackToMultiplePatients,
}) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return (
    <>
      <Alert type="info" headingLevel="h4" slim className="custom-alert">
        Interested in learning more about using the TEFCA Query Connector for
        your jurisdiction? Send us an email at{" "}
        <a
          href="mailto:dibbs@cdc.gov"
          style={{
            color: "inherit",
            fontWeight: "bold",
            textDecoration: "underline",
          }}
        >
          dibbs@cdc.gov
        </a>
      </Alert>

      <div className="results-banner">
        <div className="results-banner-content usa-nav-container">
          {goBackToMultiplePatients && (
            <>
              <a
                href="#"
                onClick={() => goBackToMultiplePatients()}
                className="back-link"
              >
                <Icon.ArrowBack />
                Return to search results
              </a>
              <div className="results-banner-divider">|</div>
            </>
          )}

          <a href="#" onClick={() => goBack()} className="back-link">
            New patient search
          </a>
        </div>
      </div>
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
                Query Results
              </h2>
              <div className="margin-top-6">
                <AccordionContainer queryResponse={useCaseQueryResponse} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
export default ResultsView;
