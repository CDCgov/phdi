import { DisplayData } from "@/app/utils";

interface UnavailableInfoProps {
  socialUnavailableData: DisplayData[];
  encounterUnavailableData: DisplayData[];
  providerUnavailableData: DisplayData[];
}

const UnavailableInfo = ({
  socialUnavailableData,
  encounterUnavailableData,
  providerUnavailableData,
}: UnavailableInfoProps) => {
  const renderRow = (item: any, index: number) => {
    return (
      <div key={index}>
        <div className="grid-row">
          <div className="data-title font-sans-xs">
            <h4>{item.title}</h4>
          </div>
          <div className="grid-col-auto font-sans-xs">N/A</div>
        </div>
        <div className={"section__line_gray"} />
      </div>
    );
  };
  const renderSection = (sectionTitle: string, data: DisplayData[]) => {
    return (
      <div className="margin-bottom-4">
        <h3
          className="usa-summary-box__heading padding-bottom-205"
          id="summary-box-key-information"
        >
          {sectionTitle}
        </h3>
        <div className="usa-summary-box__text">
          {data.map((item, index) => renderRow(item, index))}
        </div>
      </div>
    );
  };

  return (
    <div className="">
      <div
        className="padding-bottom-3"
        aria-labelledby="summary-box-key-information"
      >
        <div className="usa-summary-box__body">
          {socialUnavailableData.length > 0 &&
            renderSection("Social History", socialUnavailableData)}
          {encounterUnavailableData.length > 0 &&
            renderSection("Encounter Details", encounterUnavailableData)}
          {providerUnavailableData.length > 0 &&
            renderSection("Provider Details", providerUnavailableData)}
        </div>
      </div>
    </div>
  );
};

export default UnavailableInfo;
