import { UseCaseQueryResponse } from "../../query-service";
import AccordionContainer from "./AccordionContainer";
import SideNav from "./SideNav";
import React from "react";

type QueryViewProps = {
  useCaseQueryResponse: UseCaseQueryResponse;
};

/**
 * The QueryView component to render the query results.
 * @param props - The props for the QueryView component.
 * @param props.useCaseQueryResponse - The response from the query service.
 * @returns The QueryView component.
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
