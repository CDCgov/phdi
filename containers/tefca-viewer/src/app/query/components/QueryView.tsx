import { UseCaseQueryResponse } from "../../query-service";
import AccordionContainer from "./AccordionContainer";
import SideNav from "./SideNav";
import React, { useEffect } from "react";
import { Mode } from "../page";

type QueryViewProps = {
  useCaseQueryResponse: UseCaseQueryResponse;
  setMode: (mode: Mode) => void;
};

/**
 * The QueryView component to render the query results.
 * @param props - The props for the QueryView component.
 * @param props.useCaseQueryResponse - The response from the query service.
 * @param props.setMode - The function to set the mode of the query page.
 * @returns The QueryView component.
 */
const QueryView: React.FC<QueryViewProps> = ({
  useCaseQueryResponse,
  setMode,
}) => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  return (
    <>
      <div className="results-banner">
        <div className="results-banner-content usa-nav-container">
          <a href="#" onClick={() => setMode("search")}>
            Return to search
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
export default QueryView;
