/**
 * Imports the otel registration
 */
export async function register() {
  let a = "a";
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./app/services/instrumentation");
  }
}
