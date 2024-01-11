import { evaluate } from "fhirpath";
import { Bundle } from "fhir/r4";
import {
  extractFacilityAddress,
  extractFacilityContactInfo,
  PathMappings,
} from "../../utils";

interface EcrMetadataProps {
  fhirPathMappings: PathMappings;
  fhirBundle: Bundle | undefined;
}

const EcrMetadata = ({ fhirPathMappings, fhirBundle }: EcrMetadataProps) => {
  return (
    <div>
      <div
        className="padding-bottom-3"
        aria-labelledby="summary-box-key-information"
      >
        <div className="usa-summary-box__body">
          <h3
            className="usa-summary-box__heading padding-y-105"
            id="summary-box-key-information"
          >
            eICR Details
          </h3>
          <div className="usa-summary-box__text">
            <div className="grid-row">
              <div className="data-title">
                <h4>eICR Identifier</h4>
              </div>
              <div className="grid-col-auto">
                {evaluate(fhirBundle, fhirPathMappings.eicrIdentifier)}
              </div>
            </div>
            <div className={"section__line_gray padding-bottom-3"} />
            <h3
              className="usa-summary-box__heading padding-y-105"
              id="summary-box-key-information"
            >
              eCR Sender Details
            </h3>
            <div className="grid-row">
              <div className="data-title">
                <h4>Date/Time eCR Created</h4>
              </div>
              <div className="grid-col-auto">
                {evaluate(fhirBundle, fhirPathMappings.dateTimeEcrCreated)}
              </div>
            </div>
            <div className={"section__line_gray"} />
            <div className="grid-row">
              <div className="data-title">
                <h4>Sender Software</h4>
              </div>
              <div className="grid-col-auto">
                {evaluate(fhirBundle, fhirPathMappings.senderSoftware)}
              </div>
            </div>
            <div className={"section__line_gray"} />
            <div className="grid-row">
              <div className="data-title">
                <h4>Sender Facility Name</h4>
              </div>
              <div className="grid-col-auto">
                {evaluate(fhirBundle, fhirPathMappings.senderFacilityName)}
              </div>
            </div>
            <div className={"section__line_gray"} />
            <div className="grid-row">
              <div className="data-title">
                <h4>Facility Address</h4>
              </div>
              <div className="grid-col-auto">
                {extractFacilityAddress(fhirBundle, fhirPathMappings)}
              </div>
            </div>
            <div className={"section__line_gray"} />
            <div className="grid-row">
              <div className="data-title">
                <h4>Facility Contact</h4>
              </div>
              <div className="grid-col-auto">
                {evaluate(fhirBundle, fhirPathMappings.facilityContact)}
              </div>
            </div>
            <div className={"section__line_gray"} />
            <div className="grid-row">
              <div className="data-title">
                <h4>Facility ID</h4>
              </div>
              <div className="grid-col-auto">
                {evaluate(fhirBundle, fhirPathMappings.facilityID)}
              </div>
            </div>
            <div className={"section__line_gray"} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EcrMetadata;
