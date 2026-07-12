import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import createIntlMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

const intlMiddleware = createIntlMiddleware(routing);

export function middleware(request: NextRequest) {
  // /internal is the ops console (Stage 12 gives it its own shell) — never
  // locale-prefixed, and stays gated exactly as before this stage.
  if (request.nextUrl.pathname.startsWith("/internal")) {
    const appEnv = process.env.APP_ENV ?? "production";
    const isDev = process.env.NODE_ENV === "development";
    if (!isDev && appEnv !== "local") {
      return new NextResponse(null, { status: 404 });
    }
    return NextResponse.next();
  }

  return intlMiddleware(request);
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
