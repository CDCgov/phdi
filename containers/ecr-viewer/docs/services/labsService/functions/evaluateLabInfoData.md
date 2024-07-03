[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / evaluateLabInfoData

# Function: evaluateLabInfoData()

> **evaluateLabInfoData**(`fhirBundle`, `labReports`, `mappings`): [`LabReportElementData`](../interfaces/LabReportElementData.md)[]

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing lab and RR data.

• **labReports**: `any`[]

An array of DiagnosticReport objects

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

An object containing the FHIR path mappings.

## Returns

[`LabReportElementData`](../interfaces/LabReportElementData.md)[]

An array of the Diagnostic reports Elements and Organization Display Data

## Defined in

[src/app/services/labsService.tsx:391](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/labsService.tsx#L391)
