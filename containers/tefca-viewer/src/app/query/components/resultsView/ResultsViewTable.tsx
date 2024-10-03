import React from "react";
import Accordion from "../../designSystem/Accordion";
import styles from "./resultsTable.module.css";
import ResultsViewAccordionBody from "./ResultsViewAccordionBody";
import { ResultsViewAccordionItem } from "../ResultsView";

type ResultsViewTable = {
  accordionItems: ResultsViewAccordionItem[];
};

/**
 * Returns the ResultsViewTable component to render all components of the query response.
 * @param root0 - The props for the AccordionContainer component.
 * @param root0.accordionItems - an array of items to render as an accordion
 * group of type ResultsViewAccordionItem
 * @returns The ResultsViewTable component.
 */
const ResultsViewTable: React.FC<ResultsViewTable> = ({ accordionItems }) => {
  return (
    <div data-testid="accordion">
      {accordionItems.map((item) => {
        const titleId = formatIdForAnchorTag(item.title);
        return (
          item.content && (
            <div className="padding-bottom-2" key={item.title}>
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
                key={titleId}
                headingLevel={"h3"}
                accordionClassName={styles.accordionWrapper}
                containerClassName={styles.accordionContainer}
              />
            </div>
          )
        );
      })}
    </div>
  );
};

export default ResultsViewTable;

/**
 * Helper function to format titles (probably title cased with spaces) into
 * anchor tag format
 * @param title A string that we want to turn
 *  into anchor tag format
 * @returns - A hyphenated id that can be linked as an anchor tag
 */
export function formatIdForAnchorTag(title: string) {
  return title.toLocaleLowerCase().replace(" ", "-");
}
