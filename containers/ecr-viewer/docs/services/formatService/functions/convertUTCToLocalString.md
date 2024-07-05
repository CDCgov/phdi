[**ecr-viewer**](../../../README.md) • **Docs**

***

[ecr-viewer](../../../README.md) / [services/formatService](../README.md) / convertUTCToLocalString

# Function: convertUTCToLocalString()

> **convertUTCToLocalString**(`utcDateString`): `string`

Converts a UTC date time string to the date string in the user's local timezone.
Returned date is in format "MM/DD/YYYY HH:MM AM/PM Z" where "Z" is the timezone abbreviation

## Parameters

• **utcDateString**: `string`

The date string in UTC to be converted.

## Returns

`string`

The formatted date string converted to the user's local timezone.

## Throws

If the input UTC date string is invalid.

## Defined in

[src/app/services/formatService.tsx:153](https://github.com/CDCgov/phdi/blob/fa63a85e5b4651bdfc0d25ecc23a67e11fbcba18/containers/ecr-viewer/src/app/services/formatService.tsx#L153)
