[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/formatService](../README.md) / formatVitals

# Function: formatVitals()

> **formatVitals**(`heightAmount`, `heightUnit`, `weightAmount`, `weightUnit`, `bmi`): `string`

## Parameters

• **heightAmount**: `string`

The amount of height.

• **heightUnit**: `string`

The measurement type of height (e.g., "[in_i]" for inches, "cm" for centimeters).

• **weightAmount**: `string`

The amount of weight.

• **weightUnit**: `string`

The measurement type of weight (e.g., "[lb_av]" for pounds, "kg" for kilograms).

• **bmi**: `string`

The Body Mass Index (BMI).

## Returns

`string`

The formatted vital signs information.

## Defined in

[src/app/services/formatService.tsx:262](https://github.com/CDCgov/phdi/blob/55d1a87d29da9da2522ba2a73bc122cba666b133/containers/ecr-viewer/src/app/services/formatService.tsx#L262)
