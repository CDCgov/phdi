import React, { useEffect, useState } from "react";
import {
  Fieldset,
  Label,
  TextInput,
  Select,
  Alert,
} from "@trussworks/react-uswds";
import { fhirServers } from "../../fhir-servers";
import {
  USE_CASES,
  FHIR_SERVERS,
  demoData,
  demoDataUseCase,
  demoQueryOptions,
  patientOptions,
  stateOptions,
} from "../../constants";
import {
  UseCaseQueryResponse,
  UseCaseQuery,
  UseCaseQueryRequest,
} from "../../query-service";
import { Mode } from "../page";
import { useSearchParams } from "next/navigation";

interface SearchFormProps {
  setOriginalRequest: (originalRequest: UseCaseQueryRequest) => void;
  setUseCaseQueryResponse: (UseCaseQueryResponse: UseCaseQueryResponse) => void;
  setMode: (mode: Mode) => void;
  setLoading: (loading: boolean) => void;
}

/**
 * @param root0 - SearchFormProps
 * @param root0.setOriginalRequest - The function to set the original request.
 * @param root0.setUseCaseQueryResponse - The function to set the use case query response.
 * @param root0.setMode - The function to set the mode.
 * @param root0.setLoading - The function to set the loading state.
 * @returns - The SearchForm component.
 */
