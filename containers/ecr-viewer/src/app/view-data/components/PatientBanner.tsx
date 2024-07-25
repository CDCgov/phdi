import { evaluatePatientName } from "@/app/services/evaluateFhirDataService";
import { formatDate } from "@/app/services/formatService";
import { PathMappings } from "@/app/utils";
import { Bundle } from "fhir/r4";

import { evaluate } from "fhirpath";

interface PatientBannerProps {
  bundle: Bundle;
  mappings: PathMappings;
}

/**
 * Generates a JSX element to display patient name and date of birth in a sticky banner. Only shown in the integrated viewer.
 * @param props - Properties for the Patient Banner
 * @param props.bundle - The FHIR bundle containing the patient data
 * @param props.mappings - The path mappings for the FHIR bundle
 * @returns a react element for Patient Banner
 */
const PatientBanner = ({ bundle, mappings }: PatientBannerProps) => {
  if (process.env.STANDALONE_VIEWER) {
    return;
  } else {
    return (
      <div className="patient-banner">
        <span className="patient-banner-name">
          {evaluatePatientName(bundle, mappings)}
        </span>
        <span className=".patient-banner-dob">
          {formatDate(evaluate(bundle, mappings.patientDOB)[0]) || ""}
        </span>
      </div>
    );
  }
};

export default PatientBanner;
