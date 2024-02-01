import { DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";

interface ClinicalProps {
  activeProblemsDetails: DisplayData[];
  vitalData: DisplayData[]
}

const ClinicalInfo = ({ activeProblemsDetails, vitalData }: ClinicalProps) => {
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

  const renderTableDetails = (tableDetails: DisplayData[]) => {
    return (
      <div>
        {tableDetails.map((item, index) => (
          <div key={index}>
            <div className="grid-col-auto text-pre-line">{item.value}</div>
            <div className={"section__line_gray"} />
          </div>
        ))}
      </div>
    );
  };

  const renderSymptomsProblemsDetails = () => {
    return (
      <>
        <AccordianH3>Symptoms and Problems</AccordianH3>
        <AccordianDiv>{renderTableDetails(activeProblemsDetails)}</AccordianDiv>
      </>
    );
  };

  const renderVitalDetails = () => {
    return (
      <>
        <AccordianH3>Diagnostic and Vital Signs</AccordianH3>
        <AccordianDiv>
          <div className="lh-18">
            {vitalData.map((item, index) => renderData(item, index))}
          </div>
        </AccordianDiv>
      </>
    );
  };


  return (
    <AccordianSection>
      <div className="margin-top-3">
        {activeProblemsDetails.length > 0 && renderSymptomsProblemsDetails()}
        {vitalData.length > 0 && renderVitalDetails()}
      </div>
    </AccordianSection>
  );
};

export default ClinicalInfo;
