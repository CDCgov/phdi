[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/labsService](../README.md) / evaluateObservationTable

# Function: evaluateObservationTable()

> **evaluateObservationTable**(`report`, `fhirBundle`, `mappings`, `columnInfo`): `React.JSX.Element` \| `undefined`

Evaluates and generates a table of observations based on the provided DiagnosticReport,
FHIR bundle, mappings, and column information.

## Parameters

• **report**: [`LabReport`](../interfaces/LabReport.md)

The DiagnosticReport containing observations to be evaluated.

• **fhirBundle**: `Bundle`\<`FhirResource`\>

The FHIR bundle containing observation data.

• **mappings**: [`PathMappings`](../../../utils/interfaces/PathMappings.md)

An object containing the FHIR path mappings.

• **columnInfo**: [`ColumnInfoInput`](../../../utils/interfaces/ColumnInfoInput.md)[]

An array of column information objects specifying column names and information paths.

## Returns

`React.JSX.Element` \| `undefined`

The JSX representation of the evaluated observation table, or undefined if there are no observations.

## Defined in

[src/app/services/labsService.tsx:269](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/labsService.tsx#L269)
