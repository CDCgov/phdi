"use client";
import React, { useState, useEffect } from "react";
import { Button, Select } from "@trussworks/react-uswds";
import { demoQueryOptions, FHIR_SERVERS, Mode } from "../../../constants";
import Backlink from "../backLink/Backlink";
import { fhirServers } from "../../../fhir-servers";
import styles from "./selectQuery.module.css";

interface SelectQueryProps {
  setQueryType: (queryType: string) => void;
  setHCO: (hco: string) => void;
  setMode: (mode: Mode) => void;
  onSubmit: () => void; // Callback when the user submits the query
  goBack: () => void;
}

/**
 *
 * @param root0 - SelectQueryProps
 * @param root0.setQueryType - Callback to update the query type
 * @param root0.setHCO - Callback to update selected Health Care Organization (HCO)
 * @param root0.setMode - Callback to switch mode
 * @param root0.onSubmit - Callback for submit action
 * @param root0.goBack - back button
 * @returns - The selectQuery component.
 */
const SelectQuery: React.FC<SelectQueryProps> = ({
  setQueryType,
  setHCO,
  setMode,
  onSubmit,
  goBack,
}) => {
  const [selectedQuery, setSelectedQuery] = useState<string>("");
  const [selectedHCO, setSelectedHCO] = useState<string>(""); // Keep this as string for HCO selection
  const [showAdvanced, setShowAdvanced] = useState(false);

  // When query changes, update the parent component state
  useEffect(() => {
    setQueryType(selectedQuery);
  }, [selectedQuery, setQueryType]);

  const handleQueryChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedQuery(event.target.value);
  };

  const handleHCOChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedHCO(event.target.value);
    setHCO(event.target.value as FHIR_SERVERS); // Update parent component state
  };

  // Link to go to customize-queries page
  const handleClick = () => {
    setMode("customize-queries");
  };

  // Submit and go to results; if no custom query selected, add alert
  const handleSubmit = () => {
    if (selectedQuery) {
      onSubmit();
    } else {
      alert("Please select a query.");
    }
  };

  return (
    <form className="content-container-smaller-width">
      {/* Back button */}
      <div className="text-bold">
        <Backlink onClick={goBack} label={RETURN_TO_STEP_ONE_LABEL} />
      </div>
      <h1 className={`${styles.selectQueryHeaderText}`}>
        Step 3: Select a query
      </h1>
      <div
        className={`font-sans-md text-light ${styles.selectQueryExplanationText}`}
      >
        We will request all data related to your selected patient and query. By
        only showing relevant data for your query, we decrease the burden on our
        systems and protect patient privacy. If you would like to customize the
        query response, click on the "customize query" button.
      </div>
      <h3 className="margin-bottom-3">Query</h3>
      <div className={styles.queryRow}>
        {/* Select a query drop down */}
        <Select
          id="querySelect"
          name="query"
          value={selectedQuery}
          onChange={handleQueryChange}
          className={`${styles.queryDropDown}`}
          required
        >
          <option value="" disabled>
            Select query
          </option>
          {demoQueryOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
        {/* Customize query button */}
        <Button
          type="button"
          className={`usa-button--outline bg-white ${styles.customizeButton}`}
          onClick={handleClick}
        >
          Customize query
        </Button>
      </div>

      {/* Show Advanced options only when `showAdvanced` is true */}
      {showAdvanced && (
        <div>
          <h3 className="margin-bottom-3">Health Care Organization (HCO)</h3>
          <Select
            id="fhir_server"
            name="fhir_server"
            value={selectedHCO} // Use selectedHCO for the selected value
            onChange={handleHCOChange}
            required
            defaultValue=""
            className={`${styles.queryDropDown}`}
          >
            <option value="" disabled>
              Select HCO
            </option>
            {Object.keys(fhirServers).map((fhirServer: string) => (
              <option key={fhirServer} value={fhirServer}>
                {fhirServer}
              </option>
            ))}
          </Select>
        </div>
      )}

      {/* Only show the "Advanced" button if `showAdvanced` is false */}
      {!showAdvanced && (
        <div>
          <Button
            className={`usa-button--unstyled margin-left-auto ${styles.searchCallToActionButton}`}
            type="button"
            onClick={() => setShowAdvanced(true)}
          >
            Advanced...
          </Button>
        </div>
      )}

      {/* Submit Button */}
      <div className="padding-top-6">
        <Button
          type="button"
          disabled={!selectedQuery}
          className={selectedQuery ? "usa-button" : "usa-button disabled"}
          onClick={handleSubmit}
        >
          Submit
        </Button>
      </div>
    </form>
  );
};

export default SelectQuery;
export const RETURN_TO_STEP_ONE_LABEL = "Return to Select patient";
