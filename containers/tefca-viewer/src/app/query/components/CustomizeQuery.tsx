"use client";

import React, { useState } from "react";
import { Accordion, Table, Icon, Checkbox } from "@trussworks/react-uswds";
import { Mode } from "../page";

interface Lab {
  code: string;
  display: string;
  system: string;
  include: boolean;
}

interface Medication {
  code: string;
  display: string;
  system: string;
  include: boolean;
}

interface Condition {
  code: string;
  display: string;
  system: string;
  include: boolean;
}

interface CustomizeQueryProps {
  queryType: string;
  labs: Lab[];
  medications: Medication[];
  conditions: Condition[];
  setMode: (mode: Mode) => void;
}

/**
 * CustomizeQuery component for displaying and customizing query details.
 * @param root0 - The properties object.
 * @param root0.queryType - The type of the query.
 * @param root0.labs - The list of lab tests.
 * @param root0.medications - The list of medications.
 * @param root0.conditions - The list of conditions.
 * @param root0.setMode - The function to set the mode.
 * @returns The CustomizeQuery component.
 */
const CustomizeQuery: React.FC<CustomizeQueryProps> = ({
  queryType,
  labs,
  medications,
  conditions,
  setMode,
}) => {
  const [activeTab, setActiveTab] = useState("labs");

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
  };

  const handleSelectAllChange = (
    items: any[],
    setItems: React.Dispatch<React.SetStateAction<any[]>>,
    checked: boolean,
  ) => {
    const updatedItems = items.map((item) => ({ ...item, include: checked }));
    setItems(updatedItems);
  };

  const renderAccordionItems = (
    items: any[],
    setItems: React.Dispatch<React.SetStateAction<any[]>>,
  ) => {
    const selectedCount = items.filter((item) => item.include).length;
    return items.length
      ? [
          {
            title: (
              <div className="accordion-title">
                {`${selectedCount} selected `}
                <Checkbox
                  id="select-all"
                  name="select-all"
                  className="custom-checkbox"
                  checked={selectedCount === items.length}
                  onChange={(e) =>
                    handleSelectAllChange(items, setItems, e.target.checked)
                  }
                  label={undefined}
                />
              </div>
            ),
            content: (
              <Table bordered>
                <thead>
                  <tr>
                    <th>Include</th>
                    <th>Code</th>
                    <th>Display</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, index) => (
                    <tr key={index}>
                      <td>
                        <Checkbox
                          id={`checkbox-${index}`}
                          name={`checkbox-${index}`}
                          className="custom-checkbox"
                          checked={item.include}
                          onChange={(e) => {
                            const updatedItems = [...items];
                            updatedItems[index].include = e.target.checked;
                            setItems(updatedItems);
                          }}
                          label={undefined}
                        />
                      </td>
                      <td>{item.code}</td>
                      <td>{item.display}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            ),
            expanded: true,
            headingLevel: "h3",
          },
        ]
      : [];
  };

  const [labsState, setLabsState] = useState(labs);
  const [medicationsState, setMedicationsState] = useState(medications);
  const [conditionsState, setConditionsState] = useState(conditions);

  return (
    <div className="customize-query-container">
      <a href="#" onClick={() => setMode("search")} className="text-bold">
        <Icon.ArrowBack /> Return to patient search
      </a>
      <h1 className="font-sans-2xl text-bold">Customize query</h1>
      <p className="font-sans-lg text-light">Query: {queryType}</p>
      <nav className="usa-nav">
        <ul className="usa-nav__primary usa-accordion">
          <li
            className={`usa-nav__primary-item ${activeTab === "labs" ? "usa-current" : ""}`}
          >
            <a href="#labs" onClick={() => handleTabChange("labs")}>
              Labs
            </a>
          </li>
          <li
            className={`usa-nav__primary-item ${activeTab === "medications" ? "usa-current" : ""}`}
          >
            <a
              href="#medications"
              onClick={() => handleTabChange("medications")}
            >
              Medications
            </a>
          </li>
          <li
            className={`usa-nav__primary-item ${activeTab === "conditions" ? "usa-current" : ""}`}
          >
            <a href="#conditions" onClick={() => handleTabChange("conditions")}>
              Conditions
            </a>
          </li>
        </ul>
      </nav>
      <hr />
      <div>
        {activeTab === "labs" && (
          <Accordion
            items={renderAccordionItems(labsState, setLabsState)}
            multiselectable
          />
        )}
        {activeTab === "medications" && (
          <Accordion
            items={renderAccordionItems(medicationsState, setMedicationsState)}
            multiselectable
          />
        )}
        {activeTab === "conditions" && (
          <Accordion
            items={renderAccordionItems(conditionsState, setConditionsState)}
            multiselectable
          />
        )}
      </div>
    </div>
  );
};

export default CustomizeQuery;
