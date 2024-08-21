"use client";

import React, { useMemo, useState } from "react";
import { Accordion, Button, Icon, Checkbox } from "@trussworks/react-uswds";
import { AccordianSection } from "../../query/component-utils";
import { Mode, ValueSet } from "../../constants";
import { AccordionItemProps } from "@trussworks/react-uswds/lib/components/Accordion/Accordion";
import { is } from "date-fns/locale";

interface CustomizeQueryProps {
  queryType: string;
  ValueSet: ValueSet;
  setMode: (mode: Mode) => void;
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
  const [isExpanded, setIsExpanded] = useState(true);

  /*Keeps track of whether the accordion is expanded to change the direction of the arrow*/
  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const handleTabChange = (tab: keyof ValueSet) => {
    setActiveTab(tab);
  };

  const handleSelectAllChange = (
    items: any[],
    setItems: React.Dispatch<React.SetStateAction<any[]>>,
    checked: boolean
  ) => {
    const updatedItems = items.map((item) => ({ ...item, include: checked }));
    setItems(updatedItems);
  };

  const handleIncludeAll = (
    setValueSet: React.Dispatch<React.SetStateAction<ValueSet>>,
    key: keyof ValueSet,
    include: boolean
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
  };

  const accordionItems: AccordionItemProps[] = useMemo(() => {
    const items = valueSetState[activeTab as keyof ValueSet];
    const selectedCount = items.filter((item) => item.include).length;
    return items.length
      ? [
          {
            title: (
              <div className="accordion-header display-flex flex-no-wrap flex-align-start">
                <Checkbox
                  id="select-all"
                  name="select-all"
                  className="hide-checkbox-label"
                  checked={selectedCount === items.length}
                  onChange={(e) =>
                    handleSelectAllChange(
                      items,
                      (updatedItems) =>
                        setValueSetState((prevState) => ({
                          ...prevState,
                          [activeTab]: updatedItems,
                        })),
                      e.target.checked
                    )
                  }
                  label={<span className="hide-me">Select/deselect all</span>}
                />
                <div>
                  {`${items[0].display}`}

                  <span className="accordion-subtitle margin-top-2">
                    <strong>Author:</strong> {items[0].author}{" "}
                    <strong>System:</strong> {items[0].system}
                  </span>
                </div>

                <span className="margin-left-auto">{`${selectedCount} selected`}</span>
                {/* <Icon.ExpandLess size={4} /> */}
                <div onClick={handleToggleExpand} style={{ cursor: "pointer" }}>
                  {isExpanded ? (
                    <Icon.ExpandLess size={4} />
                  ) : (
                    <Icon.ExpandMore size={4} />
                  )}
                </div>
              </div>
            ),
            id: items[0].author + ":" + items[0].system,
            className: "accordion-item",
            content: (
              <AccordianSection>
                <div className="customize-query-grid-container customize-query-table">
                  <div className="customize-query-grid-header">
                    <div>Include</div>
                    <div>Code</div>
                    <div>Display</div>
                  </div>
                  <div className="customize-query-grid-body">
                    {items.map((item, index) => (
                      <div
                        className="customize-query-grid-row customize-query-striped-row"
                        key={item.code}
                      >
                        <div>
                          <Checkbox
                            id={`checkbox-${index}`}
                            name={`checkbox-${index}`}
                            checked={item.include}
                            className="hide-checkbox-label"
                            onChange={(e) => {
                              const updatedItems = [...items];
                              updatedItems[index].include = e.target.checked;
                              setValueSetState((prevState) => ({
                                ...prevState,
                                [activeTab]: updatedItems,
                              }));
                            }}
                            label={<span className="hide-me">Include</span>}
                          />
                        </div>
                        <div>{item.code}</div>
                        <div>{item.display}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </AccordianSection>
            ),
            expanded: true,
            headingLevel: "h3",
          },
        ]
      : [];
  }, [valueSetState, activeTab, isExpanded]);

  return (
    <div className="customize-query-container">
      <a
        href="#"
        onClick={() => setMode("search")}
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
          <a href="#medications" onClick={() => handleTabChange("medications")}>
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
      </nav>
      <ul className="usa-nav__primary usa-accordion"></ul>
      <hr className="custom-hr"></hr>
      <a
        href="#"
        type="button"
        className="include-all-link"
        onClick={() =>
          handleIncludeAll(setValueSetState, activeTab as keyof ValueSet, true)
        }
      >
        Include all {activeTab}
      </a>
      <div>
        <Accordion items={accordionItems} multiselectable bordered />
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
