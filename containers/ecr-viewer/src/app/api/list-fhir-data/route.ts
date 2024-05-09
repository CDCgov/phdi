import { NextResponse } from "next/server";
import { list_s3, list_postgres } from "./list-fhir-data-service";

const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";

/**
 * Handles GET requests by fetching data from different sources based on the environment configuration.
 * It supports fetching from S3 and Postgres. If the `SOURCE` environment variable is not set to
 * a supported source, it returns a JSON response indicating an invalid source.
 * @returns A promise that resolves to a `NextResponse` object
 *   if the source is invalid, or the result of fetching from the specified source.
 *   The specific return type (e.g., the type returned by `get_s3` or `get_postgres`)
 *   may vary based on the source and is thus marked as `unknown`.
 */
export async function GET() {
  if (process.env.SOURCE === S3_SOURCE) {
    return list_s3();
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    return await list_postgres();
  } else {
    return NextResponse.json({ message: "Invalid source" }, { status: 500 });
  }
}
