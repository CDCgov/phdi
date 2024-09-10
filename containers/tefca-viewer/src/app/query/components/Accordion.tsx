import {
  HeadingLevel,
  Accordion as TrussAccordion,
} from "@trussworks/react-uswds";
import { AccordionItemProps } from "@trussworks/react-uswds/lib/components/Accordion/Accordion";

type AccordionProps = {
  title: string;
  content: string | React.ReactNode;
  expanded: boolean;
  id: string;
  headingLevel: HeadingLevel;
  handleToggle?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  containerClassName?: string;
  accordionClassName?: string;
};

const Accordion: React.FC<AccordionProps> = ({
  title,
  content,
  expanded,
  id,
  headingLevel,
  handleToggle,
  containerClassName,
  accordionClassName,
}) => {
  const accordionItem: AccordionItemProps = {
    title,
    content,
    expanded,
    id,
    headingLevel,
    handleToggle,
  };
  return (
    <div className={containerClassName}>
      <TrussAccordion
        items={[accordionItem]}
        multiselectable={true}
        className={accordionClassName}
      />
    </div>
  );
};

export default Accordion;
