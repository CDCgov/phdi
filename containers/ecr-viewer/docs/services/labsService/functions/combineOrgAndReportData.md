[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / combineOrgAndReportData

# Function: combineOrgAndReportData()

> **combineOrgAndReportData**(`organizationElements`, `fhirBundle`, `mappings`): [`LabReportElementData`](../interfaces/LabReportElementData.md)[]

## Parameters

• **organizationElements**: [`ResultObject`](../interfaces/ResultObject.md)

Object contianing the keys of org data, values of the diagnostic report elements

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing lab and RR data.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

An object containing the FHIR path mappings.

## Returns

[`LabReportElementData`](../interfaces/LabReportElementData.md)[]

An array of the Diagnostic reports Elements and Organization Display Data

## Defined in

[src/app/services/labsService.tsx:524](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/labsService.tsx#L524)
