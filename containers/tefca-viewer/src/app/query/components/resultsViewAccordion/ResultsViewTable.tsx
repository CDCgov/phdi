import React from "react";
import Accordion from "../../designSystem/Accordion";
import styles from "./resultsTable.module.css";
import ResultsViewAccordionBody from "./ResultsViewAccordionBody";
import { ResultsViewAccordionItem } from "../ResultsView";

type ResultsViewTable = {
  accordionItems: ResultsViewAccordionItem[];
};

/**
 * Returns the Accordion component to render all components of the query response.
 * @param props - The props for the AccordionContainer component.
 * @param props.queryResponse - The response from the query service.
 * @returns The AccordionContainer component.
 */
const ResultsViewTable: React.FC<ResultsViewTable> = ({ accordionItems }) => {
  return (
    <div data-testid="accordion">
      {accordionItems.map((item) => {
        const titleId = formatIdForAnchorTag(item.title);
        return (
          item.content && (
            <>
              <Accordion
                title={item.title}
                content={
                  <ResultsViewAccordionBody
                    title={item.subtitle ?? ""}
                    content={item.content}
                    id={formatIdForAnchorTag(item.subtitle ?? "")}
                  />
                }
                expanded={true}
                id={titleId}
                headingLevel={"h3"}
                accordionClassName={styles.accordionWrapper}
                containerClassName={styles.accordionContainer}
              />
            </>
          )
        );
      })}
    </div>
  );
};

export default ResultsViewTable;

export function formatIdForAnchorTag(id: string) {
  return id.toLocaleLowerCase().replace(" ", "-");
}
