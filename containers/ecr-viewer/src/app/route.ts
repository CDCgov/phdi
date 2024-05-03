import { NextResponse } from "next/server";

/**
 * Health check for ECR Viewer
 * @returns Response with status OK.
 */
export async function GET() {
  return NextResponse.json({ status: "OK" }, { status: 200 });
}
