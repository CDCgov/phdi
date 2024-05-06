import { registerOTel } from "@vercel/otel";

/**
 * Registers the ecr-viewer service for OpenTelemetry
 * When listening for logs, it will show up as ecr-viewer
 */
export function register() {
  registerOTel({ serviceName: "ecr-viewer" });
}
