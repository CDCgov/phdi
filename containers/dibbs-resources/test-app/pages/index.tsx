// pages/index.tsx
import { AccordionContainer } from "dibbs-resources";
import { TooltipElement } from "dibbs-resources";
import { formatDate } from "dibbs-resources";
import { AccordionItemProps } from "@trussworks/react-uswds/lib/components/Accordion/Accordion";

/**
 * The items to be displayed in the accordion.
 */
const accordionItems: AccordionItemProps[] = [
  {
    title: "Item 1",
    content: <p>Content 1</p>,
    expanded: false,
    id: "item-1",
    headingLevel: "h3",
  },
  {
    title: "Item 2",
    content: <p>Content 2</p>,
    expanded: false,
    id: "item-2",
    headingLevel: "h3",
  },
];

/**
 * The home page component.
 * @returns The home page component.
 */
export default function Home() {
  return (
    <div>
      <h1>Test Components</h1>
      <AccordionContainer accordionItems={accordionItems} />
      <TooltipElement content="Hover me" tooltip="Tooltip text" />
      <p>Formatted Date: {formatDate("2023-01-01")}</p>
    </div>
  );
}
