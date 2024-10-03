"use client";
import React, { useState, useEffect } from "react";
import { Button, Label, Select } from "@trussworks/react-uswds";
import { demoQueryOptions, FHIR_SERVERS } from "../../constants";

interface SelectQueryProps {
  setQueryType: (queryType: string) => void;
  setHCO: (hco: string) => void;
  onSubmit: () => void; // Callback when the user submits the query
}

/**
 *
 * @param root0 - a
 * @param root0.setQueryType - b
 * @param root0.setHCO - c
 * @param root0.onSubmit -d
 * @returns - The selectQuery component.
 */
const SelectQuery: React.FC<SelectQueryProps> = ({
  setQueryType,
  setHCO,
  onSubmit,
}) => {
  const [selectedQuery, setSelectedQuery] = useState<string>("");
  const [selectedHCO, setSelectedHCO] = useState<FHIR_SERVERS>();

  // When query changes, update the parent component state
  useEffect(() => {
    setQueryType(selectedQuery);
  }, [selectedQuery, setQueryType]);

  // When HCO changes, update the parent component state
  useEffect(() => {
    setHCO(selectedHCO);
  }, [selectedHCO, setHCO]);

  const handleQueryChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedQuery(event.target.value);
  };

  const handleHCOChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedHCO(event.target.value);
  };

  const handleSubmit = () => {
    if (selectedQuery && selectedHCO) {
      onSubmit();
    } else {
      alert("Please select both a query and a healthcare organization.");
    }
  };

  return (
    <div className="select-query-container">
      <h2 className="font-sans-lg text-bold">Select a query</h2>

      <div className="usa-form-group">
        <Label htmlFor="querySelect">Query</Label>
        <Select
          id="querySelect"
          name="query"
          value={selectedQuery}
          onChange={handleQueryChange}
          required
        >
          <option value="" disabled>
            -- Select a Query --
          </option>
          {demoQueryOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      </div>

      <div className="usa-form-group">
        <Label htmlFor="hcoSelect">Health Care Organization (HCO)</Label>
        <Select
          id="hcoSelect"
          name="hco"
          value={selectedHCO}
          onChange={handleHCOChange}
          required
        >
          <option value="" disabled>
            -- Select an HCO --
          </option>
          {HCOOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      </div>

      <Button type="button" onClick={handleSubmit}>
        Submit
      </Button>
    </div>
  );
};

export default SelectQuery;
