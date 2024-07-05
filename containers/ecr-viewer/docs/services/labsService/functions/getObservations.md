[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / getObservations

# Function: getObservations()

> **getObservations**(`report`, `fhirBundle`, `mappings`): `Observation`[]

## Parameters

• **report**: [`LabReport`](../interfaces/LabReport.md)

The lab report containing the results to be processed.

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing related resources for the lab report.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

An object containing paths to relevant fields within the FHIR resources.

## Returns

`Observation`[]

An array of `Observation` resources from the FHIR bundle that correspond to the
given references. If no matching observations are found or if the input references array is empty, an empty array
is returned.

## Defined in

[src/app/services/labsService.tsx:42](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/labsService.tsx#L42)
