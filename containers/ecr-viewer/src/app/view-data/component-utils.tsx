import React, { ReactNode } from "react";

type AccordianSectionProps = {
  children: ReactNode;
};

export const AccordianSection: React.FC<AccordianSectionProps> = ({
  children,
}) => {
  return (
    <div>
      <div className="padding-bottom-3">
        <div className="usa-summary-box__body">{children}</div>
      </div>
    </div>
  );
};

export const AccordianH3: React.FC<AccordianSectionProps> = ({ children }) => {
  return (
    <h3
      className="usa-summary-box__heading padding-y-105"
      id="summary-box-key-information"
    >
      {children}
    </h3>
  );
};

export const AccordianDiv: React.FC<AccordianSectionProps> = ({ children }) => {
  return <div className="usa-summary-box__text">{children}</div>;
};
