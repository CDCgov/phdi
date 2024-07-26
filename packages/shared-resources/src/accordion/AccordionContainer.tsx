import React, { ReactNode } from "react";
import { Accordion } from "@trussworks/react-uswds";
import { AccordionItemProps } from "@trussworks/react-uswds/lib/components/Accordion/Accordion";
import { formatString } from "../services/formatService";

type AccordionContainerProps = {
  accordionItems: AccordionItemProps[];
};

/**
 * Functional component for an accordion container displaying various sections of eCR information.
 * @param props - Props containing FHIR bundle and path mappings.
 * @param props.accordionItems - The list of accordion items.
 * @returns The JSX element representing the accordion container.
 */
const AccordionContainer = ({
  accordionItems,
}: AccordionContainerProps): React.JSX.Element => {
  const items: AccordionItemProps[] = accordionItems.map((item, index) => {
    let formattedTitle = formatString(`${item["title"]}`);
    return {
      ...item,
      id: `${formattedTitle}_${index + 1}`,
      title: <span id={formattedTitle}>{item["title"]}</span>,
    };
  });

  return (
    <Accordion
      className="info-container"
      items={items}
      multiselectable={true}
    />
  );
};
export default AccordionContainer;
