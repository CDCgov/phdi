"use client";
import React, { useState } from "react";
import { PatientQueryResponse, use_case_query } from "./patient_search";
import { PatientView } from "./components/PatientView";

export function PatientSearch() {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<"meld" | "ehealthexchange">("meld");
  const [dob, setdob] = useState<string>("");


  // Set a mode to switch between search and view
  const [mode, setMode] = useState<"search" | "view">("search");
  // Set a loading state to show a loading message when loading
  const [loading, setLoading] = useState<boolean>(false);
  // Set a state to store the response from the use case query
  const [useCaseQueryResponse, setUseCaseQueryResponse] = useState<PatientQueryResponse>();

  const handleSubmit = async () => {
    setLoading(true);
    console.log("First Name:", firstName);
    console.log("Last Name:", lastName);
    console.log("FHIR Server:", fhirServer);
    console.log("Date of Birth:", dob);
    const use_case_query_response = await use_case_query({ fhir_server: fhirServer, first_name: firstName, last_name: lastName, dob: dob });
    console.log("Patient ID:", use_case_query_response)
    setUseCaseQueryResponse(use_case_query_response);
    setMode("view");
    setLoading(false);
  };


  return (
    <div>
      {mode === "search" && (<>
        <h1>Patient Search</h1>
        <div>
          <label htmlFor="fhirServer">FHIR Server:</label>
          <select
            id="fhirServer"
            value={fhirServer}
            onChange={(event) => {
              setFhirServer(event.target.value as "meld" | "ehealthexchange");
            }}
            required
          >
            <option value="" disabled>Select FHIR Server</option>
            <option value="meld">Meld</option>
            <option value="ehealthexchange">eHealth Exchange</option>
          </select>
        </div>
        <div>
          <label htmlFor="firstName">First Name:</label>
          <input
            type="text"
            id="firstName"
            value={firstName}
            onChange={(event) => {
              setFirstName(event.target.value);
            }}
          />
        </div>
        <div>
          <label htmlFor="lastName">Last Name:</label>
          <input
            type="text"
            id="lastName"
            value={lastName}
            onChange={(event) => {
              setLastName(event.target.value);
            }}
          />
        </div>
        <div>
          <label htmlFor="dob">Date of Birth:</label>
          <input
            type="date"
            id="dob"
            value={dob}
            onChange={(event) => {
              setdob(event.target.value);
            }}
          />
        </div>
        <button type="button" onClick={handleSubmit}>
          Submit
        </button>
      </>)}

      {/* Switch the mode to view to show the results of the query */}
      {mode === "view" && (<>
        <h1>Patient View</h1>
        <button type="button" onClick={() => setMode("search")}>Search for a new patient</button>
        <LoadingView loading={loading} />
        <PatientView useCaseQueryResponse={useCaseQueryResponse} />
      </>)}
    </div>
  );
};

function LoadingView({ loading }: { loading: boolean }) {
  if (loading) {
    return (<div>
      <h2>Loading...</h2>
    </div>)
  } else {
    return null;
  }
}

export default PatientSearch;
