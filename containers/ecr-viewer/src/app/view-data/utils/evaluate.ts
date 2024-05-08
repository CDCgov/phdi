import { evaluate as fhirPathEvaluate } from "fhirpath";
import getUuidByString from "uuid-by-string";

// let count = 0;
// let totalTime = 0;
// let countPath: {[key: string]: any} = {};
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
  let key = getUuidByString(
    JSON.stringify(fhirData) +
      ",,,,," +
      JSON.stringify(context) +
      ",,,,," +
      JSON.stringify(path),
  );
  if (cache.hasOwnProperty(key)) {
    return cache[key];
  }
  // if(countPath[path as string]){
  //   countPath[path as string].count++;
  // }else{
  //   countPath[path as string] = { count: 1, totalTime: 0 };
  // }
  // const start = performance.now();
  cache[key] = fhirPathEvaluate(fhirData, path, context, model, options);
  // const evaluateTime = performance.now() - start;
  // totalTime += evaluateTime;
  // console.log(`path: ${path}, count: ${count++}, path time: ${evaluateTime}, totalTime: ${totalTime}` );
  // countPath[path as string].totalTime += evaluateTime;
  // console.log(countPath);
  // console.log(cache);
  return cache[key];
};
