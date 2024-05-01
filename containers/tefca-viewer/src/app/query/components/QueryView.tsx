import { UseCaseQueryResponse } from "../../query-service";
import AccordionContainer from "./AccordionContainer";
import SideNav from "./SideNav";
import React from "react";

/**
 * Displays query results.
 * @param {UseCaseQueryResponse} useCaseQueryResponse - The query results to display.
 * @returns {React.FC} The QueryView component.
 */
type QueryViewProps = {
  useCaseQueryResponse: UseCaseQueryResponse;
};

/**
 *
 * @param root0
 * @param root0.useCaseQueryResponse
 */
const QueryView: React.FC<QueryViewProps> = ({ useCaseQueryResponse }) => {
  return (
    <div>
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
      </div>
    </div>
  );
};
export default QueryView;
