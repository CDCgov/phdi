import { UseCaseQueryResponse } from "../../query-service";
import AccordionContainer from "./AccordionContainer";
import SideNav from "./SideNav";
import React from "react";

type PatientViewProps = {
    useCaseQueryResponse: UseCaseQueryResponse;
}
export function PatientView({ useCaseQueryResponse }: PatientViewProps) {

    return (<div>
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
                  <AccordionContainer
                    queryResponse={useCaseQueryResponse}
                  />
                </div>
              </div>
            </div>
                </div>
            </div>
        </div>
    </div>)
}