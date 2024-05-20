import { NextRequest, NextResponse } from "next/server";
import { trace } from "@opentelemetry/api";

/**
 * Handles GET requests by fetching data from different sources based on the environment configuration.
 * It supports fetching from S3 and Postgres. If the `SOURCE` environment variable is not set to
 * a supported source, it returns a JSON response indicating an invalid source.
 * @param request - The incoming request object provided by Next.js.
 * @returns A promise that resolves to a `NextResponse` object
 *   if the source is invalid, or the result of fetching from the specified source.
 *   The specific return type (e.g., the type returned by `get_s3` or `get_postgres`)
 *   may vary based on the source and is thus marked as `unknown`.
 */
export async function POST(request: NextRequest) {
  const requestBody = await request.json();
  const { startTime, endTime, fhirId } = requestBody;
  const tracer = trace.getTracer("ecr-viewer");
  const timeOnPage = tracer.startSpan("timeOnPage", {
    attributes: {
      timeElapsed: endTime - startTime,
      startTime: startTime,
      endTime: endTime,
      fhirId: fhirId,
    },
  });
  timeOnPage.end();
  return NextResponse.json({ message: "ok" }, { status: 200 });
}
