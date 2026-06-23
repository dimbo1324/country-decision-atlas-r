import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const appEnv = process.env.APP_ENV ?? "production";
  if (appEnv !== "local" && request.nextUrl.pathname.startsWith("/internal")) {
    return new NextResponse(null, { status: 404 });
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/internal/:path*"],
};
