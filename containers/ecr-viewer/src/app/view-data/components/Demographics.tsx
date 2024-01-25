import { DisplayData } from "../../utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";

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
    <AccordianSection>
      <AccordianH3>
        <span id="demographics">Demographics</span>
      </AccordianH3>
      <AccordianDiv>
        {demographicsData.map((item, index) =>
          renderDemographicsData(item, index),
        )}
      </AccordianDiv>
    </AccordianSection>
  );
};

export default Demographics;
