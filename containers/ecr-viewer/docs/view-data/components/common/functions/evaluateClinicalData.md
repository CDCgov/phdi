[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/components/common](../README.md) / evaluateClinicalData

# Function: evaluateClinicalData()

> **evaluateClinicalData**(`fhirBundle`, `mappings`): `object`

## Parameters

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing clinical data.

• **mappings**: [`PathMappings`](../../../../utils/interfaces/PathMappings.md)

The object containing the fhir paths.

## Returns

`object`

An object containing evaluated and formatted clinical data.

### activeProblemsDetails

> **activeProblemsDetails**: [`CompleteData`](../../../../utils/interfaces/CompleteData.md)

### clinicalNotes

> **clinicalNotes**: [`CompleteData`](../../../../utils/interfaces/CompleteData.md)

### immunizationsDetails

> **immunizationsDetails**: [`CompleteData`](../../../../utils/interfaces/CompleteData.md)

### reasonForVisitDetails

> **reasonForVisitDetails**: [`CompleteData`](../../../../utils/interfaces/CompleteData.md)

### treatmentData

> **treatmentData**: [`CompleteData`](../../../../utils/interfaces/CompleteData.md)

### vitalData

> **vitalData**: [`CompleteData`](../../../../utils/interfaces/CompleteData.md)

## Defined in

[src/app/view-data/components/common.tsx:507](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/view-data/components/common.tsx#L507)
