import { evaluate } from "fhirpath";
import { Bundle } from "fhir/r4";

interface EcrViewerProps {
  fhirPathMappings: PathMappings;
  fhirBundle: Bundle;
}

interface PathMappings {
  [key: string]: string;
}

const patientAddress = (fhirBundle: Bundle, fhirPathMappings: PathMappings) => {
  const streetAddresses = evaluate(
    fhirBundle,
    fhirPathMappings.patientStreetAddress,
  ).join("\n");
  const city = evaluate(fhirBundle, fhirPathMappings.patientCity);
  const state = evaluate(fhirBundle, fhirPathMappings.patientState);
  const zipCode = evaluate(fhirBundle, fhirPathMappings.patientZipCode);

  return `${streetAddresses}
    ${city} ${state}
    ${zipCode}, USA`;
};

const patientName = (fhirBundle: Bundle, fhirPathMappings: PathMappings) => {
  const givenNames = evaluate(
    fhirBundle,
    fhirPathMappings.patientGivenName,
  ).join(" ");
  const familyName = evaluate(fhirBundle, fhirPathMappings.patientFamilyName);

  return `${givenNames} ${familyName}`;
};

const patientContactInfo = (
  fhirBundle: Bundle,
  fhirPathMappings: PathMappings,
) => {
  const phoneNumbers = evaluate(
    fhirBundle,
    fhirPathMappings.patientPhoneNumbers,
  )
    .map((phoneNumber) => `tel: (${phoneNumber.use}) ${phoneNumber.value}`)
    .join("\n");
  const emails = evaluate(fhirBundle, fhirPathMappings.patientEmails)
    .map((email) => `email: ${email.value}`)
    .join("\n");

  return `${phoneNumbers}
    ${emails}`;
};

const EcrSummary = ({ fhirPathMappings, fhirBundle }: EcrViewerProps) => {
  return (
    <div>
      <h2>Quick eCR Summary</h2>
      <div
        className="usa-summary-box padding-3"
        aria-labelledby="summary-box-key-information"
      >
        <div className="usa-summary-box__body">
          <h3
            className="usa-summary-box__heading padding-top-105 padding-bottom-1"
            id="summary-box-key-information"
          >
            About the Patient
          </h3>
          <div className="usa-summary-box__text">
            <div className="grid-row">
              <div className="grid-col-2 text-bold">Patient Name</div>
              <div className="grid-col-auto">
                {patientName(fhirBundle, fhirPathMappings)}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="grid-col-2 text-bold">Patient Address</div>
              <div className="grid-col-auto text-pre-line">
                {patientAddress(fhirBundle, fhirPathMappings)}
              </div>
            </div>
            <div className={"section__line"} />
            <div className="grid-row">
              <div className="grid-col-2 text-bold">Patient Contact</div>
              <div className="grid-col-auto text-pre-line">
                {patientContactInfo(fhirBundle, fhirPathMappings)}
              </div>
            </div>
            <div className={"section__line"} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EcrSummary;
