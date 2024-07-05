[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/formatService](../README.md) / extractNumbersAndPeriods

# Function: extractNumbersAndPeriods()

> **extractNumbersAndPeriods**(`inputValues`): `string`[]

Extracts and concatenates all sequences of numbers and periods from each string in the input array,
excluding any leading and trailing periods in the first matched sequence of each string.

## Parameters

• **inputValues**: `string`[]

An array of strings from which numbers and periods will be extracted.

## Returns

`string`[]

An array of strings, each corresponding to an input string with all found sequences
of numbers and periods concatenated together, with any leading period in the first sequence removed.

- ['1.2.840.114350.1.13.297.3.7.2.798268.1670845']

## Examples

```ts

```

```ts

```

## Defined in

[src/app/services/formatService.tsx:406](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/formatService.tsx#L406)
