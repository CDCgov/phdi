import { DisplayData } from "../../utils";

interface DemographicsProps {
  demographicsData: DisplayData[];
}

const Demographics = ({ demographicsData }: DemographicsProps) => {
  const renderDemographicsData = (item: any, index: number) => {
    return (
      <div key={index}>
        <div className="grid-row">
          <div className="data-title">
            <h4>{item.title}</h4>
          </div>
          <div className="grid-col-auto maxw7 text-pre-line">{item.value}</div>
        </div>
        <div className={"section__line_gray"} />
      </div>
    );
  };
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
            Demographics
          </h3>
          <div className="usa-summary-box__text">
            {demographicsData.map((item, index) =>
              renderDemographicsData(item, index),
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Demographics;
