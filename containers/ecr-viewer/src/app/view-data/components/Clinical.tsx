import { DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";

interface ClinicalProps {
  activeProblemsDetails: DisplayData[];
  // Other clinical data details will go here
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

  // this is just for Active Problems table -> don't want title and value (table) to appear on same row
  const renderActiveProblemsDetails = () => {
    return (
      <div>
        {activeProblemsDetails.map((item, index) => (
          <div key={index}>
            <div className="data-title">
              <h4>{item.title}</h4>
            </div>
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
        <AccordianDiv>{renderActiveProblemsDetails()}</AccordianDiv>
      </>
    );
  };

  return (
    <AccordianSection>
      {/* <div>{encounterData.length > 0 && renderEncounterDetails()}</div> */}
      <div className="margin-top-3">
        {/* // TODO: renderSymptomsPRoblemsDetails shouldn't depend on just activeProblemsDetails */}
        {activeProblemsDetails.length > 0 && renderSymptomsProblemsDetails()}
      </div>
    </AccordianSection>
  );
};

export default ClinicalInfo;
