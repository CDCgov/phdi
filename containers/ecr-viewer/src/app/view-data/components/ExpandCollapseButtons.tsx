import React from "react";

type ExpandCollapseButtonsProps = {
  id: string;
  buttonSelector: string;
  accordionSelector: string;
};

export const ExpandCollapseButtons: React.FC<ExpandCollapseButtonsProps> = ({
  id,
  buttonSelector,
  accordionSelector,
}) => {
  return (
    <>
      <button
        id={`${id}-expand-button`}
        className={"usa-button usa-button--unstyled"}
        onClick={() => {
          const buttons = document.querySelectorAll(buttonSelector);
          buttons.forEach((button) =>
            button.setAttribute("aria-expanded", "true"),
          );
          const accordions = document.querySelectorAll(accordionSelector);
          accordions.forEach((accordion: HTMLButtonElement) =>
            accordion.removeAttribute("hidden"),
          );
        }}
      >
        Expand all sections
      </button>
      <span className={"vertical-line"}></span>
      <button
        id={`${id}-collapse-button`}
        className={"usa-button usa-button--unstyled"}
        onClick={() => {
          const buttons = document.querySelectorAll(buttonSelector);
          buttons.forEach((button) =>
            button.setAttribute("aria-expanded", "false"),
          );
          const accordions = document.querySelectorAll(accordionSelector);
          accordions.forEach((accordion: HTMLButtonElement) =>
            accordion.setAttribute("hidden", "true"),
          );
        }}
      >
        Collapse all sections
      </button>
    </>
  );
};
