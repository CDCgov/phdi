[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / evaluateOrganismsReportData

# Function: evaluateOrganismsReportData()

> **evaluateOrganismsReportData**(`report`, `fhirBundle`, `mappings`): `undefined` \| `Element`

## Parameters

• **report**: [`LabReport`](../interfaces/LabReport.md)

An object containing an array of lab result references. If it exists, one of the Observations in the report will contain all the lab organisms table data.

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing diagnostic report data.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

An object containing the FHIR path mappings.

## Returns

`undefined` \| `Element`

- An array of React elements representing the lab organisms table.

## Defined in

[src/app/services/labsService.tsx:339](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/labsService.tsx#L339)
