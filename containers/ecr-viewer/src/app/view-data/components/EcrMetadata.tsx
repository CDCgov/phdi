import { DisplayData, ReportableConditions } from "../../utils";
import { Fragment } from "react";

import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import { Table } from "@trussworks/react-uswds";

interface EcrMetadataProps {
  rrDetails: ReportableConditions;
  eicrDetails: DisplayData[];
  eCRSenderDetails: DisplayData[];
}

export const ecrMetadataConfig: SectionConfig = new SectionConfig(
  "eCR Metadata",
  ["RR Details", "eICR Details", "eCR Sender Details"],
);

interface ReportableConditionsList {
  [condition: string]: {
    [trigger: string]: Set<string>; // Maps a trigger to a set of locations
  };
}

const convertDictionaryToRows = (dictionary: ReportableConditionsList) => {
  if (!dictionary) return [];
  const rows: JSX.Element[] = [];
  Object.entries(dictionary).forEach(([condition, triggers], _) => {
    Object.entries(triggers).forEach(([trigger, locations], triggerIndex) => {
      const locationsArray = Array.from(locations);
      locationsArray.forEach((location, locationIndex) => {
        const isConditionRow = triggerIndex === 0 && locationIndex === 0;
        const isTriggerRow = locationIndex === 0;
        const conditionCell = isConditionRow ? (
          <td
            rowSpan={Object.keys(triggers).reduce(
              (acc, key) => acc + Array.from(triggers[key]).length,
              0,
            )}
          >
            {condition}
          </td>
        ) : null;
        const triggerCell = isTriggerRow ? (
          <td rowSpan={locationsArray.length}>{trigger}</td>
        ) : null;

        rows.push(
          <tr key={`${condition}-${trigger}-${location}`}>
            {conditionCell}
            {triggerCell}
            <td>{location}</td>
          </tr>,
        );
      });
    });
  });

  return rows;
};

const EcrMetadata = ({
  rrDetails,
  eicrDetails,
  eCRSenderDetails,
}: EcrMetadataProps) => {
  return (
    <AccordianSection>
      <AccordianH4>
        <span id={ecrMetadataConfig.subNavItems?.[0].id}>
          {ecrMetadataConfig.subNavItems?.[0].title}
        </span>
      </AccordianH4>
      <AccordianDiv>
        <Table bordered caption="Reportibility Summary" className="rrTable">
          <thead>
            <tr>
              <th>
                <span title="List of conditions that caused this eCR to be sent to your 
                jurisdiction based on the rules set up for routing eCRs by your jurisdiction 
                in RCKMS (Reportable Condition Knowledge Management System). 
                Can include multiple Reportable Conditions for one eCR.">
                Reportable Condition
              </span>
              </th>
              <th>
                <span title="Reason(s) that this eCR was sent for this condition. 
                Corresponds to your jurisdiction's rules for routing eCRs in RCKMS 
                (Reportable Condition Knowledge Management System).">
                  RCKMS Rule Summary
                </span>
              </th>
              <th>
                <span title="List of jurisdictions this eCR was sent to. Can 
                include multiple jurisdictions depending on provider location, 
                patient address, and jurisdictions onboarded to eCR.">
                  Jurisdiction Sent eCR
                  </span>
              </th>
            </tr>
          </thead>
          <tbody>{convertDictionaryToRows(rrDetails)}</tbody>
        </Table>
        <div className={"padding-bottom-1"} />
        <AccordianH4>
          <span id={ecrMetadataConfig.subNavItems?.[1].id}>
            {ecrMetadataConfig.subNavItems?.[1].title}
          </span>
        </AccordianH4>
        {eicrDetails.map(({ title, value }) => {
          return (
            <Fragment key={title}>
              <div className="grid-row">
                <div className="data-title">{title}</div>
                <div className="grid-col-auto text-pre-line">{value}aaaaa</div>
              </div>
              <div className={"section__line_gray"} />
            </Fragment>
          );
        })}
        <div className={"padding-bottom-1"} />
        <AccordianH4>
          <span id={ecrMetadataConfig.subNavItems?.[2].id}>
            {ecrMetadataConfig.subNavItems?.[2].title}
          </span>
        </AccordianH4>
        {eCRSenderDetails.map(({ title, value }) => {
          return (
            <Fragment key={title}>
              <div className="grid-row">
                <div className="data-title">{title}</div>
                <div className="grid-col-auto text-pre-line">{value}</div>
              </div>
              <div className={"section__line_gray"} />
            </Fragment>
          );
        })}
      </AccordianDiv>
    </AccordianSection>
  );
};

export default EcrMetadata;
