import React, { useCallback, useEffect, useState } from "react";
import {
  Fieldset,
  Label,
  TextInput,
  Select,
  Alert,
  Button,
} from "@trussworks/react-uswds";
import { fhirServers } from "../../fhir-servers";
import {
  USE_CASES,
  FHIR_SERVERS,
  demoData,
  PatientType,
  demoQueryOptions,
  patientOptions,
  stateOptions,
  Mode,
} from "../../constants";
import {
  UseCaseQueryResponse,
  UseCaseQuery,
  UseCaseQueryRequest,
} from "../../query-service";

import { FormatPhoneAsDigits } from "@/app/format-service";

interface SearchFormProps {
  useCase: USE_CASES;
  setUseCase: (useCase: USE_CASES) => void;
  setOriginalRequest: (originalRequest: UseCaseQueryRequest) => void;
  setUseCaseQueryResponse: (UseCaseQueryResponse: UseCaseQueryResponse) => void;
  setMode: (mode: Mode) => void;
  setLoading: (loading: boolean) => void;
  setQueryType: (queryType: string) => void;
  userJourney: "test" | "demo";
}

/**
 * @param root0 - SearchFormProps
 * @param root0.useCase - The use case this query will cover.
 * @param root0.setUseCase - Update stateful use case.
 * @param root0.setOriginalRequest - The function to set the original request.
 * @param root0.setUseCaseQueryResponse - The function to set the use case query response.
 * @param root0.setMode - The function to set the mode.
 * @param root0.setLoading - The function to set the loading state.
 * @param root0.setQueryType - The function to set the query type.
 * @param root0.userJourney - The user journey.
 * @returns - The SearchForm component.
 */
