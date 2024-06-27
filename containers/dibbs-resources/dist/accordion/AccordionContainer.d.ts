import React, { ReactNode } from "react";
import { AccordionItemProps } from "@trussworks/react-uswds/lib/components/Accordion/Accordion";
type AccordionContainerProps = {
  children?: ReactNode;
  accordionItems: AccordionItemProps[];
};
/**
 * Functional component for an accordion container displaying various sections of eCR information.
 * @param props - Props containing FHIR bundle and path mappings.
 * @param props.accordionItems - The list of accordion items.
 * @returns The JSX element representing the accordion container.
 */
declare const AccordionContainer: React.FC<AccordionContainerProps>;
export default AccordionContainer;
