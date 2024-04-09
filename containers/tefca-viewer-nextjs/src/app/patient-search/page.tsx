"use client";
import React, { useState } from "react";
import { Fieldset, Label, TextInput, DatePicker, Select } from "@trussworks/react-uswds";

const PatientSearch: React.FC = () => {
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [fhirServer, setFhirServer] = useState<string>("");

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    console.log("First Name:", firstName);
    console.log("Last Name:", lastName);
    console.log("FHIR Server:", fhirServer);
  };

  return (
    <div>
      <form className="patient-search-form" onSubmit={handleSubmit}>
      <h1 className="font-sans-2xl text-bold">Search for a Patient</h1>
          <Fieldset>
              <h2 className="font-sans-lg search-form-section-label"><strong>Name</strong></h2>
              <div className="grid-row grid-gap">
                  <div className="tablet:grid-col-6">
                      <Label htmlFor="first_name">First Name</Label>
                      <TextInput id="first_name" name="first_name" type="text" pattern="^[A-Za-z]+$"/>
                  </div>
                  <div className="tablet:grid-col-6">
                      <Label htmlFor="last_name">Last Name</Label>
                      <TextInput id="last_name" name="last_name" type="text" pattern="^[A-Za-z]+$"/>
                  </div>
              </div>
              <h2 className="font-sans-lg search-form-section-label"><strong>Phone Number</strong></h2>
              <div className="grid-row grid-gap">
                  <div className="grid-col-6">
                      <Label htmlFor="phone">Phone Number</Label>
                      <TextInput id="phone" name="phone" type="tel"/>
                  </div>
              </div>
              <h2 className="font-sans-lg search-form-section-label"><strong>Date of Birth</strong></h2>
              <div className="grid-row grid-gap">
                  <div className="grid-col-6">
                      <Label htmlFor="dob">Date of Birth</Label>
                      <DatePicker id="dob" name="dob"/>
                  </div>
              </div>
              <h2 className="font-sans-lg search-form-section-label"><strong>Address</strong></h2>
              <div className="grid-row grid-gap">
                  <div className="grid-col">
                      <Label htmlFor="street_address_1">Street address</Label>
                      <TextInput id="street_address_1" name="street_address_1" type="tel"/>
                  </div>
              </div>
              <div className="grid-row grid-gap">
                  <div className="grid-col">
                      <Label htmlFor="street_address_2">Address Line 2</Label>
                      <TextInput id="street_address_2" name="street_address_2" type="text"/>
                  </div>
              </div>
              <div className="grid-row grid-gap">
                  <div className="tablet:grid-col-5">
                      <Label htmlFor="city">City</Label>
                      <TextInput id="city" name="city" type="text"/>
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
                      <TextInput className="usa-input usa-input--medium" id="zip" name="zip" type="text" pattern="[\d]{5}(-[\d]{4})?"/>
                  </div>
              </div>
              <h2 className="font-sans-lg search-form-section-label"><strong>Medical Record Number (MRN)</strong></h2>
              <div className="grid-row grid-gap">
                  <div className="grid-col-6">
                      <Label htmlFor="mrn">Medical Record Number</Label>
                      <TextInput id="mrn" name="mrn" type="number" pattern="^\d+$"/>
                  </div>
              </div>
              <h2 className="font-sans-lg search-form-section-label"><strong>Case investigation topic</strong></h2>
              <div className="grid-row grid-gap">
                  <div className="grid-col-7">
                      <Label htmlFor="use_case">Use case</Label>
                      <Select id="use_case" name="use_case">
                          <option value="" disabled selected></option>
                          <option value="newborn-screening">Newborn Screening</option>
                          <option value="syphilis">Syphilis</option>
                          <option value="cancer">Cancer</option>
                          <option value="sdoh">Social Determinants of Health</option>
                      </Select>
                  </div>
                </div>
              <h2 className="font-sans-lg search-form-section-label"><strong>FHIR Server (QHIN)</strong></h2>
              <div className="grid-row grid-gap">
                  <div className="grid-col-5">
                      <Label htmlFor="fhir_server">FHIR Server</Label>
                      <Select id="fhir_server" name="fhir_server">
                          <option value="" disabled selected></option>
                          <option value="meld">Meld</option> 
                          <option value="ehx">eHealth Exchange</option>
                      </Select>
                  </div>
                  </div>
          </Fieldset>
          <button className="usa-button patient-search-button" type="submit">Search for patient</button>
      </form>
    </div>
  );
};

export default PatientSearch;
