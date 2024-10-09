"use client";
import React, { useState } from "react";
import { UseCaseQueryResponse } from "../query-service";
import ResultsView from "./components/ResultsView";
import PatientSearchResults from "./components/PatientSearchResults";
import SearchForm from "./components/searchForm/SearchForm";
import SelectQuery from "./components/SelectQuery";
import { Mode, USE_CASES } from "../constants";
import LoadingView from "./components/LoadingView";
import { ToastContainer } from "react-toastify";

import "react-toastify/dist/ReactToastify.min.css";
import SiteAlert from "./designSystem/SiteAlert";
import { Patient } from "fhir/r4";

/**
 * Parent component for the query page. Based on the mode, it will display the search
 * form, the results of the query, or the multiple patients view.
 * @returns - The Query component.
 */
const Query: React.FC = () => {
  const [useCase, setUseCase] = useState<USE_CASES>("" as USE_CASES);
  const [mode, setMode] = useState<Mode>("search");
  const [loading, setLoading] = useState<boolean>(false);

  const [patientDiscoveryQueryResponse, setPatientDiscoveryQueryResponse] =
    useState<UseCaseQueryResponse>({});
  const [patientForQuery, setPatientForQueryResponse] = useState<Patient>();
  const [resultsQueryResponse, setResultsQueryResponse] =
    useState<UseCaseQueryResponse>({});

  return (
    <>
      <SiteAlert page={mode} />
      <div className="main-container">
        {mode === "search" && (
          <SearchForm
            useCase={useCase}
            setUseCase={setUseCase}
            setMode={setMode}
            setLoading={setLoading}
            setPatientDiscoveryQueryResponse={setPatientDiscoveryQueryResponse}
          />
        )}

        {mode === "patient-results" && (
          <>
            <PatientSearchResults
              patients={patientDiscoveryQueryResponse?.Patient ?? []}
              goBack={() => setMode("search")}
              setMode={setMode}
              setPatientForQueryResponse={setPatientForQueryResponse}
            />
          </>
        )}

        {mode === "select-query" && (
          <SelectQuery
            patientForQuery={patientForQuery}
            setMode={setMode}
            goBack={() => setMode("patient-results")}
            onSubmit={() => setMode("results")}
            resultsQueryResponse={resultsQueryResponse}
            setResultsQueryResponse={setResultsQueryResponse}
          />
        )}

        {mode === "results" && (
          <>
            {resultsQueryResponse && (
              <ResultsView
                useCaseQueryResponse={resultsQueryResponse}
                goBack={() => {
                  setMode("select-query");
                }}
                goToBeginning={() => {
                  setMode("search");
                }}
              />
            )}
          </>
        )}
        <LoadingView loading={loading} />

        <ToastContainer icon={false} />
      </div>
    </>
  );
};

export default Query;
