"use client";
import React, { useState } from "react";
import { UseCaseQueryResponse } from "../query-service";
import ResultsView from "./components/ResultsView";
import PatientSearchResults from "./components/PatientSearchResults";
import SearchForm from "./components/searchForm/SearchForm";
import SelectQuery from "./components/SelectQuery";
import { FHIR_SERVERS, Mode, USE_CASES, ValueSetItem } from "../constants";
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
  const [fhirServer, setFhirServer] = useState<FHIR_SERVERS>(
    "Public HAPI: eHealthExchange",
  );

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
            fhirServer={fhirServer}
            setFhirServer={setFhirServer}
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
            goBack={() => setMode("patient-results")}
            onSubmit={() => setMode("results")}
            selectedQuery={useCase}
            setSelectedQuery={setUseCase}
            patientForQuery={patientForQuery}
            resultsQueryResponse={resultsQueryResponse}
            setResultsQueryResponse={setResultsQueryResponse}
            fhirServer={fhirServer}
            setFhirServer={setFhirServer}
          />
        )}

        {mode === "results" && (
          <>
            {resultsQueryResponse && (
              <ResultsView
                selectedQuery={useCase}
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
