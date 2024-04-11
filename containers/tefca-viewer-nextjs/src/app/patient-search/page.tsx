"use client";
import React, { useState } from "react";
import { UseCaseQueryResponse, use_case_query } from "./patient_search";
import { PatientView } from "./components/PatientView";
import { Fieldset, Label, TextInput, DatePicker, Select } from "@trussworks/react-uswds";

export function PatientSearch() {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<"meld" | "ehealthexchange">();
  const [phone, setPhone] = useState<string>("");
  const [dob, setDOB] = useState<string>("");
  const [mrn, setMRN] = useState<string>("");
  const [useCase, setUseCase] = useState<"social-determinants" | "newborn-screening" | "syphilis"|"cancer">();

  // Set a mode to switch between search and view
  const [mode, setMode] = useState<"search" | "view">("search");
  // Set a loading state to show a loading message when loading
  const [loading, setLoading] = useState<boolean>(false);
  // Set a state to store the response from the use case query
  const [useCaseQueryResponse, setUseCaseQueryResponse] = useState<UseCaseQueryResponse>();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    console.log("Event:", event)
    const use_case_query_response = await use_case_query({ use_case: useCase, fhir_server: fhirServer, first_name: firstName, last_name: lastName, dob: dob });
    console.log("Patient ID:", use_case_query_response)
    setUseCaseQueryResponse(use_case_query_response);
    setMode("view");
    setLoading(false);
  };

  return (
    <div>
      {mode === "search" && (<>
        <form className="patient-search-form" onSubmit={handleSubmit}>
          <h1 className="font-sans-2xl text-bold">Search for a Patient</h1>
          <Fieldset>
            <h2 className="font-sans-lg search-form-section-label"><strong>Name</strong></h2>
            <div className="grid-row grid-gap">
              <div className="tablet:grid-col-6">
                <Label htmlFor="first_name">First Name</Label>
                <TextInput id="firstName" name="first_name" type="text" pattern="^[A-Za-z]+$"
                  value={firstName}
                  onChange={(event) => {
                    setFirstName(event.target.value);
                  }} />
              </div>
              <div className="tablet:grid-col-6">
                <Label htmlFor="last_name">Last Name</Label>
                <TextInput id="lastName" name="last_name" type="text" pattern="^[A-Za-z]+$"
                  value={lastName}
                  onChange={(event) => {
                    setLastName(event.target.value);
                  }} />
              </div>
            </div>
            <h2 className="font-sans-lg search-form-section-label"><strong>Phone Number</strong></h2>
            <div className="grid-row grid-gap">
              <div className="grid-col-6">
                <Label htmlFor="phone">Phone Number</Label>
                <TextInput id="phone" name="phone" type="tel" value={phone} onChange={(event) => {
                  setPhone(event.target.value);
                }} />
              </div>
            </div>
            <div>
              <h2 className="font-sans-lg search-form-section-label"><strong>Date of Birth</strong></h2>
              <div className="grid-row grid-gap">
                <div className="grid-col-6">
                  <Label htmlFor="dob">Date of Birth</Label>
                  <div className="usa-date-picker">
                    <input
                      className="usa-input"
                      name="dob"
                      id="dob"
                      type="date"
                      value={dob}
                      onChange={(event) => {
                        setDOB(event.target.value);
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
            <h2 className="font-sans-lg search-form-section-label"><strong>Address</strong></h2>
            <div className="grid-row grid-gap">
              <div className="grid-col">
                <Label htmlFor="street_address_1">Street address</Label>
                <TextInput id="street_address_1" name="street_address_1" type="tel" />
              </div>
            </div>
            <div className="grid-row grid-gap">
              <div className="grid-col">
                <Label htmlFor="street_address_2">Address Line 2</Label>
                <TextInput id="street_address_2" name="street_address_2" type="text" />
              </div>
            </div>
            <div className="grid-row grid-gap">
              <div className="tablet:grid-col-5">
                <Label htmlFor="city">City</Label>
                <TextInput id="city" name="city" type="text" />
              </div>
              <div className="tablet:grid-col-3">
                <Label htmlFor="state">State</Label>
                <Select id="state" name="state">
                  <option value="" disabled selected></option>
                  <option value="AL">AL - Alabama</option>
                  <option value="AK">AK - Alaska</option>
                  <option value="AS">AS - American Samoa</option>
                  <option value="AZ">AZ - Arizona</option>
                  <option value="AR">AR - Arkansas</option>
                  <option value="CA">CA - California</option>
                  <option value="CO">CO - Colorado</option>
                  <option value="CT">CT - Connecticut</option>
                  <option value="DE">DE - Delaware</option>
                  <option value="DC">DC - District of Columbia</option>
                  <option value="FL">FL - Florida</option>
                  <option value="GA">GA - Georgia</option>
                  <option value="GU">GU - Guam</option>
                  <option value="HI">HI - Hawaii</option>
                  <option value="ID">ID - Idaho</option>
                  <option value="IL">IL - Illinois</option>
                  <option value="IN">IN - Indiana</option>
                  <option value="IA">IA - Iowa</option>
                  <option value="KS">KS - Kansas</option>
                  <option value="KY">KY - Kentucky</option>
                  <option value="LA">LA - Louisiana</option>
                  <option value="ME">ME - Maine</option>
                  <option value="MD">MD - Maryland</option>
                  <option value="MA">MA - Massachusetts</option>
                  <option value="MI">MI - Michigan</option>
                  <option value="MN">MN - Minnesota</option>
                  <option value="MS">MS - Mississippi</option>
                  <option value="MO">MO - Missouri</option>
                  <option value="MT">MT - Montana</option>
                  <option value="NE">NE - Nebraska</option>
                  <option value="NV">NV - Nevada</option>
                  <option value="NH">NH - New Hampshire</option>
                  <option value="NJ">NJ - New Jersey</option>
                  <option value="NM">NM - New Mexico</option>
                  <option value="NY">NY - New York</option>
                  <option value="NC">NC - North Carolina</option>
                  <option value="ND">ND - North Dakota</option>
                  <option value="MP">MP - Northern Mariana Islands</option>
                  <option value="OH">OH - Ohio</option>
                  <option value="OK">OK - Oklahoma</option>
                  <option value="OR">OR - Oregon</option>
                  <option value="PA">PA - Pennsylvania</option>
                  <option value="PR">PR - Puerto Rico</option>
                  <option value="RI">RI - Rhode Island</option>
                  <option value="SC">SC - South Carolina</option>
                  <option value="SD">SD - South Dakota</option>
                  <option value="TN">TN - Tennessee</option>
                  <option value="TX">TX - Texas</option>
                  <option value="UM">UM - United States Minor Outlying Islands</option>
                  <option value="UT">UT - Utah</option>
                  <option value="VT">VT - Vermont</option>
                  <option value="VI">VI - Virgin Islands</option>
                  <option value="VA">VA - Virginia</option>
                  <option value="WA">WA - Washington</option>
                  <option value="WV">WV - West Virginia</option>
                  <option value="WI">WI - Wisconsin</option>
                  <option value="WY">WY - Wyoming</option>
                  <option value="AA">AA - Armed Forces Americas</option>
                  <option value="AE">AE - Armed Forces Africa</option>
                  <option value="AE">AE - Armed Forces Canada</option>
                  <option value="AE">AE - Armed Forces Europe</option>
                  <option value="AE">AE - Armed Forces Middle East</option>
                  <option value="AP">AP - Armed Forces Pacific</option>
                </Select>
              </div>
              <div className="tablet:grid-col-4">
                <Label htmlFor="zip">ZIP code</Label>
                <TextInput className="usa-input usa-input--medium" id="zip" name="zip" type="text" pattern="[\d]{5}(-[\d]{4})?" />
              </div>
            </div>
            <h2 className="font-sans-lg search-form-section-label"><strong>Medical Record Number (MRN)</strong></h2>
            <div className="grid-row grid-gap">
              <div className="grid-col-6">
                <Label htmlFor="mrn">Medical Record Number</Label>
                <TextInput id="mrn" name="mrn" type="text" pattern="^\d+$" value={mrn} onChange={(event) => {
                  setMRN(event.target.value);
                }}/>
              </div>
            </div>
            <h2 className="font-sans-lg search-form-section-label"><strong>Case investigation topic</strong></h2>
            <div className="grid-row grid-gap">
              <div className="grid-col-7">
                <Label htmlFor="use_case">Use case</Label>
                <Select id="use_case" name="use_case" value={useCase} onChange={(event) => {
                  setUseCase(event.target.value as "social-determinants" | "newborn-screening" | "syphilis" | "cancer");
                }} 
                required>
                  <option value="" disabled selected></option>
                  <option value="newborn-screening">Newborn Screening</option>
                  <option value="syphilis">Syphilis</option>
                  <option value="cancer">Cancer</option>
                  <option value="social-determinants">Social Determinants of Health</option>
                </Select>
              </div>
            </div>
            <h2 className="font-sans-lg search-form-section-label"><strong>FHIR Server (QHIN)</strong></h2>
              <div className="grid-row grid-gap">
              <div className="grid-col-5">
                <Label htmlFor="fhir_server">FHIR Server</Label>
                <Select id="fhir_server" name="fhir_server" value={fhirServer} onChange={(event) => {
                  setFhirServer(event.target.value as "meld" | "ehealthexchange");
                }}
                  required>
                  <option value="" disabled selected></option>
                  <option value="meld">Meld</option>
                  <option value="ehealthexchange">eHealth Exchange</option>
                </Select>
              </div>
                  </div>
          </Fieldset>
          <button className="usa-button patient-search-button" type="submit">
            Search for patient
          </button>
        </form>
      </>)}

      {/* Switch the mode to view to show the results of the query */}
      {mode === "view" && (<>
        <button className="usa-button" onClick={() => setMode("search")}>Search for a new patient</button>
        <LoadingView loading={loading} />
        {/* TODO: add error view if loading is done and there's no useCaseQueryResponse */}
        {useCaseQueryResponse && <PatientView useCaseQueryResponse={useCaseQueryResponse} />}
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
