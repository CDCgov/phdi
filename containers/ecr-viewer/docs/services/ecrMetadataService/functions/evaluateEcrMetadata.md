[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/ecrMetadataService](../README.md) / evaluateEcrMetadata

# Function: evaluateEcrMetadata()

> **evaluateEcrMetadata**(`fhirBundle`, `mappings`): `object`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing eCR metadata.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

`object`

An object containing evaluated and formatted eCR metadata.

### ecrSenderDetails

> **ecrSenderDetails**: [`CompleteData`](../../../utils/interfaces/CompleteData.md)

### eicrDetails

> **eicrDetails**: [`CompleteData`](../../../utils/interfaces/CompleteData.md)

### rrDetails

> **rrDetails**: [`ReportableConditions`](../interfaces/ReportableConditions.md) = `reportableConditionsList`

## Defined in

[src/app/services/ecrMetadataService.ts:20](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/ecrMetadataService.ts#L20)
