import { DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";
import { SectionConfig } from "./SideNav";

interface ClinicalProps {
  clinicalData: DisplayData[];
}

export const clinicalInfoConfig: SectionConfig = new SectionConfig(
  "Clinical Info",
  ["Symptoms and Problems"],
);

const ClinicalInfo = ({ clinicalData }: ClinicalProps) => {
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

  const renderSymptomsAndProblems = () => {
    return (
      <>
        <AccordianH3>Symptoms and Problems</AccordianH3>
        <AccordianDiv>
          {clinicalData.map((item, index) => renderData(item, index))}
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      <div>{clinicalData.length > 0 && renderSymptomsAndProblems()}</div>
    </AccordianSection>
  );
};

export default ClinicalInfo;
