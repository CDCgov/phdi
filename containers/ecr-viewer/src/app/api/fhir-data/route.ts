import { NextRequest, NextResponse } from "next/server";
import { get_s3, get_postgres } from "./fhir-data-service";

const S3_SOURCE = "s3";
const POSTGRES_SOURCE = "postgres";

export async function GET(request: NextRequest) {
  if (process.env.SOURCE === S3_SOURCE) {
    return get_s3(request);
  } else if (process.env.SOURCE === POSTGRES_SOURCE) {
    return await get_postgres(request);
  } else {
    return NextResponse.json({ message: "Invalid source" }, { status: 500 });
  }
}
