import { DisplayData } from "../../utils";
import {
  AccordianSection,
  AccordianH4,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";

interface DemographicsProps {
  demographicsData: DisplayData[];
}

export const demographicsConfig = new SectionConfig("Demographics");

const Demographics = ({ demographicsData }: DemographicsProps) => {
  const renderDemographicsData = (item: any, index: number) => {
    return (
      <div key={index}>
        <div className="grid-row">
          <div className="data-title">{item.title}</div>
          <div className="grid-col-auto maxw7 text-pre-line">{item.value}</div>
        </div>
        <div className={"section__line_gray"} />
      </div>
    );
  };
  return (
    <AccordianSection>
      <AccordianH4>
        <span id={demographicsConfig.id}>{demographicsConfig.title}</span>
      </AccordianH4>
      <AccordianDiv>
        {demographicsData.map((item, index) =>
          renderDemographicsData(item, index),
        )}
      </AccordianDiv>
    </AccordianSection>
  );
};

export default Demographics;
