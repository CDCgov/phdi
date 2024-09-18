import { UseCaseQueryResponse } from "../../query-service";
import SideNav from "./SideNav";
import React, { useEffect } from "react";
import { Alert, Icon } from "@trussworks/react-uswds";
import ResultsViewTable from "./ResultsViewTable";

type ResultsViewProps = {
  useCaseQueryResponse: UseCaseQueryResponse;
  goBack: () => void;
  goBackToMultiplePatients?: () => void;
};

/**
 * The QueryView component to render the query results.
 * @param props - The props for the QueryView component.
 * @param props.useCaseQueryResponse - The response from the query service.
 * @param props.goBack - The function to go back to the previous page.
 * @param props.goBackToMultiplePatients - The function to go back to the multiple patients selection page.
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
      <div className="main-container grid-container grid-row">
        <div className="nav-wrapper tablet:grid-col-3">
          <nav className="sticky-nav">
            <SideNav />
          </nav>
        </div>
        <div className="tablet:grid-col-9">
          <div className="ecr-content">
            <h2 className="margin-bottom-3" id="ecr-summary">
              Query Results
            </h2>
            <div className="margin-top-6">
              <ResultsViewTable queryResponse={useCaseQueryResponse} />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
export default ResultsView;
