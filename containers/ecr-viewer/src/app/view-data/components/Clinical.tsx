import { DisplayData, renderData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";

interface ClinicalProps {
  activeProblemsDetails: DisplayData[];
  clinicalNotes: DisplayData[];
}

const ClinicalInfo = ({ activeProblemsDetails, clinicalNotes }: ClinicalProps) => {
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
      {clinicalNotes?.length > 0 && (<>
        <AccordianH3>Clinical Notes</AccordianH3>
        <AccordianDiv>{renderData(clinicalNotes)}</AccordianDiv>
      </>)}
      {activeProblemsDetails.length > 0 && renderSymptomsProblemsDetails()}
    </AccordianSection>
  );
};

export default ClinicalInfo;
