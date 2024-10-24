"use client";
import React from "react";
import { Button } from "@trussworks/react-uswds";

type SortButtonProps = {
  columnName: string;
  className: string;
};

/**
 * Functional component for a sort button.
 * @param props - Props containing button configurations.
 * @param props.columnName - The name of the column to sort
 * @param props.className   - The class name of the button
 * @returns The JSX element representing the sort button.
 */
export const SortButton: React.FC<SortButtonProps> = ({
  columnName,
  className,
}) => {
  const buttonSelector = `${columnName}-sort-button`;
  // const headerSelector = `${currentSortedColumnId}-header`;
  const headerSelectorToSort = `${columnName}-header`;
  return (
    <>
      <Button
        id={`${columnName}-sort-button`}
        className={`usa-button ${className}`}
        type="button"
        onClick={() => {
          // Reset arrow direction if changing column
          const buttonsToReset = document.querySelectorAll(
            'th[aria-sort="ascending"] button',
          );
          //console.log("Buttons to reset");
          //console.log(buttonsToReset);
          buttonsToReset.forEach((header) => {
            header.id !== buttonSelector
              ? header.setAttribute("class", "usa-button sortable-column")
              : "";
          });

          // Change arrow direction
          //console.log(columnSortDirection);
          //console.log(`button#${buttonSelector}`);
          const buttons = document.querySelectorAll(`button#${buttonSelector}`);
          //console.log(buttons);
          buttons.forEach((button) => {
            button.className === "usa-button sortable-column"
              ? button.setAttribute("class", "usa-button sortable-asc-column")
              : button.className === "usa-button sortable-asc-column"
                ? button.setAttribute(
                    "class",
                    "usa-button sortable-desc-column",
                  )
                : button.setAttribute(
                    "class",
                    "usa-button sortable-asc-column",
                  );
          });

          // Reset header marker
          const headersToReset = document.querySelectorAll(`th`);
          //console.log(headersToReset);
          headersToReset.forEach((header) => {
            header.removeAttribute("aria-sort");
          });

          // Set header marker
          const headerToSet = document.querySelectorAll(
            `th#${headerSelectorToSort}`,
          );
          //console.log(headerToSet);
          headerToSet.forEach((header) =>
            header.setAttribute("aria-sort", "ascending"),
          );
        }}
        children={""}
      ></Button>
    </>
  );
};
