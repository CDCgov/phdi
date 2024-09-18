import { Mode } from "@/app/constants";
import {
  StepIndicator as TrussStepIndicator,
  StepIndicatorStep,
  HeadingLevel,
} from "@trussworks/react-uswds";
import styles from "./stepIndicator.module.css";

type StepIndicatorProps = {
  headingLevel: HeadingLevel;
  curStep: Mode;
};
type StepStatus = "current" | "complete" | "incomplete";

export const CUSTOMIZE_QUERY_STEPS: { [mode: string]: string } = {
  search: "Enter patient info",
  "select-query": "Select query",
  "multiple-patients-results": "Select patient",
  results: "View patient record",
};

const StepIndicator: React.FC<StepIndicatorProps> = ({
  headingLevel,
  curStep,
}) => {
  const stepArray = Object.keys(CUSTOMIZE_QUERY_STEPS).map((key, index) => {
    return { [key]: index };
  });
  const stepOrder = Object.assign({}, ...stepArray);

  return (
    <TrussStepIndicator
      headingLevel={headingLevel}
      counters="default"
      className={`custom-query-step-indicator ${styles.container}`}
    >
      {Object.values(CUSTOMIZE_QUERY_STEPS).map((label, index) => {
        let status = "incomplete";
        if (stepOrder[curStep] === index) {
          status = "current";
        } else if (stepOrder[curStep] > index) {
          status = "complete";
        }
        return (
          <StepIndicatorStep label={label} status={status as StepStatus} />
        );
      })}
    </TrussStepIndicator>
  );
};

export default StepIndicator;
