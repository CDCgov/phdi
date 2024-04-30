import React, { ReactNode } from "react";
import classNames from "classnames";

type AccordianSectionProps = {
  children: ReactNode;
  className?: string;
  id?: string;
};


/**
 * Accordion section component for the content of the accordion.
 * @param {Object} props - The props object.
 * @param {React.ReactNode} props.children - The children elements.
 * @param {string} [props.className] - Additional CSS classes for customization.
 * @returns {React.JSX.Element} React element representing the AccordionSection component.
 */
export const AccordianSection: React.FC<AccordianSectionProps> = ({
  children,
  className,
}) => {
  return (
    <div>
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
 * @param {Object} props - The props object.
 * @param {React.ReactNode} props.children - The children elements.
 * @param {string} [props.className] - Additional CSS classes for customization.
 * @param {string} [props.id] - The ID attribute of the heading.
 * @returns {React.JSX.Element} React element representing the AccordionH4 component.
 */
export const AccordianH4: React.FC<AccordianSectionProps> = ({
  children,
  className,
  id,
}: AccordianSectionProps): React.JSX.Element => {
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
 * Accordion div component for the content of the accordion section.
 * @param {Object} props - The props object.
 * @param {React.ReactNode} props.children - The children elements.
 * @param {string} [props.className] - Additional CSS classes for customization.
 * @returns {React.JSX.Element} React element representing the AccordionDiv component.
 */
export const AccordianDiv: React.FC<AccordianSectionProps> = ({
  children,
  className,
}) => {
  return (
    <div className={classNames("usa-summary-box__text", className)}>
      {children}
    </div>
  );
};
