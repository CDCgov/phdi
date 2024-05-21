/**
 * Registers the ecr-viewer service for OpenTelemetry
 * When listening for logs, it will show up as ecr-viewer
 */
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./app/services/instrumentation");
  }
}
