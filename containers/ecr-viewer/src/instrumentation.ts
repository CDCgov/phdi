/**
 * Imports the otel registration
 */
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./app/services/instrumentation");
  }
}
