"use client";
import React, { useState } from "react";
import { use_case_query } from "./patient_search";

const PatientSearch: React.FC = () => {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<"meld" | "ehealthexchange">("meld");
  const [dob, setdob] = useState<string>("");

  const handleSubmit = async () => {
    console.log("First Name:", firstName);
    console.log("Last Name:", lastName);
    console.log("FHIR Server:", fhirServer);
    console.log("Date of Birth:", dob);
    const patient_id = await use_case_query({ fhir_server: fhirServer, first_name: firstName, last_name: lastName, dob: dob });
    console.log("Patient ID:", patient_id)
  };


  return (
    <div>
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
          <option value="ehealth-exchange">eHealth Exchange</option>
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
    </div>
  );
};

export default PatientSearch;
