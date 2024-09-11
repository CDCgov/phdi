"use client";

import React, { useMemo, useState, useEffect } from "react";
import { Accordion, Button, Icon } from "@trussworks/react-uswds";
import { AccordianSection } from "../../query/component-utils";
import { ValueSetItem } from "../../constants";
import { AccordionItemProps } from "@trussworks/react-uswds/lib/components/Accordion/Accordion";
import {
  getSavedQueryByName,
  filterQueryRows,
  mapQueryRowsToValueSetItems,
} from "@/app/database-service";
import { UseCaseQueryResponse } from "@/app/query-service";
import LoadingView from "./LoadingView";
import { showRedirectConfirmation } from "./RedirectionToast";

interface CustomizeQueryProps {
  useCaseQueryResponse: UseCaseQueryResponse;
  queryType: string;
  queryName: string;
  goBack: () => void;
}

/**
 * CustomizeQuery component for displaying and customizing query details.
 * @param root0 - The properties object.
 * @param root0.useCaseQueryResponse - The response from the query service.
 * @param root0.queryType - The type of the query.
 * @param root0.queryName - The name of the query to customize.
 * @param root0.goBack - Back button to go from "customize-queries" to "search" component.
 * @returns The CustomizeQuery component.
 */
const CustomizeQuery: React.FC<CustomizeQueryProps> = ({
  useCaseQueryResponse,
  queryType,
  queryName,
  goBack,
}) => {
  const [activeTab, setActiveTab] = useState("labs");

  const [groupedValueSetState, setGroupedValueSetState] = useState<{
    labs: { author: string; system: string; items: ValueSetItem[] }[];
    medications: { author: string; system: string; items: ValueSetItem[] }[];
    conditions: { author: string; system: string; items: ValueSetItem[] }[];
  }>({
    labs: [],
    medications: [],
    conditions: [],
  });
  const [isExpanded, setIsExpanded] = useState(true);

  // Keeps track of whether the accordion is expanded to change the direction of the arrow
  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  // Keeps track of which side nav tab to display to users
  const handleTabChange = (tab: keyof typeof groupedValueSetState) => {
    setActiveTab(tab);
  };

  // Handles the toggle of the 'include' state for individual items
  const toggleInclude = (groupIndex: number, itemIndex: number) => {
    const updatedGroups = [
      ...groupedValueSetState[activeTab as keyof typeof groupedValueSetState],
    ];
    const updatedItems = [...updatedGroups[groupIndex].items]; // Clone the current group items
    updatedItems[itemIndex] = {
      ...updatedItems[itemIndex],
      include: !updatedItems[itemIndex].include, // Toggle the include state
    };

    updatedGroups[groupIndex] = {
      ...updatedGroups[groupIndex],
      items: updatedItems, // Update the group's items
    };

    setGroupedValueSetState((prevState) => ({
      ...prevState,
      [activeTab]: updatedGroups, // Update the state with the new group
    }));
  };

  // Allows all items to be selected within an accordion section
  // Allows all items to be selected within all accordion sections of the active tab
  const handleSelectAllChange = (checked: boolean) => {
    const updatedGroups = groupedValueSetState[
      activeTab as keyof typeof groupedValueSetState
    ].map((group) => {
      const updatedItems = group.items.map((item) => ({
        ...item,
        include: checked, // Set all items to checked or unchecked
      }));
      return {
        ...group,
        items: updatedItems, // Update the group's items
      };
    });

    setGroupedValueSetState((prevState) => ({
      ...prevState,
      [activeTab]: updatedGroups, // Update the state for the current tab
    }));
  };

  // Will eventually be the json object storing the parsed data to return on the results page
  const handleApplyChanges = () => {
    const selectedItems = Object.keys(groupedValueSetState).reduce(
      (acc, key) => {
        const items =
          groupedValueSetState[key as keyof typeof groupedValueSetState];
        // Flatten groups to extract items and filter them
        acc[key as keyof typeof groupedValueSetState] = items
          .flatMap((group) => group.items) // Extract items from each group
          .filter((item) => item.include); // Filter included items only
        return acc;
      },
      {} as Record<string, ValueSetItem[]>,
    ); // Ensure type is correct for the flattened data

    goBack();
    showRedirectConfirmation({
      heading: QUERY_CUSTOMIZATION_CONFIRMATION_HEADER,
      body: QUERY_CUSTOMIZATION_CONFIRMATION_BODY,
      headingLevel: "h4",
    });
  };

  useEffect(() => {
    // Gate whether we actually update state after fetching so we
    // avoid name-change race conditions
    let isSubscribed = true;

    const fetchQuery = async () => {
      const queryResults = await getSavedQueryByName(queryName);
      const labs = await mapQueryRowsToValueSetItems(
        await filterQueryRows(queryResults, "labs"),
      );
      const meds = await mapQueryRowsToValueSetItems(
        await filterQueryRows(queryResults, "medications"),
      );
      const conds = await mapQueryRowsToValueSetItems(
        await filterQueryRows(queryResults, "conditions"),
      );

      // Only update if the fetch hasn't altered state yet
      if (isSubscribed) {
        setGroupedValueSetState({
          labs: labs,
          medications: meds,
          conditions: conds,
        });
      }
    };

    fetchQuery().catch(console.error);

    // Destructor hook to prevent future state updates
    return () => {
      isSubscribed = false;
    };
  }, [queryName]);

  useEffect(() => {
    const items = groupedValueSetState[
      activeTab as keyof typeof groupedValueSetState
    ].flatMap((group) => group.items);
    const selectedCount = items.filter((item) => item.include).length;
    const topCheckbox = document.getElementById(
      "select-all",
    ) as HTMLInputElement;
    if (topCheckbox) {
      topCheckbox.indeterminate =
        selectedCount > 0 && selectedCount < items.length;
    }
  }, [groupedValueSetState, activeTab]);

  const accordionItems: AccordionItemProps[] = useMemo(() => {
    const groups =
      groupedValueSetState[activeTab as keyof typeof groupedValueSetState];
    return groups.map((group, groupIndex) => {
      const selectedCount = group.items.filter((item) => item.include).length;
      return {
        title: (
          <div
            className="accordion-header display-flex flex-no-wrap flex-align-start"
            onClick={handleToggleExpand}
          >
            <div
              id="select-all"
              className="hide-checkbox-label"
              style={{
                width: "36px",
                height: "36px",
                backgroundColor: selectedCount === 0 ? "#565C65" : "#fff",
                border:
                  selectedCount === 0 ? "3px white solid" : "1px solid #A9AEB1",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                cursor: "pointer",
                borderRadius: "4px",
              }}
              onClick={(e) => {
                e.stopPropagation();
                handleSelectAllChange(selectedCount !== group.items.length);
              }}
            >
              {selectedCount === group.items.length && (
                <Icon.Check
                  className="usa-icon"
                  style={{ backgroundColor: "white" }}
                  size={4}
                  color="#565C65"
                />
              )}
              {selectedCount > 0 && selectedCount < group.items.length && (
                <Icon.Remove
                  className="usa-icon"
                  style={{ backgroundColor: "white" }}
                  size={4}
                  color="#565C65"
                />
              )}
            </div>
            <div>
              {`${group.items[0].display}`}

              <span className="accordion-subtitle margin-top-2">
                <strong>Author:</strong> {group.author}{" "}
                <strong style={{ marginLeft: "20px" }}>System:</strong>{" "}
                {group.system}
              </span>
            </div>
            <span className="margin-left-auto">{`${selectedCount} selected`}</span>
            <div
              onClick={handleToggleExpand}
              style={{
                cursor: "pointer",
                alignItems: "center",
                display: "flex",
                margin: "-3px",
              }}
            >
              {isExpanded ? (
                <Icon.ExpandLess size={4} />
              ) : (
                <Icon.ExpandMore size={4} />
              )}
            </div>
          </div>
        ),
        id: group.author + ":" + group.system,
        className: "accordion-item",
        content: (
          <AccordianSection>
            <div className="customize-query-grid-container customize-query-table">
              <div className="customize-query-grid-header margin-top-10">
                <div className="accordion-table-header">Include</div>
                <div className="accordion-table-header">Code</div>
                <div className="accordion-table-header">Display</div>
              </div>
              <div className="customize-query-grid-body">
                {group.items.map((item, itemIndex) => (
                  <div
                    className="customize-query-grid-row customize-query-striped-row"
                    key={item.code}
                  >
                    <div
                      className="hide-checkbox-label"
                      style={{
                        border: "1px solid #A9AEB1",
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        cursor: "pointer",
                        borderRadius: "4px",
                        width: "36px",
                        height: "36px",
                        marginLeft: "30px",
                        backgroundColor: "#fff",
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleInclude(groupIndex, itemIndex);
                      }}
                    >
                      {item.include && (
                        <Icon.Check
                          className="usa-icon"
                          style={{ backgroundColor: "white" }}
                          size={4}
                          color="#005EA2"
                        />
                      )}
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
      };
    });
  }, [groupedValueSetState, activeTab, isExpanded]);

  return (
    <div className="customize-query-container">
      <div style={{ paddingTop: "24px" }}>
        <a
          href="#"
          onClick={() => goBack()}
          className="text-bold"
          style={{ fontSize: "16px" }}
        >
          <Icon.ArrowBack /> Return to patient search
        </a>
      </div>
      <LoadingView loading={!useCaseQueryResponse} />
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
        onClick={() => handleSelectAllChange(true)}
      >
        Include all {activeTab}
      </a>
      <div>
        <Accordion items={accordionItems} multiselectable bordered />
      </div>
      <div className="button-container">
        <Button type="button" onClick={handleApplyChanges}>
          Apply changes
        </Button>
        <Button type="button" outline onClick={() => goBack()}>
          Cancel
        </Button>
      </div>
    </div>
  );
};

export default CustomizeQuery;

export const QUERY_CUSTOMIZATION_CONFIRMATION_HEADER =
  "Query Customization Successful!";
export const QUERY_CUSTOMIZATION_CONFIRMATION_BODY =
  "You've successfully customized your query. Once you're done adding patient details, submit your completed query to get results";