const SearchForm: React.FC<SearchFormProps> = ({
  setOriginalRequest,
  setUseCaseQueryResponse,
  setMode,
  setLoading,
}) => {
  const params = useSearchParams();
  useEffect(() => console.log("params", params), [params]);

  // Get the demoOption (initial selection) selected from modal via the URL
  const [demoOption, setDemoOption] = useState<string>(
    params.get("useCase") || "demo-cancer"
  );

  //Set the patient options based on the demoOption
  const [patientOption, setPatientOption] = useState<string>(
    patientOptions[demoOption]?.[0]?.value || ""
  );
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<FHIR_SERVERS>();
  const [phone, setPhone] = useState<string>("");
  const [dob, setDOB] = useState<string>("");
  const [mrn, setMRN] = useState<string>("");
  const [useCase, setUseCase] = useState<USE_CASES>();
  const [autofilled, setAutofilled] = useState(false); // boolean indicating if the form was autofilled, changes color if true

  // Fills fields if patientOption changes
  useEffect(() => {
    if (!patientOption) {
      return;
    }
    const data = demoData[patientOption as demoDataUseCase];
    if (data) {
      setDemoOption(demoOption);
      setAutofilled(true);
      setFirstName(data.FirstName);
      setLastName(data.LastName);
      setDOB(data.DOB);
      setMRN(data.MRN);
      setPhone(data.Phone);
      setFhirServer(data.FhirServer as FHIR_SERVERS);
      setUseCase(data.UseCase as USE_CASES);
    }
  }, [demoOption, patientOption]);

  // Change the selectedDemoOption (the option selected once you are past the modal) and set the patientOption to the first patientOption for the selectedDemoOption
  const handleDemoQueryChange = (selectedDemoOption: string) => {
    setDemoOption(selectedDemoOption);
    setPatientOption(patientOptions[selectedDemoOption][0].value);
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
      <Alert type="info" headingLevel="h4" slim className="custom-alert">
        This site is for demo purposes only. Please do not enter PII on this
        website.
      </Alert>
      <form className="patient-search-form" onSubmit={HandleSubmit}>
        <h1 className="font-sans-2xl text-bold">Search for a Patient</h1>
        <h2 className="font-sans-lg search-form-section-label">
          <strong>Case investigation topic</strong>
        </h2>
        <div className="grid-row grid-gap">
          <div className="grid-col-7">
            <Label htmlFor="use_case">Use case</Label>
            <Select
              id="use_case"
              name="use_case"
              value={useCase}
              onChange={(event) => {
                setUseCase(
                  event.target.value as
                    | "social-determinants"
                    | "newborn-screening"
                    | "syphilis"
                    | "cancer"
                );
              }}
              // style={{
              //   backgroundColor: autofilled ? autofillColor : undefined,
              // }}
              required
              defaultValue=""
            >
              <option value="" disabled>
                Select Use Case
              </option>
              <option value="cancer">Cancer</option>
              <option value="chlamydia">Chlamydia</option>
              <option value="gonorrhea">Gonorrhea</option>
              <option value="newborn-screening">Newborn Screening</option>
              <option value="social-determinants">
                Social Determinants of Health
              </option>
              <option value="syphilis">Syphilis</option>
            </Select>
          </div>
        </div>
        <h2 className="font-sans-lg search-form-section-label">
          <strong>FHIR Server (QHIN)</strong>
        </h2>
        <div className="grid-row grid-gap">
          <div className="grid-col-5">
            <Label htmlFor="fhir_server">FHIR Server</Label>
            <Select
              id="fhir_server"
              name="fhir_server"
              value={fhirServer}
              onChange={(event) => {
                setFhirServer(event.target.value as FHIR_SERVERS);
              }}
              // style={{
              //   backgroundColor: autofilled ? autofillColor : undefined,
              // }}
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
        <div className="usa-summary-box usa-summary-box demo-query-filler">
          <Label className="usa-label" htmlFor="demo-query">
            <b>Select a patient type to populate the form with sample data.</b>
          </Label>
          <div className="display-flex flex-align-start">
            <div className="usa-combo-box flex-1" data-enhanced="true">
              <Label htmlFor="demo-patient">Patient</Label>
              <select
                id="demo-patient"
                name="demo-patient"
                className="usa-select margin-top-1"
                value={patientOption}
                onChange={(event) => {
                  setPatientOption(event.target.value);
                }}
              >
                {patientOptions[demoOption]?.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            {/* <Button
              className="margin-left-1  margin-top-1 usa-button--outline bg-white"
              type="button"
              onClick={() => {}} // TODO: Link to customize query page
            >
              Customize queries
            </Button> */}
          </div>
        </div>
        <Fieldset>
          <h2 className="font-sans-lg search-form-section-label">
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
                  backgroundColor: autofilled ? autofillColor : undefined,
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
                  backgroundColor: autofilled ? autofillColor : undefined,
                }}
              />
            </div>
          </div>
          <h2 className="font-sans-lg search-form-section-label">
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
                  backgroundColor: autofilled ? autofillColor : undefined,
                }}
              />
            </div>
          </div>
          <div>
            <h2 className="font-sans-lg search-form-section-label">
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
                      backgroundColor: autofilled ? autofillColor : undefined,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
          <h2 className="font-sans-lg search-form-section-label">
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
          <h2 className="font-sans-lg search-form-section-label">
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
                  backgroundColor: autofilled ? autofillColor : undefined,
                }}
              />
            </div>
          </div>
          {/* <h2 className="font-sans-lg search-form-section-label">
            <strong>Case investigation topic</strong>
          </h2>
          <div className="grid-row grid-gap">
            <div className="grid-col-7">
              <Label htmlFor="use_case">Use case</Label>
              <Select
                id="use_case"
                name="use_case"
                value={useCase}
                onChange={(event) => {
                  setUseCase(
                    event.target.value as
                      | "social-determinants"
                      | "newborn-screening"
                      | "syphilis"
                      | "cancer"
                  );
                }}
                style={{
                  backgroundColor: autofilled ? autofillColor : undefined,
                }}
                required
                defaultValue=""
              >
                <option value="" disabled>
                  Select Use Case
                </option>
                <option value="cancer">Cancer</option>
                <option value="chlamydia">Chlamydia</option>
                <option value="gonorrhea">Gonorrhea</option>
                <option value="newborn-screening">Newborn Screening</option>
                <option value="social-determinants">
                  Social Determinants of Health
                </option>
                <option value="syphilis">Syphilis</option>
              </Select>
            </div>
          </div>
          <h2 className="font-sans-lg search-form-section-label">
            <strong>FHIR Server (QHIN)</strong>
          </h2>
          <div className="grid-row grid-gap">
            <div className="grid-col-5">
              <Label htmlFor="fhir_server">FHIR Server</Label>
              <Select
                id="fhir_server"
                name="fhir_server"
                value={fhirServer}
                onChange={(event) => {
                  setFhirServer(event.target.value as FHIR_SERVERS);
                }}
                style={{
                  backgroundColor: autofilled ? autofillColor : undefined,
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
          </div> */}
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
