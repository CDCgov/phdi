import { DisplayData } from "@/app/utils";
import {
  AccordianSection,
  AccordianH3,
  AccordianDiv,
} from "../component-utils";

interface UnavailableInfoProps {
  demographicsUnavailableData: DisplayData[];
  socialUnavailableData: DisplayData[];
  encounterUnavailableData: DisplayData[];
  clinicalUnavailableData: DisplayData[];
  providerUnavailableData: DisplayData[];
  activeProblemsUnavailableData: DisplayData[];
}

const UnavailableInfo = ({
  demographicsUnavailableData,
  socialUnavailableData,
  encounterUnavailableData,
  clinicalUnavailableData,
  providerUnavailableData,
  activeProblemsUnavailableData,
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
    <AccordianSection>
      {demographicsUnavailableData?.length > 0 &&
        renderSection("Demographics", demographicsUnavailableData)}
      {socialUnavailableData?.length > 0 &&
        renderSection("Social History", socialUnavailableData)}
      {encounterUnavailableData?.length > 0 &&
        renderSection("Encounter Details", encounterUnavailableData)}
      {clinicalUnavailableData.length > 0 &&
        renderSection("Clinical Info", clinicalUnavailableData)}
      {providerUnavailableData.length > 0 &&
        renderSection("Provider Details", providerUnavailableData)}
      {activeProblemsUnavailableData?.length > 0 && // Add other items under symptoms and problems here
        renderSection("Symptoms and Problems", activeProblemsUnavailableData)}
    </AccordianSection>
  );
};

export default UnavailableInfo;
