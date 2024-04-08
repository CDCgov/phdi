import { NextRequest, NextResponse } from "next/server";
import { get_s3, get_postgres } from "./fhir-data-service";

const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";

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
export async function GET(request: NextRequest) {
  if (process.env.SOURCE === S3_SOURCE) {
    return get_s3(request);
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    return await get_postgres(request);
  } else {
    return NextResponse.json({ message: "Invalid source" }, { status: 500 });
  }
}