const SearchForm: React.FC<SearchFormProps> = ({
  useCase,
  setUseCase,
  setOriginalRequest,
  setUseCaseQueryResponse,
  setMode,
  setLoading,
  setQueryType,
  userJourney,
}) => {
  //Set the patient options based on the demoOption
  const [patientOption, setPatientOption] = useState<string>(
    patientOptions[useCase]?.[0]?.value || ""
  );
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<FHIR_SERVERS>();
  const [phone, setPhone] = useState<string>("");
  const [dob, setDOB] = useState<string>("");
  const [mrn, setMRN] = useState<string>("");

  const [autofilled, setAutofilled] = useState(false); // boolean indicating if the form was autofilled, changes color if true

  // Fills fields with sample data based on the selected patientOption
  const fillFields = useCallback(
    (patientOption: PatientType, highlightAutofilled = true) => {
      const data = demoData[patientOption];
      if (data) {
        setFirstName(data.FirstName);
        setLastName(data.LastName);
        setDOB(data.DOB);
        setMRN(data.MRN);
        setPhone(data.Phone);
        setFhirServer(data.FhirServer as FHIR_SERVERS);
        setUseCase(data.UseCase as USE_CASES);
        // setQueryType(
        //     demoQueryOptions.find((option) => option.value === data.UseCase)
        //         ?.label || "",
        // );
        setAutofilled(highlightAutofilled);
      }
    },
    [patientOption, setUseCase, setQueryType]
  );

  // Fills fields if patientOption changes (auto-fill)
  useEffect(() => {
    if (!patientOption || userJourney !== "demo") {
      return;
    }
    fillFields(patientOption as PatientType);
  }, [fillFields, patientOption, userJourney]);

  // Change the selectedDemoOption in the dropdown and update the
  // query type (which governs the DB fetch) accordingly
  const handleDemoQueryChange = (selectedDemoOption: string) => {
    setPatientOption(patientOptions[selectedDemoOption][0].value);
    setQueryType(
      demoQueryOptions.find((dqo) => dqo.value == selectedDemoOption)?.label ||
        ""
    );
  };

  const handleClick = () => {
    setMode("customize-queries");
  };

  async function HandleSubmit(event: React.FormEvent<HTMLFormElement>) {
    if (!useCase || !fhirServer) {
      console.error("Use case and FHIR server are required.");
      return;
    }
    event.preventDefault();
    setLoading(true);

    const originalRequest = {
      first_name: firstName,
      last_name: lastName,
      dob: dob,
      mrn: mrn,
      fhir_server: fhirServer,
      use_case: useCase,
      phone: FormatPhoneAsDigits(phone),
    };
    setOriginalRequest(originalRequest);
    const queryResponse = await UseCaseQuery(originalRequest);
    setUseCaseQueryResponse(queryResponse);
    if (!queryResponse.Patient || queryResponse.Patient.length === 0) {
      setMode("no-patients");
    } else if (queryResponse.Patient.length === 1) {
      setMode("results");
    } else {
      setMode("multiple-patients");
    }
    setLoading(false);
  }
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <>
      <form className="patient-search-form" onSubmit={HandleSubmit}>
        <h1 className="font-sans-2xl text-bold">Search for a Patient</h1>
        {userJourney === "test" && (
          <>
            <h2 className="font-sans-lg search-form-section-label">
              <strong>Query information</strong>
            </h2>
            <Label htmlFor="query">
              <b>Query</b>
            </Label>
            <div className="grid-row grid-gap">
              <div className="usa-combo-box" data-enhanced="true">
                <select
                  id="query"
                  name="query"
                  className="usa-select margin-top-1"
                  value={useCase}
                  onChange={(event) => {
                    handleDemoQueryChange(event.target.value);
                    setUseCase(event.target.value as USE_CASES);
                  }}
                >
                  {demoQueryOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <Label htmlFor="fhir_server">
              <b>FHIR Server (QHIN)</b>
            </Label>
            <div className="grid-row grid-gap">
              <div className="usa-combo-box">
                <Select
                  id="fhir_server"
                  name="fhir_server"
                  value={fhirServer}
                  onChange={(event) => {
                    setFhirServer(event.target.value as FHIR_SERVERS);
                  }}
                  required
                  defaultValue=""
                >
                  <option value="" disabled>
                    Select FHIR Server
                  </option>
                  {Object.keys(fhirServers).map((fhirServer: string) => (
                    <option key={fhirServer} value={fhirServer}>
                      {fhirServer}
                    </option>
                  ))}
                </Select>
              </div>
            </div>
            <h2 className="font-sans-lg search-form-section-label">
              <strong>Patient information</strong>
            </h2>
            <div className="usa-summary-box test-query-filler">
              <Label
                className="usa-label margin-bottom-2 font-sans-xs"
                htmlFor="query"
              >
                <b>
                  Select a patient type to populate the form with sample data.
                </b>
              </Label>
              <div className="display-flex flex-align-start">
                <div className="usa-combo-box flex-1" data-enhanced="true">
                  <Label htmlFor="patient">Patient</Label>
                  <select
                    id="patient"
                    name="patient"
                    className="usa-select margin-top-1"
                    value={patientOption}
                    onChange={(event) => {
                      setPatientOption(event.target.value);
                    }}
                  >
                    {patientOptions[useCase]?.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <Button
                  className="margin-left-1  margin-top-4 usa-button--outline bg-white"
                  type="button"
                  value={patientOption}
                  onClick={() => {
                    fillFields(patientOption as PatientType, false);
                  }}
                >
                  Fill fields
                </Button>
              </div>
            </div>
          </>
        )}
        {userJourney === "demo" && (
          <div className="usa-summary-box usa-summary-box demo-query-filler">
            <Label className="usa-label" htmlFor="query">
              <b>Select a sample query and patient to populate the form.</b>
            </Label>
            <Label htmlFor="query">Query</Label>
            <div className="display-flex flex-align-start query-customize-wrapper">
              <select
                id="query"
                name="query"
                className="usa-select margin-top-1"
                defaultValue={""}
                value={useCase}
                onChange={(event) => {
                  handleDemoQueryChange(event.target.value);
                  setUseCase(event.target.value as USE_CASES);
                }}
              >
                <option value="" disabled>
                  {" "}
                  -- Select An Option --{" "}
                </option>
                {demoQueryOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <Button
                type="button"
                className="usa-button usa-button--outline customize-query-button"
                onClick={() => handleClick()}
              >
                Customize query
              </Button>
            </div>
            <Label htmlFor="patient">Patient</Label>
            <select
              id="patient"
              name="patient"
              className="usa-select margin-top-1"
              value={patientOption}
              onChange={(event) => {
                setPatientOption(event.target.value);
              }}
            >
              {patientOptions[useCase]?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        )}
        <Fieldset>
          <h2 className="font-sans-md search-form-section-label">
            <strong>Name</strong>
          </h2>
          <div className="grid-row grid-gap">
            <div className="tablet:grid-col-6">
              <Label htmlFor="firstName">First Name</Label>
              <TextInput
                id="firstName"
                name="first_name"
                type="text"
                pattern="^[A-Za-z ]+$"
                value={firstName}
                onChange={(event) => {
                  setFirstName(event.target.value);
                }}
                style={{
                  backgroundColor:
                    autofilled && firstName ? autofillColor : undefined,
                }}
              />
            </div>
            <div className="tablet:grid-col-6">
              <Label htmlFor="lastName">Last Name</Label>
              <TextInput
                id="lastName"
                name="last_name"
                type="text"
                pattern="^[A-Za-z ]+$"
                value={lastName}
                onChange={(event) => {
                  setLastName(event.target.value);
                }}
                style={{
                  backgroundColor:
                    autofilled && lastName ? autofillColor : undefined,
                }}
              />
            </div>
          </div>
          <h2 className="font-sans-md search-form-section-label">
            <strong>Phone Number</strong>
          </h2>
          <div className="grid-row grid-gap">
            <div className="grid-col-6">
              <Label htmlFor="phone">Phone Number</Label>
              <TextInput
                id="phone"
                name="phone"
                type="tel"
                value={phone}
                onChange={(event) => {
                  setPhone(event.target.value);
                }}
                style={{
                  backgroundColor:
                    autofilled && phone ? autofillColor : undefined,
                }}
              />
            </div>
          </div>
          <div>
            <h2 className="font-sans-md search-form-section-label">
              <strong>Date of Birth</strong>
            </h2>
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
                    style={{
                      backgroundColor:
                        autofilled && dob ? autofillColor : undefined,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
          <h2 className="font-sans-md search-form-section-label">
            <strong>Address</strong>
          </h2>
          <div className="grid-row grid-gap">
            <div className="grid-col">
              <Label htmlFor="street_address_1">Street address</Label>
              <TextInput
                id="street_address_1"
                name="street_address_1"
                type="tel"
              />
            </div>
          </div>
          <div className="grid-row grid-gap">
            <div className="grid-col">
              <Label htmlFor="street_address_2">Address Line 2</Label>
              <TextInput
                id="street_address_2"
                name="street_address_2"
                type="text"
              />
            </div>
          </div>
          <div className="grid-row grid-gap">
            <div className="tablet:grid-col-5">
              <Label htmlFor="city">City</Label>
              <TextInput id="city" name="city" type="text" />
            </div>
            <div className="tablet:grid-col-3">
              <Label htmlFor="state">State</Label>
              <Select id="state" name="state" defaultValue="">
                <option value="" disabled>
                  Select a state
                </option>
                {stateOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
            </div>
            <div className="tablet:grid-col-4">
              <Label htmlFor="zip">ZIP code</Label>
              <TextInput
                className="usa-input usa-input--medium"
                id="zip"
                name="zip"
                type="text"
                pattern="[\d]{5}(-[\d]{4})?"
              />
            </div>
          </div>
          <h2 className="font-sans-md search-form-section-label">
            <strong>Medical Record Number (MRN)</strong>
          </h2>
          <div className="grid-row grid-gap">
            <div className="grid-col-6">
              <Label htmlFor="mrn">Medical Record Number</Label>
              <TextInput
                id="mrn"
                name="mrn"
                type="text"
                value={mrn}
                onChange={(event) => {
                  setMRN(event.target.value);
                }}
                style={{
                  backgroundColor:
                    autofilled && mrn ? autofillColor : undefined,
                }}
              />
            </div>
          </div>
        </Fieldset>
        <button className="usa-button patient-search-button" type="submit">
          Search for patient
        </button>
      </form>
    </>
  );
};

export default SearchForm;

const autofillColor = "#faf3d1";
