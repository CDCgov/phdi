import React, { useCallback, useEffect, useState } from "react";
import {
  Fieldset,
  Label,
  TextInput,
  Select,
  Button,
} from "@trussworks/react-uswds";
import {
  USE_CASES,
  FHIR_SERVERS,
  demoData,
  PatientType,
  demoQueryOptions,
  patientOptions,
  stateOptions,
  Mode,
  ValueSetItem,
} from "../../../constants";
import {
  UseCaseQueryResponse,
  UseCaseQuery,
  UseCaseQueryRequest,
} from "../../../query-service";
import { fhirServers } from "../../../fhir-servers";
import styles from "./searchForm.module.css";

import { FormatPhoneAsDigits } from "@/app/format-service";

interface SearchFormProps {
  useCase: USE_CASES;
  queryValueSets: ValueSetItem[];
  setUseCase: (useCase: USE_CASES) => void;
  setOriginalRequest: (originalRequest: UseCaseQueryRequest) => void;
  setUseCaseQueryResponse: (UseCaseQueryResponse: UseCaseQueryResponse) => void;
  setMode: (mode: Mode) => void;
  setLoading: (loading: boolean) => void;
  setQueryType: (queryType: string) => void;
}

/**
 * @param root0 - SearchFormProps
 * @param root0.useCase - The use case this query will cover.
 * @param root0.queryValueSets - Stateful collection of valuesets to use in the query.
 * @param root0.setUseCase - Update stateful use case.
 * @param root0.setOriginalRequest - The function to set the original request.
 * @param root0.setUseCaseQueryResponse - The function to set the use case query response.
 * @param root0.setMode - The function to set the mode.
 * @param root0.setLoading - The function to set the loading state.
 * @param root0.setQueryType - The function to set the query type.
 * @returns - The SearchForm component.
 */
const SearchForm: React.FC<SearchFormProps> = ({
  useCase,
  queryValueSets,
  setUseCase,
  setOriginalRequest,
  setUseCaseQueryResponse,
  setMode,
  setLoading,
  setQueryType,
}) => {
  //Set the patient options based on the demoOption
  const [patientOption, setPatientOption] = useState<string>(
    patientOptions[useCase]?.[0]?.value || "",
  );
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<FHIR_SERVERS>();
  const [phone, setPhone] = useState<string>("");
  const [dob, setDOB] = useState<string>("");
  const [mrn, setMRN] = useState<string>("");

  const [showAdvanced, setShowAdvanced] = useState(false);
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
        setAutofilled(highlightAutofilled);
      }
    },
    [patientOption, setUseCase, setQueryType],
  );

  // Change the selectedDemoOption in the dropdown and update the
  // query type (which governs the DB fetch) accordingly
  const handleDemoQueryChange = (selectedDemoOption: string) => {
    setPatientOption(patientOptions[selectedDemoOption][0].value);
    setQueryType(
      demoQueryOptions.find((dqo) => dqo.value == selectedDemoOption)?.label ||
        "",
    );
  };

  const handleClick = () => {
    setMode("customize-queries");
  };

  async function HandleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!useCase || !fhirServer) {
      console.error("Use case and FHIR server are required.");
      return;
    }
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
    const queryResponse = await UseCaseQuery(originalRequest, queryValueSets);
    setUseCaseQueryResponse(queryResponse);

    if (queryResponse.Patient && queryResponse.Patient.length === 1) {
      setMode("results");
    } else {
      setMode("patient-results");
    }
    setLoading(false);
  }
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <>
      <form className="content-container-smaller-width" onSubmit={HandleSubmit}>
        <h1 className="font-sans-2xl text-bold margin-bottom-105">
          Search for a Patient
        </h1>
        <h2 className="font-sans-lg text-normal margin-top-0 margin-bottom-105">
          Enter patient information below to search for a patient. We will query
          the connected network to find matching records.{" "}
        </h2>
        {
          <div className={`usa-summary-box ${styles.demoQueryFiller}`}>
            <Label
              className="no-margin-top-important maxw-full font-sans text-normal"
              htmlFor="query"
            >
              The demo site uses synthetic data to provide examples of possible
              queries that you can make with the TEFCA Viewer. Select a query
              use case, a sample patient, and then click “fill fields” below.
            </Label>
            <div className={`${styles.demoQueryDropdownContainer}`}>
              <div>
                <Label htmlFor="query">Query</Label>
                <div className="display-flex flex-align-start query-page-wrapper">
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
                    <option value="" disabled>
                      {" "}
                      -- Select an Option --{" "}
                    </option>
                    {demoQueryOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <Label htmlFor="patient">Patient</Label>
                <div className="display-flex flex-align-start query-page-wrapper">
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
              </div>
            </div>

            <div className={`${styles.searchCallToActionContainer}`}>
              <Button
                className={`"usa-button" ${styles.searchCallToActionButton}`}
                type="button"
                onClick={() => {
                  fillFields(patientOption as PatientType, false);
                }}
              >
                Fill fields
              </Button>
              <Button
                type="button"
                className={`usa-button--outline bg-white ${styles.searchCallToActionButton}`}
                onClick={() => handleClick()}
              >
                Customize query
              </Button>
              <Button
                className={`usa-button--unstyled margin-left-auto ${styles.searchCallToActionButton}`}
                type="button"
                onClick={() => {
                  setShowAdvanced(!showAdvanced);
                }}
              >
                Advanced
              </Button>
            </div>
          </div>
        }
        <Fieldset className={`${styles.searchFormContainer}`}>
          {showAdvanced && (
            <div>
              <Label htmlFor="fhir_server">
                <b>FHIR Server (QHIN)</b>
              </Label>
              <div className="grid-row grid-gap">
                <div className="usa-combo-box">
                  <Select
                    id="fhir_server"
                    name="fhir_server"
                    value={fhirServer}
                    defaultValue={""}
                    onChange={(event) => {
                      setFhirServer(event.target.value as FHIR_SERVERS);
                    }}
                    required
                  >
                    <option value="" disabled>
                      {" "}
                      -- Select an Option --{" "}
                    </option>
                    {Object.keys(fhirServers).map((fhirServer: string) => (
                      <option key={fhirServer} value={fhirServer}>
                        {fhirServer}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>
            </div>
          )}
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
                  <option key={option.label} value={option.value}>
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
