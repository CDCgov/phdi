import {
  AccordionSection,
  AccordionH4,
  AccordionDiv,
} from "../component-utils";
import { Table } from "@trussworks/react-uswds";
import { ToolTipElement } from "@/app/view-data/components/ToolTipElement";
import {
  ERSDWarning,
  ReportableConditions,
} from "../../services/ecrMetadataService";
import {
  DataDisplay,
  DisplayDataProps,
} from "@/app/view-data/components/DataDisplay";
import React from "react";

interface EcrMetadataProps {
  rrDetails: ReportableConditions;
  eicrDetails: DisplayDataProps[];
  eRSDWarnings: ERSDWarning[];
  eCRCustodianDetails: DisplayDataProps[];
  eicrAuthorDetails: DisplayDataProps[][];
}

interface ReportableConditionsList {
  [condition: string]: {
    [trigger: string]: Set<string>; // Maps a trigger to a set of locations
  };
}

const convertDictionaryToRows = (dictionary: ReportableConditionsList) => {
  if (!dictionary) return [];
  const rows: React.JSX.Element[] = [];
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

/**
 * Functional component for displaying eCR metadata.
 * @param props - Props containing eCR metadata.
 * @param props.rrDetails - The reportable conditions details.
 * @param props.eicrDetails - The eICR details.
 * @param props.eRSDWarnings - The eRSD warnings.
 * @param props.eCRCustodianDetails - The eCR custodian details.
 * @param props.eicrAuthorDetails - The eICR author details.
 * @returns The JSX element representing the eCR metadata.
 */
const EcrMetadata = ({
  rrDetails,
  eicrDetails,
  eRSDWarnings,
  eCRCustodianDetails,
  eicrAuthorDetails,
}: EcrMetadataProps) => {
  return (
    <AccordionSection>
      <AccordionH4 id={"rr-details"}>RR Details</AccordionH4>
      <AccordionDiv>
        <Table
          bordered
          caption="Reportibility Summary"
          className="rrTable"
          fixed={true}
          fullWidth={true}
        >
          <thead>
            <tr>
              <th className="width-25p">
                <ToolTipElement
                  content={"Reportable Condition"}
                  toolTip={
                    "List of conditions that caused this eCR to be sent to your jurisdiction based on the rules set up for routing eCRs by your jurisdiction in RCKMS (Reportable Condition Knowledge Management System). Can include multiple Reportable Conditions for one eCR."
                  }
                />
              </th>
              <th>
                <ToolTipElement
                  content={"RCKMS Rule Summary"}
                  toolTip={
                    "Reason(s) that this eCR was sent for this condition. Corresponds to your jurisdiction's rules for routing eCRs in RCKMS (Reportable Condition Knowledge Management System)."
                  }
                />
              </th>
              <th className="width-25p">
                <ToolTipElement
                  content={"Jurisdiction Sent eCR"}
                  toolTip={
                    "List of jurisdictions this eCR was sent to. Can include multiple jurisdictions depending on provider location, patient address, and jurisdictions onboarded to eCR."
                  }
                />
              </th>
            </tr>
          </thead>
          <tbody>{convertDictionaryToRows(rrDetails)}</tbody>
        </Table>
        {eRSDWarnings?.length > 0 ? (
          <div>
            <div className="section__line_gray"></div>
            <Table
              bordered={false}
              className="ersd-table fixed-table border-top border-left border-right border-bottom"
              caption="eRSD Warnings"
              fixed={true}
              fullWidth
            >
              <thead>
                <tr>
                  <th>Warning</th>
                  <th>Version in Use</th>
                  <th>Expected Version</th>
                  <th>Suggested Solution</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(eRSDWarnings) &&
                  eRSDWarnings.map((warningItem, index) => (
                    <tr key={index}>
                      <td className="padding-105">{warningItem.warning}</td>
                      <td className="padding-105">{warningItem.versionUsed}</td>
                      <td className="padding-105">
                        {warningItem.expectedVersion}
                      </td>
                      <td className="padding-105">
                        {warningItem.suggestedSolution}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </Table>
            <div className="section__line_gray"></div>
          </div>
        ) : (
          ""
        )}
        <div className={"padding-bottom-1"} />
        <AccordionH4 id={"eicr-details"}>eICR Details</AccordionH4>
        {eicrDetails.map((item, index) => {
          return <DataDisplay item={item} key={index} />;
        })}
        <div className={"padding-bottom-1"} />
        {eicrAuthorDetails?.map((authorDetailsDisplayProps, index) => {
          if (authorDetailsDisplayProps?.length > 0) {
            return (
              <React.Fragment key={index}>
                <AccordionH4 id={"eicr-author-details-for-practitioner"}>
                  eICR Author Details for Practitioner
                </AccordionH4>
                {authorDetailsDisplayProps.map((item, index) => {
                  return <DataDisplay item={item} key={index} />;
                })}
                <div className={"padding-bottom-1"} />
              </React.Fragment>
            );
          }
        })}
        <AccordionH4 id={"eicr-custodian-details"}>
          eICR Custodian Details
        </AccordionH4>
        {eCRCustodianDetails.map((item, index) => {
          return <DataDisplay item={item} key={index} />;
        })}
      </AccordionDiv>
    </AccordionSection>
  );
};

export default EcrMetadata;
