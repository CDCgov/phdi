import {
  HeadingLevel,
  Accordion as TrussAccordion,
} from "@trussworks/react-uswds";

export type AccordionProps = {
  title: string | React.ReactNode;
  content: string | React.ReactNode;
  expanded?: boolean;
  id: string;
  headingLevel?: HeadingLevel;
  handleToggle?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  containerClassName?: string;
  accordionClassName?: string;
};

/**
 * Accordion wrapper around the Truss implementation that takes in content-forward
 * params and puts it in the right data structure that Truss expects. Hiding
 * these implementation details will hopefully make the component a bit easier
 * to interact with
 * @param props - props
 * @param props.title - The text on the toggle-able button part of the component
 * @param props.content - The text to render in the body of the component
 * @param props.expanded - Whether the accordion is expanded by default. Defaults to false
 * @param props.id - HTML id of the element
 * @param props.headingLevel - h1-h6 heading level. Defaults to h4
 * @param props.handleToggle - listener function to trigger when the accordion is toggled
 * @param props.containerClassName - custom CSS for the container around the accordion
 * @param props.accordionClassName - custom CSS for the accordion itself
 * @returns An accordion component that wraps the USWDS Truss implementation
 */
const Accordion: React.FC<AccordionProps> = ({
  title,
  content,
  id,
  expanded = false,
  headingLevel = "h4",
  handleToggle,
  containerClassName,
  accordionClassName,
}) => {
  const accordionItem = [
    { title, content, id, expanded, headingLevel, handleToggle },
  ];
  return (
    <div className={containerClassName}>
      <TrussAccordion
        items={accordionItem}
        multiselectable={true}
        className={accordionClassName}
      />
    </div>
  );
};

export default Accordion;
