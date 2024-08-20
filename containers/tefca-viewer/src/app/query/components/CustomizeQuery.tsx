"use client";

import React, { useState } from "react";
import { Accordion, Button, Icon, Checkbox } from "@trussworks/react-uswds";
import { Mode } from "../../constants";
import { AccordianSection, AccordianDiv } from "../component-utils";

interface Lab {
  code: string;
  display: string;
  system: string;
  include: boolean;
  author: string;
}

interface Medication {
  code: string;
  display: string;
  system: string;
  include: boolean;
  author: string;
}

interface Condition {
  code: string;
  display: string;
  system: string;
  include: boolean;
  author: string;
}

interface CustomizeQueryProps {
  queryType: string;
  labs: Lab[];
  medications: Medication[];
  conditions: Condition[];
  setMode: (mode: Mode) => void;
  goBack: () => void;
}

/**
 * CustomizeQuery component for displaying and customizing query details.
 * @param root0 - The properties object.
 * @param root0.queryType - The type of the query.
 * @param root0.labs - The list of lab tests.
 * @param root0.medications - The list of medications.
 * @param root0.conditions - The list of conditions.
 * @param root0.setMode - The function to set the mode.
 * @param root0.goBack - Back button to go from /customize to /query page.
 * @returns The CustomizeQuery component.
 */
const CustomizeQuery: React.FC<CustomizeQueryProps> = ({
  queryType,
  labs,
  medications,
  conditions,
  setMode,
  goBack,
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

  const handleIncludeAll = (
    setItems: React.Dispatch<React.SetStateAction<any[]>>,
    include: boolean,
  ) => {
    setItems((prevItems) => prevItems.map((item) => ({ ...item, include })));
  };

  const handleApplyChanges = () => {
    const selectedLabs = labsState.filter((lab) => lab.include);
    const selectedMedications = medicationsState.filter(
      (medication) => medication.include,
    );
    const selectedConditions = conditionsState.filter(
      (condition) => condition.include,
    );

    console.log("Selected Labs:", selectedLabs);
    console.log("Selected Medications:", selectedMedications);
    console.log("Selected Conditions:", selectedConditions);
  };

  const renderItems = (
    items: any[],
    setItems: React.Dispatch<React.SetStateAction<any[]>>,
  ) => (
    <div className="accordion-items">
      {items.map((item, index) => (
        <div key={index} className="accordion-item-row">
          <div className="accordion-item-cell">
            <Checkbox
              id={`checkbox-${index}`}
              name={`checkbox-${index}`}
              checked={item.include}
              onChange={(e) => {
                const updatedItems = [...items];
                updatedItems[index].include = e.target.checked;
                setItems(updatedItems);
              }}
              label={undefined}
            />
          </div>
          <div className="accordion-item-cell">{item.code}</div>
          <div className="accordion-item-cell">{item.display}</div>
        </div>
      ))}
    </div>
  );

  const renderAccordionItems = (
    items: any[],
    setItems: React.Dispatch<React.SetStateAction<any[]>>,
    title: string,
  ) => {
    const selectedCount = items.filter((item) => item.include).length;
    return items.length
      ? items.map((item, index) => ({
          id: `${title}-${index}`,
          title: (
            <div className="accordion-title">
              <div className="accordion-header">
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
                {`${item.display}`}
                <div>{`${selectedCount} selected`}</div>
              </div>
              <div className="accordion-subtitle">
                <strong>Author:</strong> {item.author} <strong>System:</strong>{" "}
                {item.system}
              </div>
            </div>
          ),
          content: (
            <>
              <AccordianSection>
                <AccordianDiv>
                  <div className="accordion-table-header">
                    <div className="accordion-header-cell">Include</div>
                    <div className="accordion-header-cell">Code</div>
                    <div className="accordion-header-cell">Display</div>
                  </div>
                  {renderItems(items, setItems)}
                </AccordianDiv>
              </AccordianSection>
            </>
          ),
          expanded: true,
          headingLevel: "h3" as "h3",
        }))
      : [];
  };

  const [labsState, setLabsState] = useState(labs);
  const [medicationsState, setMedicationsState] = useState(medications);
  const [conditionsState, setConditionsState] = useState(conditions);

  return (
    <div className="customize-query-container">
      <a
        href="#"
        onClick={goBack}
        className="text-bold"
        style={{ fontSize: "16px" }}
      >
        <Icon.ArrowBack /> Return to patient search
      </a>
      <h1 className="font-sans-2xl text-bold" style={{ paddingBottom: "0px" }}>
        Customize query
      </h1>
      <div
        className="font-sans-lg text-light"
        style={{ paddingBottom: "0px", paddingTop: "4px" }}
      >
        Query: {queryType}
      </div>
      <nav className="usa-nav custom-nav">
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
          <a href="#medications" onClick={() => handleTabChange("medications")}>
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
      </nav>
      <ul className="usa-nav__primary usa-accordion"></ul>
      <hr className="custom-hr"></hr>
      <a
        href="#"
        type="button"
        className="include-all-link"
        onClick={() => {
          if (activeTab === "labs") handleIncludeAll(setLabsState, true);
          if (activeTab === "medications")
            handleIncludeAll(setMedicationsState, true);
          if (activeTab === "conditions")
            handleIncludeAll(setConditionsState, true);
        }}
      >
        Include all {activeTab}
      </a>
      <div>
        {activeTab === "labs" && (
          <Accordion
            items={renderAccordionItems(labsState, setLabsState, "Labs")}
            multiselectable
            bordered
          />
        )}
        {activeTab === "medications" && (
          <Accordion
            items={renderAccordionItems(
              medicationsState,
              setMedicationsState,
              "Medications",
            )}
            multiselectable
          />
        )}
        {activeTab === "conditions" && (
          <Accordion
            items={renderAccordionItems(
              conditionsState,
              setConditionsState,
              "Conditions",
            )}
            multiselectable
          />
        )}
      </div>
      <div className="button-container">
        <Button type="button" onClick={handleApplyChanges}>
          Apply Changes
        </Button>
        <Button type="button" onClick={() => setMode("search")}>
          Cancel
        </Button>
      </div>
    </div>
  );
};

export default CustomizeQuery;
