import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function POST(request: NextRequest) {
  cookies().set({
    name: "authorization",
    value: request.headers.get("authorization") || "",
    httpOnly: true,
  });
  return NextResponse.json({}, { status: 200 });
}
