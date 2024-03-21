import { DisplayData } from "../../utils";
import { Fragment } from "react";

import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";
import { Table } from "@trussworks/react-uswds";

interface EcrMetadataProps {
  rrDetails: any;
  eicrDetails: DisplayData[];
  eCRSenderDetails: DisplayData[];
}

export const ecrMetadataConfig: SectionConfig = new SectionConfig(
  "eCR Metadata",
  ["RR Details", "eICR Details", "eCR Sender Details"],
);

interface TriggerLocationDict {
  [key: string]: {
    triggers: Set<string>;
    jurisdiction: Set<string>;
  };
}

const convertDictionaryToRows = (dictionary: TriggerLocationDict) => {
  if (!dictionary) return [];
  const rows: JSX.Element[] = [];
  console.log("The dic");
  console.log(dictionary);
  Object.entries(dictionary).forEach(([key, { triggers, jurisdiction }], _) => {
    console.log("The locations");
    console.log(jurisdiction);
    const triggersArray = Array.from(triggers);
    const locationsArray = Array.from(jurisdiction);
    const maxRows = Math.max(triggersArray.length, locationsArray.length);

    // Generate rows for the current key
    for (let i = 0; i < maxRows; i++) {
      rows.push(
        <tr key={`${key}-${i}`}>
          {i === 0 && <td rowSpan={maxRows}>{key}</td>}
          <td>{triggersArray[i] || ""}</td>
          <td>{locationsArray[i] || ""}</td>
        </tr>,
      );
    }
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
        <Table bordered caption="Reportibility Summary">
          <thead>
            <tr>
              <th>Key</th>
              <th>Triggers</th>
              <th>Locations</th>
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
                <div className="grid-col-auto text-pre-line">{value}</div>
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
