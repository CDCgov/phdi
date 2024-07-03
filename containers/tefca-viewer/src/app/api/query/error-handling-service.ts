import { OperationOutcome } from "fhir/r4";

export async function handleRequestError(
  diagnostics_message: string
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
