"use client";
import React from "react";
import { Button } from "@trussworks/react-uswds";

type ExpandCollapseButtonsProps = {
  id: string;
  buttonSelector: string;
  accordionSelector: string;
  expandButtonText: string;
  collapseButtonText: string;
};

/**
 * Functional component for a pair of expand and collapse buttons.
 * @param props - Props containing button configurations.
 * @param props.id - The ID for the buttons.
 * @param props.buttonSelector - The CSS selector for the buttons.
 * @param props.accordionSelector - The CSS selector for the accordions to be hidden.
 * @param props.expandButtonText - The text for the expand button.
 * @param props.collapseButtonText - The text for the collapse button.
 * @returns The JSX element representing the expand and collapse buttons.
 */
export const ExpandCollapseButtons: React.FC<ExpandCollapseButtonsProps> = ({
  id,
  buttonSelector,
  accordionSelector,
  expandButtonText,
  collapseButtonText,
}) => {
  return (
    <>
      <Button
        id={`${id}-expand-button`}
        type={"button"}
        unstyled={true}
        onClick={() => {
          const buttons = document.querySelectorAll(buttonSelector);
          buttons.forEach((button) =>
            button.setAttribute("aria-expanded", "true"),
          );
          const accordions = document.querySelectorAll(accordionSelector);
          accordions.forEach((accordion) =>
            accordion.removeAttribute("hidden"),
          );
        }}
      >
        {expandButtonText}
      </Button>
      <span className={"vertical-line"}></span>
      <Button
        id={`${id}-collapse-button`}
        type={"button"}
        unstyled={true}
        onClick={() => {
          const buttons = document.querySelectorAll(buttonSelector);
          buttons.forEach((button) =>
            button.setAttribute("aria-expanded", "false"),
          );
          const accordions = document.querySelectorAll(accordionSelector);
          accordions.forEach((accordion) =>
            accordion.setAttribute("hidden", "true"),
          );
        }}
      >
        {collapseButtonText}
      </Button>
    </>
  );
};
