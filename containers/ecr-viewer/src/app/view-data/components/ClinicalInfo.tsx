import { DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";

interface ClinicalInfoProps {
  vitalData: DisplayData[];
}

const ClinicalInfo = ({ vitalData }: ClinicalInfoProps) => {
  console.log("vital data", vitalData);

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

  const renderVitalDetails = () => {
    return (
      <>
        <AccordianH3>Diagnostic and Vital Signs</AccordianH3>
        <AccordianDiv>
          <div className="lh-24">
            {vitalData.map((item, index) => renderData(item, index))}
          </div>
        </AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      <div className="">{vitalData.length > 0 && renderVitalDetails()}</div>
    </AccordianSection>
  );
};

export default ClinicalInfo;
