import Demographics from "./Demographics";
import ObservationTable from "./ObservationTable";
import EncounterTable from "./EncounterTable";
import DiagnosticReportTable from "./DiagnosticReportTable";
import React from "react";
import Accordion from "./Accordion";
import { UseCaseQueryResponse } from "@/app/query-service";
import ConditionsTable from "./ConditionsTable";
import MedicationRequestTable from "./MedicationRequestTable";
import styles from "./resultsTable.module.css";
import ResultsViewAccordionBody from "./ResultsViewAccordionBody";

type ResultsViewTable = {
  queryResponse: UseCaseQueryResponse;
};

/**
 * Returns the Accordion component to render all components of the query response.
 * @param props - The props for the AccordionContainer component.
 * @param props.queryResponse - The response from the query service.
 * @returns The AccordionContainer component.
 */
const ResultsViewTable: React.FC<ResultsViewTable> = ({ queryResponse }) => {
  const patient =
    queryResponse.Patient && queryResponse.Patient.length === 1
      ? queryResponse.Patient[0]
      : null;
  const observations = queryResponse.Observation
    ? queryResponse.Observation
    : null;
  const encounters = queryResponse.Encounter ? queryResponse.Encounter : null;
  const conditions = queryResponse.Condition ? queryResponse.Condition : null;
  const diagnosticReports = queryResponse.DiagnosticReport
    ? queryResponse.DiagnosticReport
    : null;
  const medicationRequests = queryResponse.MedicationRequest
    ? queryResponse.MedicationRequest
    : null;

  const accordionItems = [
    {
      title: "Patient Info",
      subtitle: "Demographics",
      content: patient ? <Demographics patient={patient} /> : null,
    },
    {
      title: "Observations",
      content: observations ? (
        <ObservationTable observations={observations} />
      ) : null,
    },
    {
      title: "Encounters",
      content: encounters ? <EncounterTable encounters={encounters} /> : null,
    },
    {
      title: "Conditions",
      content: conditions ? <ConditionsTable conditions={conditions} /> : null,
    },
    {
      title: "Diagnostic Reports",
      content: diagnosticReports ? (
        <DiagnosticReportTable diagnosticReports={diagnosticReports} />
      ) : null,
    },
    {
      title: "Medication Requests",
      content: medicationRequests ? (
        <MedicationRequestTable medicationRequests={medicationRequests} />
      ) : null,
    },
  ];

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
                    title={item.subtitle ?? item.title}
                    content={item.content}
                    id={formatIdForAnchorTag(item.subtitle ?? item.title)}
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

function formatIdForAnchorTag(id: string) {
  return id.toLocaleLowerCase().replace(" ", "-");
}
