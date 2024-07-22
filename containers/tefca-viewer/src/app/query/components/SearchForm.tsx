import React, { useCallback, useEffect, useState } from "react";
import {
  Fieldset,
  Label,
  TextInput,
  Select,
  Button,
  Alert,
} from "@trussworks/react-uswds";
import { fhirServers } from "../../fhir-servers";
import {
  USE_CASES,
  FHIR_SERVERS,
  demoData,
  demoDataUseCase,
} from "../../constants";
import {
  UseCaseQueryResponse,
  UseCaseQuery,
  UseCaseQueryRequest,
} from "../../query-service";
import { Mode } from "../page";

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
  const [demoOption, setDemoOption] = useState<string>("demo-cancer");
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<FHIR_SERVERS>();
  const [phone, setPhone] = useState<string>("");
  const [dob, setDOB] = useState<string>("");
  const [mrn, setMRN] = useState<string>("");
  const [useCase, setUseCase] = useState<USE_CASES>();
  const [autofilled, setAutofilled] = useState(false); // boolean indicating if the form was autofilled, changes color if true

  // Fill the fields with the demo data if selected
  const fillFields = useCallback(() => {
    const data = demoData[demoOption as demoDataUseCase];
    if (data) {
      setAutofilled(true);
      setFirstName(data.FirstName);
      setLastName(data.LastName);
      setDOB(data.DOB);
      setMRN(data.MRN);
      setPhone(data.Phone);
      setFhirServer(data.FhirServer as FHIR_SERVERS);
      setUseCase(data.UseCase as USE_CASES);
    }
  }, [demoOption]);

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
        <h4 className="font-sans-md text-normal margin-top-0">
          Please enter <b>3 out of 5 of the following sections</b> <br></br>for
          a given patient, in addition to a case investigation topic.
        </h4>
        <div className="usa-summary-box usa-summary-box demo-data-filler">
          <label className="usa-label" htmlFor="demo-data">
            Select from the following use cases to "pre-fill" patient
            information below:
          </label>
          <div className="display-flex flex-align-center margin-top-2">
            <div className="usa-combo-box flex-1" data-enhanced="true">
              <select
                id="demo-data"
                name="demo-data"
                className="usa-select margin-top-0"
                value={demoOption}
                onChange={(event) => {
                  setDemoOption(event.target.value);
                }}
              >
                <option value="demo-cancer">
                  A demo patient with a cancer use case
                </option>
                <option value="demo-sti-chlamydia">
                  A demo patient with a chlamydia use case
                </option>
                <option value="demo-sti-gonorrhea">
                  A demo patient with a gonorrhea use case
                </option>
                <option value="demo-newborn-screening">
                  A demo patient with a newborn screening use case
                </option>
                <option value="demo-social-determinants">
                  A demo patient with a social determinants of health use case
                </option>
                <option value="demo-sti-syphilis">
                  A demo patient with a syphilis use case
                </option>
              </select>
            </div>
            <Button
              className="margin-left-1 usa-button--outline bg-white"
              type="button"
              onClick={() => {
                fillFields();
              }}
            >
              Fill fields
            </Button>
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
                <option value="UM">
                  UM - United States Minor Outlying Islands
                </option>
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
                      | "cancer",
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
