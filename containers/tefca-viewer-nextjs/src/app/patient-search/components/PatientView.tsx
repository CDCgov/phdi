import { UseCaseQueryResponse } from "../patient_search";
import AccordionContainer from "./AccordionContainer";
import SideNav from "./SideNav";
// import { PathMappings } from "@/app/utils";
import React from "react";
import mappings from "@/app/api/fhirPath.json" assert { type: "json" };

type PatientViewProps = {
    useCaseQueryResponse: UseCaseQueryResponse;
}
export function PatientView({ useCaseQueryResponse }: PatientViewProps) {

    console.log("useCaseQueryResponse", useCaseQueryResponse);
    console.log("mappings", mappings);

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