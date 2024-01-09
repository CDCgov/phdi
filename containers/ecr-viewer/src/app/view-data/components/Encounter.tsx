import { DisplayData } from "@/app/utils";

interface EncounterProps {
  encounterData: DisplayData[];
  providerData: DisplayData[];
}

const EncounterDetails = ({ encounterData, providerData }: EncounterProps) => {
  const combineData = () => {
    const combinedData = encounterData.slice();
    combinedData.splice(2, 0, ...providerData);
    return combinedData;
  };

  const renderData = (item: any, index: number) => {
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

  const renderEncounterDetails = () => {
    return (
      <div>
        <h3
          className="usa-summary-box__heading padding-y-105"
          id="summary-box-key-information"
        >
          Encounter Details
        </h3>

        <div className="usa-summary-box__text">
          {encounterData.map((item, index) => renderData(item, index))}
        </div>
      </div>
    );
  };

  const renderProviderDetails = () => {
    return (
      <div>
        <h3
          className="usa-summary-box__heading padding-y-105"
          id="summary-box-key-information"
        >
          Provider Details
        </h3>
        <div className="usa-summary-box__text">
          {providerData.map((item, index) => renderData(item, index))}
        </div>
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
          <div>{encounterData.length > 0 && renderEncounterDetails()}</div>
          <div className="margin-top-3">
            {providerData.length > 0 && renderProviderDetails()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EncounterDetails;
