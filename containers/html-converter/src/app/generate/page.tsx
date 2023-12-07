import {evaluate} from "fhirpath";
import fs from "fs";
import {parse} from "yaml";
import {Bundle} from "fhir/r4";

interface EcrViewerProps {
    fhirBundle: any
}
const EcrViewer = (
    // {fhirBundle}: EcrViewerProps
) => {
    const file = fs.readFileSync('./src/app/generate/fhirPath.yml', 'utf8').toString();
    const fhirBundle: Bundle = JSON.parse(fs.readFileSync('./src/app/generate/exampleBundle.json', 'utf8').toString());
    const fhirPathMappings = parse(file);
    return <div>
        <h3>About the patient</h3>
        <b>Patient Name</b> { evaluate(fhirBundle, fhirPathMappings.patientGivenName).join(" ") } { evaluate(fhirBundle, fhirPathMappings.patientFamilyName) }
        <br />
        <b>Patient Address</b> { evaluate(fhirBundle, fhirPathMappings.patientStreetAddress).join(" ") } { evaluate(fhirBundle, fhirPathMappings.patientCity) } { evaluate(fhirBundle, fhirPathMappings.patientState) } { evaluate(fhirBundle, fhirPathMappings.patientZipCode) }
        <br />
        <b>Patient Contact</b> { evaluate(fhirBundle, fhirPathMappings.patientPhoneNumbers).map(phoneNumber => { return `tel: (${phoneNumber.use}) ${phoneNumber.value}`}).join(" ") } { evaluate(fhirBundle, fhirPathMappings.patientEmails).map(email => { return `email: ${email.value}`}).join(" ") }
    </div>;
};

export default EcrViewer;