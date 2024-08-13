"use client";

import React, { useState } from "react";
import { Accordion, Button, Icon, Checkbox } from "@trussworks/react-uswds";
import { AccordianSection, AccordianDiv } from "../component-utils";
import { ValueSet } from "../../constants";

interface CustomizeQueryProps {
  queryType: string;
  ValueSet: ValueSet;
  setMode: (mode: string) => void;
}

/**
 * CustomizeQuery component for displaying and customizing query details.
 * @param root0 - The properties object.
 * @param root0.queryType - The type of the query.
 * @param root0.ValueSet - The value set of labs, conditions, and medications.
 * @param root0.setMode - The function to set the mode.
 * @returns The CustomizeQuery component.
 */
const CustomizeQuery: React.FC<CustomizeQueryProps> = ({
  queryType,
  ValueSet,
  setMode,
}) => {
  const [activeTab, setActiveTab] = useState("labs");

  const [valueSetState, setValueSetState] = useState<ValueSet>(ValueSet);

  const handleTabChange = (tab: keyof ValueSet) => {
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
    setValueSet: React.Dispatch<React.SetStateAction<ValueSet>>,
    key: keyof ValueSet,
    include: boolean,
  ) => {
    setValueSet((prevValueSet) => ({
      ...prevValueSet,
      [key]: prevValueSet[key].map((item) => ({ ...item, include })),
    }));
  };

  const handleApplyChanges = () => {
    const selectedItems = Object.keys(valueSetState).reduce((acc, key) => {
      const items = valueSetState[key as keyof ValueSet];
      acc[key as keyof ValueSet] = items.filter((item) => item.include);
      return acc;
    }, {} as ValueSet);

    console.log(selectedItems);
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
      ? [
          {
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
                  {`${items[0].display}`}
                  <div>{`${selectedCount} selected`}</div>
                </div>
                <div className="accordion-subtitle">
                  <strong>Author:</strong> {items[0].author}{" "}
                  <strong>System:</strong> {items[0].system}
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
            headingLevel: "h3",
          },
        ]
      : [];
  };

  return (
    <div className="customize-query-container">
      <a href="#" onClick={() => setMode("search")} className="text-bold">
        <Icon.ArrowBack /> Return to patient search
      </a>
      <h1 className="font-sans-2xl text-bold">Customize query</h1>
      <p className="font-sans-lg text-light">Query: {queryType}</p>
      <nav className="usa-nav custom-nav">
        <ul className="usa-nav__primary usa-accordion">
          <li
            className={`usa-nav__primary-item ${
              activeTab === "labs" ? "usa-current" : ""
            }`}
          >
            <a href="#labs" onClick={() => handleTabChange("labs")}>
              Labs
            </a>
          </li>
          <li
            className={`usa-nav__primary-item ${
              activeTab === "medications" ? "usa-current" : ""
            }`}
          >
            <a
              href="#medications"
              onClick={() => handleTabChange("medications")}
            >
              Medications
            </a>
          </li>
          <li
            className={`usa-nav__primary-item ${
              activeTab === "conditions" ? "usa-current" : ""
            }`}
          >
            <a href="#conditions" onClick={() => handleTabChange("conditions")}>
              Conditions
            </a>
          </li>
        </ul>
      </nav>
      <a
        href="#"
        type="button"
        style={{ fontSize: "16px", fontFamily: "Public Sans" }}
        onClick={() =>
          handleIncludeAll(setValueSetState, activeTab as keyof ValueSet, true)
        }
      >
        Include all {activeTab}
      </a>
      <div>
        <Accordion
          items={renderAccordionItems(
            valueSetState[activeTab as keyof ValueSet],
            (updatedItems) =>
              setValueSetState((prevState) => ({
                ...prevState,
                [activeTab]: updatedItems,
              })),
            activeTab.charAt(0).toUpperCase() + activeTab.slice(1),
          )}
          multiselectable
          bordered
        />
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
