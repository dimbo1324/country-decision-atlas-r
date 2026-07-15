import type { Metadata } from "next";
import { getLocale } from "next-intl/server";
import {
  BackgroundFX,
  BackgroundTexture,
  Toaster,
} from "@country-decision-atlas/ui";
import { AuthProvider } from "../shared/auth/AuthProvider";
import { crimsonText, imFellEnglish, playfairDisplay } from "./fonts";
import { Providers } from "./providers";
import "@country-decision-atlas/ui/theme.css";
import "./theme-vars.css";

export const metadata: Metadata = {
  title: "Country Decision Atlas",
  description: "Платформа для сравнения стран и принятия решений о переезде.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();

  return (
    <html
      lang={locale}
      className={`${playfairDisplay.variable} ${crimsonText.variable} ${imFellEnglish.variable}`}
    >
      <body>
        <BackgroundTexture />
        <BackgroundFX />
        <Providers>
          <AuthProvider>{children}</AuthProvider>
        </Providers>
        <Toaster />
      </body>
    </html>
  );
}
