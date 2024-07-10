import { OperationOutcome } from "fhir/r4";

/**
 * Handles a request error by returning an OperationOutcome with a diagnostics message.
 * @param diagnostics_message - The message to be included in the `diagnostics` section
 * of the OperationOutcome.
 * @returns OperationOutcome with the included error message.
 */
export async function handleRequestError(
  diagnostics_message: string,
): Promise<OperationOutcome> {
  const OperationOutcome: OperationOutcome = {
    resourceType: "OperationOutcome",
    issue: [
      {
        severity: "error",
        code: "invalid",
        diagnostics: diagnostics_message,
      },
    ],
  };
  return OperationOutcome;
}
