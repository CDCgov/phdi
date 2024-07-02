import {
  evaluate as fhirPathEvaluate,
  type Model,
  type Path,
  type UserInvocationTable,
} from "fhirpath";
import { Context } from "node:vm";

let cache: { [key: string]: any } = {};

/**
 * Evaluates a FHIRPath expression on the provided FHIR data.
 * @param fhirData - The FHIR data to evaluate the FHIRPath expression on.
 * @param path - The FHIRPath expression to evaluate.
 * @param [context] - Optional context object to provide additional data for evaluation.
 * @param [model] - Optional model object to provide additional data for evaluation.
 * @param [options] - Optional options object for additional configuration.
 * @param [options.resolveInternalTypes] - Whether to resolve internal types in the evaluation.
 * @param [options.traceFn] - Optional trace function for logging evaluation traces.
 * @param [options.userInvocationTable] - Optional table for tracking user invocations.
 * @returns - An array containing the result of the evaluation.
 */
export const evaluate = (
  fhirData: any,
  path: string | Path,
  context?: Context,
  model?: Model,
  options?: {
    resolveInternalTypes?: boolean;
    traceFn?: (value: any, label: string) => void;
    userInvocationTable?: UserInvocationTable;
  },
): any[] => {
  let key =
    JSON.stringify(fhirData) +
    ",,,,," +
    JSON.stringify(context) +
    ",,,,," +
    JSON.stringify(path);
  if (cache.hasOwnProperty(key)) {
    return cache[key];
  }
  cache[key] = fhirPathEvaluate(fhirData, path, context, model, options);
  return cache[key];
};
