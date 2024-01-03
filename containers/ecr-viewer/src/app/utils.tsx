import { Bundle } from "fhir/r4";
import { evaluate } from "fhirpath";
import { fhirPathMappings } from "../../utils/fhirMappings";

export interface DisplayData {
    title: string,
    value: string | undefined
}

export interface PathMappings {
    [key: string]: string;
}


export const formatPatientName = (fhirBundle: Bundle | undefined, fhirPathMappings: PathMappings) => {
    const givenNames = evaluate(fhirBundle, fhirPathMappings.patientGivenName).join(" ");
    const familyName = evaluate(fhirBundle, fhirPathMappings.patientFamilyName);

    return `${givenNames} ${familyName}`;
}

const formatName = (firstName: string, lastName: string) => {
    if (firstName != undefined) {
        return `${firstName} ${lastName}`
    }
    else {
        return undefined
    }
}

export const formatPatientAddress = (fhirBundle: Bundle | undefined, fhirPathMappings: PathMappings) => {
    const streetAddresses = evaluate(fhirBundle, fhirPathMappings.patientStreetAddress).join("\n");
    const city = evaluate(fhirBundle, fhirPathMappings.patientCity);
    const state = evaluate(fhirBundle, fhirPathMappings.patientState);
    const zipCode = evaluate(fhirBundle, fhirPathMappings.patientZipCode);
    const country = evaluate(fhirBundle, fhirPathMappings.patientCountry);
    return (
        `${streetAddresses}
    ${city}, ${state}
    ${zipCode}${country && `, ${country}`}`);
}

const formatAddress = (streetAddresses: string[], city: string, state: string, zipCode: string) => {
    return (
        `${streetAddresses} 
        ${city}, ${state} ${zipCode}`
    );
}

export const formatPatientContactInfo = (fhirBundle: Bundle | undefined, fhirPathMappings: PathMappings) => {
    const phoneNumbers = evaluate(fhirBundle, fhirPathMappings.patientPhoneNumbers).map(phoneNumber => `${phoneNumber?.use?.charAt(0).toUpperCase() + phoneNumber?.use?.substring(1)} ${phoneNumber.value}`).join("\n");
    const emails = evaluate(fhirBundle, fhirPathMappings.patientEmails).map(email => `${email.value}`).join("\n");

    return `${phoneNumbers}
    ${emails}`
}

const formatPhoneNumber = (phoneNumber: string) => {
    try {
        const formattedPhoneNumber = phoneNumber.replace(/\D/g, "").replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
        return formattedPhoneNumber
    } catch {
        return undefined
    }

}

export const evaluateSocialData = (fhirBundle: Bundle | undefined, mappings: PathMappings) => {
    const socialData = [
        {
            'title': 'Occupation',
            'value': evaluate(fhirBundle, mappings['patientCurrentJobTitle'])[0]
        },
        {
            'title': 'Tobacco Use',
            'value': evaluate(fhirBundle, mappings['patientTobaccoUse'])[0]
        },
        {
            'title': 'Travel History',
            'value': evaluate(fhirBundle, mappings['patientTravelHistory'])[0]
        },
        {
            'title': 'Homeless Status',
            'value': evaluate(fhirBundle, mappings['patientHomelessStatus'])[0]
        },
        {
            'title': 'Pregnancy Status',
            'value': evaluate(fhirBundle, mappings['patientPregnancyStatus'])[0]
        },
        {
            'title': 'Alcohol Use',
            'value': evaluate(fhirBundle, mappings['patientAlcoholUse'])[0]
        },
        {
            'title': 'Sexual Orientation',
            'value': evaluate(fhirBundle, mappings['patientSexualOrientation'])[0]
        },
        {
            'title': 'Gender Identity',
            'value': evaluate(fhirBundle, mappings['patientGenderIdentity'])[0]
        },
        {
            'title': 'Occupation',
            'value': evaluate(fhirBundle, mappings['patientCurrentJobTitle'])[0]
        },
    ]
    return evaluateData(socialData)
}

export const evaluateEncounterData = (fhirBundle: Bundle | undefined, mappings: PathMappings) => {
    const encounterData = [
        {
            'title': 'Encounter Type',
            'value': evaluate(fhirBundle, mappings['encounterType'])[0]
        },
        {
            'title': 'Encounter Date',
            'value': evaluate(fhirBundle, mappings['encounterEndDate'])[0]
        },
        {
            'title': 'Facility Name',
            'value': evaluate(fhirBundle, mappings['facilityName'])[0]
        },
        {
            'title': 'Facility Address',
            'value': formatAddress(
                evaluate(fhirBundle, mappings['facilityStreetAddress']),
                evaluate(fhirBundle, mappings['facilityCity'])[0],
                evaluate(fhirBundle, mappings['facilityState'])[0],
                evaluate(fhirBundle, mappings['facilityZipCode'])[0]
            )
        },
        {
            'title': 'Facility Contact',
            'value': formatPhoneNumber(evaluate(fhirBundle, mappings['facilityContact'])[0])
        },
        {
            'title': 'Facility Type',
            'value': evaluate(fhirBundle, mappings['facilityType'])[0]
        },
        {
            'title': 'Facility ID',
            'value': evaluate(fhirBundle, mappings['facilityID'])[0]
        },

    ]
    return evaluateData(encounterData)
}

export const evaluateProviderData = (fhirBundle: Bundle | undefined, mappings: PathMappings) => {
    const providerData = [
        {
            'title': 'Provider Name',
            'value': formatName(
                evaluate(fhirBundle, mappings['providerGivenName'])[0],
                evaluate(fhirBundle, mappings['providerFamilyName'])[0]
            )
        },
        {
            'title': 'Provider Contact',
            'value': formatPhoneNumber(evaluate(fhirBundle, mappings['providerContact'])[0])
        },
    ]
    return evaluateData(providerData)
}

const evaluateData = (data: DisplayData[]) => {
    let availableArray: DisplayData[] = []
    let unavailableArray: DisplayData[] = []
    data.forEach((item) => {
        if (item.value != undefined) {
            availableArray.push(item)
        } else {
            unavailableArray.push(item)
        }
    })
    return { 'available_data': availableArray, 'unavailable_data': unavailableArray }
}