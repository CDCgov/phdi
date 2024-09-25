import styles from "./resultsTable.module.css";

type ResultsViewAccordionBodyProps = {
  title: string;
  id?: string;
  content: React.ReactNode;
};

/**
 * Fragment component to style out some of the accordion bodies
 * @param param0 - params
 * @param param0.title - Title to display once the accordion is expanded
 * @param param0.id - Markup id for the accordion
 * @param param0.content - Table / content to display once the accordion
 * is expanded
 * @returns An accordion body component
 */
const ResultsViewAccordionBody: React.FC<ResultsViewAccordionBodyProps> = ({
  title,
  content,
  id,
}) => {
  return (
    <>
      {title && (
        <h4 id={id} className={styles.accordionHeading}>
          {title}
        </h4>
      )}
      <div className={"usa-summary-box__text"}>{content}</div>
    </>
  );
};

export default ResultsViewAccordionBody;
