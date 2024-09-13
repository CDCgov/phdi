"use client";

import React, { useState, useEffect } from "react";
import { Button, Icon } from "@trussworks/react-uswds";
import { QueryTypeToQueryName, ValueSetItem } from "../../constants";
import {
  getSavedQueryByName,
  filterQueryRows,
  mapQueryRowsToValueSetItems,
} from "@/app/database-service";
import { UseCaseQueryResponse } from "@/app/query-service";
import LoadingView from "./LoadingView";
import { showRedirectConfirmation } from "./RedirectionToast";
import styles from "./customizeQuery/customizeQuery.module.css";
import CustomizeQueryAccordionHeader from "./customizeQuery/CustomizeQueryAccordionHeader";
import CustomizeQueryAccordionBody from "./customizeQuery/CustomizeQueryAccordionBody";
import Accordion from "./Accordion";
import CustomizeQueryNav from "./customizeQuery/CustomizeQueryNav";

// Define types for better structure and reusability
export type DefinedValueSetCollection = {
  valueset_name: string;
  author: string;
  system: string;
  items: ValueSetItem[];
  isExpanded: boolean;
};

type GroupedValueSet = {
  labs: DefinedValueSetCollection[];
  medications: DefinedValueSetCollection[];
  conditions: DefinedValueSetCollection[];
};

export type GroupedValueSetKey = keyof GroupedValueSet;

interface CustomizeQueryProps {
  useCaseQueryResponse: UseCaseQueryResponse;
  queryType: string;
  goBack: () => void;
}

/**
 * CustomizeQuery component for displaying and customizing query details.
 * @param root0 - The properties object.
 * @param root0.useCaseQueryResponse - The response from the query service.
 * @param root0.queryType - The type of the query.
 * @param root0.goBack - Back button to go from "customize-queries" to "search" component.
 * @returns The CustomizeQuery component.
 */
const CustomizeQuery: React.FC<CustomizeQueryProps> = ({
  useCaseQueryResponse,
  queryType,
  goBack,
}) => {
  const [activeTab, setActiveTab] = useState<GroupedValueSetKey>("labs");

  const [groupedValueSetState, setGroupedValueSetState] =
    useState<GroupedValueSet>({
      labs: [],
      medications: [],
      conditions: [],
    });

  const handleToggle = (e: React.MouseEvent<HTMLButtonElement>) => {
    alert("yay");
    console.log(e);
  };

  // Keeps track of which side nav tab to display to users
  const handleTabChange = (tab: GroupedValueSetKey) => {
    setActiveTab(tab);
  };

  // Handles the toggle of the 'include' state for individual items
  const toggleInclude = (groupIndex: number, itemIndex: number) => {
    const updatedGroups = [...groupedValueSetState[activeTab]];
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

  // Allows all items to be selected within all accordion sections of the active tab
  const handleSelectAllChange = (groupIndex: number, checked: boolean) => {
    const updatedGroups = [...groupedValueSetState[activeTab]];

    // Update only the group at the specified index
    updatedGroups[groupIndex].items = updatedGroups[groupIndex].items.map(
      (item) => ({
        ...item,
        include: checked, // Set all items in this group to checked or unchecked
      })
    );

    setGroupedValueSetState((prevState) => ({
      ...prevState,
      [activeTab]: updatedGroups, // Update the state for the current tab
    }));
  };

  // Allows all items to be selected within the entire active tab
  const handleSelectAllForTab = (checked: boolean) => {
    const updatedGroups = groupedValueSetState[activeTab].map((group) => ({
      ...group,
      items: group.items.map((item) => ({
        ...item,
        include: checked, // Set all items in this group to checked or unchecked
      })),
    }));

    setGroupedValueSetState((prevState) => ({
      ...prevState,
      [activeTab]: updatedGroups, // Update the state for the current tab
    }));
  };

  // Will eventually be the json object storing the parsed data to return on the results page
  const handleApplyChanges = () => {
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

    // Lookup the name of this queryType
    const queryName = QueryTypeToQueryName[queryType];

    const fetchQuery = async () => {
      const queryResults = await getSavedQueryByName(queryName);
      const labs = await mapQueryRowsToValueSetItems(
        await filterQueryRows(queryResults, "labs")
      );
      const meds = await mapQueryRowsToValueSetItems(
        await filterQueryRows(queryResults, "medications")
      );
      const conds = await mapQueryRowsToValueSetItems(
        await filterQueryRows(queryResults, "conditions")
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
  }, [queryType]);

  useEffect(() => {
    const items = groupedValueSetState[activeTab].flatMap(
      (group) => group.items
    );
    const selectedCount = items.filter((item) => item.include).length;
    const topCheckbox = document.getElementById(
      "select-all"
    ) as HTMLInputElement;
    if (topCheckbox) {
      topCheckbox.indeterminate =
        selectedCount > 0 && selectedCount < items.length;
    }
  }, [groupedValueSetState, activeTab]);

  return (
    <div className="main-container">
      <div className="padding-top-3">
        <a href="#" onClick={() => goBack()} className="back-link">
          <Icon.ArrowBack /> Return to patient search
        </a>
      </div>
      <LoadingView loading={!useCaseQueryResponse} />
      <h1 className="font-sans-2xl text-bold margin-top-205">
        Customize query
      </h1>
      <div className="font-sans-lg text-light padding-bottom-0 padding-top-05">
        Query: {queryType}
      </div>

      <CustomizeQueryNav
        activeTab={activeTab}
        handleTabChange={handleTabChange}
        handleSelectAllForTab={handleSelectAllForTab}
      />
      {groupedValueSetState[activeTab].map((group, groupIndex) => {
        const selectedCount = group.items.filter((item) => item.include).length;
        return (
          <Accordion
            title={
              <CustomizeQueryAccordionHeader
                selectedCount={selectedCount}
                handleSelectAllChange={handleSelectAllChange}
                groupIndex={groupIndex}
                group={group}
                isExpanded={group.isExpanded}
              />
            }
            content={
              <CustomizeQueryAccordionBody
                group={group}
                toggleInclude={toggleInclude}
                groupIndex={groupIndex}
              />
            }
            id={group.author + ":" + group.system}
            expanded
            headingLevel="h3"
            handleToggle={handleToggle}
            accordionClassName={`customize-accordion ${styles.customizeQueryAccordion}`}
            containerClassName={styles.resultsContainer}
          />
        );
      })}
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
