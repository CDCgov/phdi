import { DisplayData } from "../../utils";
import { Fragment } from "react";

import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";

interface EcrMetadataProps {
  rrDetails: DisplayData[];
  eicrDetails: DisplayData[];
  eCRSenderDetails: DisplayData[];
}

const EcrMetadata = ({
  rrDetails,
  eicrDetails,
  eCRSenderDetails,
}: EcrMetadataProps) => {
  return (
      <AccordianSection>
        <AccordianH3>
          RR Details
        </AccordianH3>
          <AccordianDiv>
            {rrDetails.map(({ title, value }) => {
              return (
                <Fragment key={title}>
                  <div className="grid-row">
                    <div className="data-title">
                      <h4>{title}</h4>
                    </div>
                    <div className="grid-col-fill">{value}</div>
                  </div>
                  <div className={"section__line_gray"} />
                </Fragment>
              );
            })}
            <div className={"padding-bottom-1"} />
            <AccordianH3>
              eICR Details
            </AccordianH3>
            {eicrDetails.map(({ title, value }) => {
              return (
                <Fragment key={title}>
                  <div className="grid-row">
                    <div className="data-title">
                      <h4>{title}</h4>
                    </div>
                    <div className="grid-col-auto">{value}</div>
                  </div>
                  <div className={"section__line_gray"} />
                </Fragment>
              );
            })}
            <div className={"padding-bottom-1"} />
            <AccordianH3>
              eCR Sender Details
            </AccordianH3>
            {eCRSenderDetails.map(({ title, value }) => {
              return (
                <Fragment key={title}>
                  <div className="grid-row">
                    <div className="data-title">
                      <h4>{title}</h4>
                    </div>
                    <div className="grid-col-auto">{value}</div>
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
