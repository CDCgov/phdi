[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / evaluateDiagnosticReportData

# Function: evaluateDiagnosticReportData()

> **evaluateDiagnosticReportData**(`labReportJson`, `report`, `fhirBundle`, `mappings`): `undefined` \| `Element`

## Parameters

• **labReportJson**: [`TableJson`](../../formatService/interfaces/TableJson.md)

A JSON object representing the lab report HTML string

• **report**: [`LabReport`](../interfaces/LabReport.md)

An object containing an array of result references.

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing diagnostic report data.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

An object containing the FHIR path mappings.

## Returns

`undefined` \| `Element`

- An array of React elements representing the lab observations.

## Defined in

[src/app/services/labsService.tsx:306](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/labsService.tsx#L306)
