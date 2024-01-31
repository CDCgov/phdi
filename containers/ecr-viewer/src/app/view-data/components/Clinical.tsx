import { DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";

interface ClinicalProps {
  activeProblemsDetails: DisplayData[];
}

const ClinicalInfo = ({ activeProblemsDetails }: ClinicalProps) => {
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

  return (
    <AccordianSection>
      <div className="margin-top-3">
        {activeProblemsDetails.length > 0 && renderSymptomsProblemsDetails()}
      </div>
    </AccordianSection>
  );
};

export default ClinicalInfo;
