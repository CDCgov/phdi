import { Accordion, Tag } from "@trussworks/react-uswds";
import React from "react";

interface AccordionLabResultsProps {
  title: string;
  abnormalTag: boolean;
  content: React.JSX.Element[];
  organizationId: string;
}

/**
 * Accordion component for displaying lab results.
 * @param {AccordionLabResultsProps} props - The props object.
 * @param {string} props.title - The title of the lab result.
 * @param {boolean} props.abnormalTag - Boolean value if the lab result is abnormal.
 * @param {React.JSX.Element} props.content - The content within the accordian.
 * @returns {React.JSX.Element} React element representing the AccordionLabResults component.
 */
export const AccordionLabResults: React.FC<AccordionLabResultsProps> = ({
  title,
  abnormalTag,
  content,
  organizationId,
}: AccordionLabResultsProps): React.JSX.Element => {
  return (
    <Accordion
      items={[
        {
          title: (
            <>
              {title}
              {abnormalTag && (
                <Tag background={"#B50909"} className={"margin-left-105"}>
                  Abnormal
                </Tag>
              )}
            </>
          ),
          content: content,
          expanded: true,
          id: title,
          headingLevel: "h5",
        },
      ]}
      className={`accordion-rr ${organizationId} margin-bottom-3`}
    />
  );
};
