import { DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";

interface EncounterProps {
  encounterData: DisplayData[];
  providerData: DisplayData[];
}

export const encounterConfig: SectionConfig = new SectionConfig(
  "Encounter Details",
  ["Encounter Details", "Provider Details"],
);

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
      <>
        <AccordianH3>
          <span id={encounterConfig.subNavItems?.[0].id}>
            {encounterConfig.subNavItems?.[0].title}
          </span>
        </AccordianH3>
        <AccordianDiv>
          {encounterData.map((item, index) => renderData(item, index))}
        </AccordianDiv>
      </>
    );
  };

  const renderProviderDetails = () => {
    return (
      <>
        <AccordianH3>
          <span id={encounterConfig.subNavItems?.[1].id}>
            {encounterConfig.subNavItems?.[1].title}
          </span>
        </AccordianH3>
        <AccordianDiv>
          {providerData.map((item, index) => renderData(item, index))}
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      <div>{encounterData.length > 0 && renderEncounterDetails()}</div>
      <div className="margin-top-3">
        {providerData.length > 0 && renderProviderDetails()}
      </div>
    </AccordianSection>
  );
};

export default EncounterDetails;
