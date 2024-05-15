import React, { ReactNode } from "react";
import classNames from "classnames";

type AccordionSectionProps = {
  children: ReactNode;
  className?: string;
  id?: string;
};

/**
 * Functional component for an accordion section.
 * @param props - Props containing children and optional className.
 * @param props.children - The content of the accordion section.
 * @param [props.className] - Optional additional class name for styling.
 * @returns The JSX element representing the accordion section.
 */
export const AccordionSection: React.FC<AccordionSectionProps> = ({
  children,
  className,
}) => {
  return (
    <div className="margin-top-0">
      <div className="padding-bottom-3">
        <div className={classNames("usa-summary-box__body", className)}>
          {children}
        </div>
      </div>
    </div>
  );
};

/**
 * Accordion heading component for level 4 headings.
 * @param props - The props object.
 * @param props.children - The children elements.
 * @param [props.className] - Additional CSS classes for customization.
 * @param [props.id] - The ID attribute of the heading.
 * @returns React element representing the AccordionH4 component.
 */
export const AccordionH4: React.FC<AccordionSectionProps> = ({
  children,
  className,
  id,
}: AccordionSectionProps): React.JSX.Element => {
  return (
    <h4
      className={classNames(
        "usa-summary-box__heading padding-y-105",
        className,
      )}
      id={id ?? "summary-box-key-information"}
    >
      {children}
    </h4>
  );
};

/**
 * Functional component for an accordion div.
 * @param props - Props containing children and optional className.
 * @param props.children - The content of the accordion div.
 * @param [props.className] - Optional additional class name for styling.
 * @returns The JSX element representing the accordion div.
 */
export const AccordionDiv: React.FC<AccordionSectionProps> = ({
  children,
  className,
}) => {
  return (
    <div className={classNames("usa-summary-box__text", className)}>
      {children}
    </div>
  );
};
