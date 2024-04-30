import Demographics from "./Demographics";
import ObservationTable from "./ObservationTable";
import React from "react";
import { Accordion } from "@trussworks/react-uswds";
import { formatString } from "@/app/format-service";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { UseCaseQueryResponse } from "@/app/query-service";

type AccordionContainerProps = {
  queryResponse: UseCaseQueryResponse;
};

/**
 * Returns the Accordion component to render all components of the query response.
 * @param queryResponse.queryResponse
 * @param queryResponse - The response from the query service.
 * @returns The AccordionContainer component.
 */
const AccordianContainer: React.FC<AccordionContainerProps> = ({
  queryResponse,
}) => {
  const accordionItems: any[] = [];

  const patient =
    queryResponse.patients && queryResponse.patients.length === 1
      ? queryResponse.patients[0]
      : null;
  const observations = queryResponse.observations
    ? queryResponse.observations
    : null;

  if (patient) {
    accordionItems.push({
      title: "Patient Info",
      content: (
        <>
          <AccordianSection>
            <AccordianH4>
              <span id="patient">Demographics</span>
            </AccordianH4>
            <AccordianDiv>
              <Demographics patient={patient} />
            </AccordianDiv>
          </AccordianSection>
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    });
  }

  if (observations) {
    accordionItems.push({
      title: "Observations",
      content: (
        <>
          <AccordianSection>
            <AccordianH4>
              <span id="observations">Observations</span>
            </AccordianH4>
            <AccordianDiv>
              <ObservationTable observations={observations} />
            </AccordianDiv>
          </AccordianSection>
        </>
      ),
      expanded: true,
      headingLevel: "h3",
    });
  }

  //Add id, adjust title
  accordionItems.forEach((item, index) => {
    let formattedTitle = formatString(item["title"]);
    item["id"] = `${formattedTitle}_${index + 1}`;
    item["title"] = <span id={formattedTitle}>{item["title"]}</span>;
    accordionItems[index] = item;
  });

  return (
    <Accordion
      className="info-container"
      items={accordionItems}
      multiselectable={true}
    />
  );
};
export default AccordianContainer;
