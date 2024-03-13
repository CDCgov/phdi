import { Accordion, Icon, Tag } from "@trussworks/react-uswds";
import React from "react";

interface AccordionRRProps {
  title: string;
  abnormalTag: boolean;
  content: React.JSX.Element;
}
export const AccordionRR: React.FC<AccordionRRProps> = ({
  title,
  abnormalTag,
  content,
}) => {
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
              <Icon.Remove className={"minimize-container"} size={3} />
            </>
          ),
          content: content,
          expanded: true,
          id: "123",
          headingLevel: "h4",
        },
      ]}
      className={"accordion-rr"}
    />
  );
};
