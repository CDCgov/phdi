import React, { ReactNode } from "react";
import classNames from "classnames";

type AccordianSectionProps = {
  children: ReactNode;
  className?: string;
};

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

export const AccordianH3: React.FC<AccordianSectionProps> = ({
  children,
  className,
}) => {
  return (
    <h3
      className={classNames(
        "usa-summary-box__heading padding-y-105",
        className,
      )}
      id="summary-box-key-information"
    >
      {children}
    </h3>
  );
};

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
