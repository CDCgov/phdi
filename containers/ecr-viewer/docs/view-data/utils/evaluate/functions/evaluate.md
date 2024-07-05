[**ecr-viewer**](../../../../README.md) • **Docs**

***

[ecr-viewer](../../../../README.md) / [view-data/utils/evaluate](../README.md) / evaluate

# Function: evaluate()

> **evaluate**(`fhirData`, `path`, `context`?, `model`?, `options`?): `any`[]

## Parameters

• **fhirData**: `any`

The FHIR data to evaluate the FHIRPath expression on.

• **path**: `string` \| `Path`

The FHIRPath expression to evaluate.

• **context?**: `Context`

Optional context object to provide additional data for evaluation.

• **model?**: `Model`

Optional model object to provide additional data for evaluation.

• **options?**

Optional options object for additional configuration.

• **options.resolveInternalTypes?**: `boolean`

Whether to resolve internal types in the evaluation.

• **options.traceFn?**

Optional trace function for logging evaluation traces.

• **options.userInvocationTable?**: `UserInvocationTable`

Optional table for tracking user invocations.

## Returns

`any`[]

- An array containing the result of the evaluation.

## Defined in

[src/app/view-data/utils/evaluate.ts:17](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/view-data/utils/evaluate.ts#L17)
