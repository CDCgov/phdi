import React from "react";
import { Button } from "@trussworks/react-uswds";

type ExpandCollapseButtonsProps = {
  id: string;
  buttonSelector: string;
  accordionSelector: string;
  expandButtonText: string;
  collapseButtonText: string;
};

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
