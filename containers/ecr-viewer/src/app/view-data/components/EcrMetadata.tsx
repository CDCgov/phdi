import {
  DisplayData,
} from "../../utils";
import { Fragment } from "react";

interface EcrMetadataProps {
  rrDetails: DisplayData[],
  eicrDetails: DisplayData[],
  eCRSenderDetails: DisplayData[]
}

const EcrMetadata = ({rrDetails, eicrDetails, eCRSenderDetails}: EcrMetadataProps) => {
  return (
    <div>
      <div
        className="padding-bottom-3"
        aria-labelledby="summary-box-key-information"
      >
        <div className="usa-summary-box__body">
          <h3
            className="usa-summary-box__heading padding-y-105"
            id="summary-box-key-information"
          >
            eICR Details
          </h3>
          <div className="usa-summary-box__text">
            {eicrDetails.map(({title, value}) => {
              return (<div className="grid-row" key={title}>
                <div className="data-title">
                  <h4>{title}</h4>
                </div>
                <div className="grid-col-auto">
                  {value}
                </div>
              </div>)
            })}
            <div className={"section__line_gray padding-bottom-3"} />
            <h3
              className="usa-summary-box__heading padding-y-105"
              id="summary-box-key-information"
            >
              eCR Sender Details
            </h3>
            {eCRSenderDetails.map(({title, value}) => {
              return (<Fragment key={title}>
                  <div className="grid-row">
                  <div className="data-title">
                    <h4>{title}</h4>
                  </div>
                  <div className="grid-col-auto">
                    {value}
                  </div>
                </div>
                <div className={"section__line_gray"} />
              </Fragment>)
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EcrMetadata;
