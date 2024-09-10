import React, { ReactNode } from "react";
import classNames from "classnames";

type AccordianSectionProps = {
  children: ReactNode;
  className?: string;
  id?: string;
};

/**
 * Accordion section component for the content of the accordion.
 * @param props - The props object.
 * @param props.children - The children elements.
 * @param [props.className] - Additional CSS classes for customization.
 * @returns React element representing the AccordionSection component.
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
