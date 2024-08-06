"use client";

import React, { useState } from "react";
import { Accordion, Table, Icon } from "@trussworks/react-uswds";
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

  const renderAccordionItems = (items: any[]) => {
    return items.length
      ? [
          {
            title: `${items.length} selected`,
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
                        <input
                          type="checkbox"
                          checked={item.include}
                          readOnly
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

  return (
    <div>
      <a href="#" onClick={() => setMode("search")} className="text-bold">
        <Icon.ArrowBack /> Return to patient search
      </a>
      <h1 className="font-sans-2xl text-bold">Customize query</h1>
      <p className="font-sans-lg text-light">Query:</p>
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
      <div>
        {activeTab === "labs" && (
          <Accordion items={renderAccordionItems(labs)} multiselectable />
        )}
        {activeTab === "medications" && (
          <Accordion
            items={renderAccordionItems(medications)}
            multiselectable
          />
        )}
        {activeTab === "conditions" && (
          <Accordion items={renderAccordionItems(conditions)} multiselectable />
        )}
      </div>
    </div>
  );
};

export default CustomizeQuery;
