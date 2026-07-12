import type { Metadata } from "next";
import {
  BackgroundFX,
  BackgroundTexture,
  Toaster,
} from "@country-decision-atlas/ui";
import { AuthProvider } from "../shared/auth/AuthProvider";
import { AppShell } from "../shared/ui/AppShell";
import { crimsonText, imFellEnglish, playfairDisplay } from "./fonts";
import "./styles.css";
import "@country-decision-atlas/ui/theme.css";
import "./theme-vars.css";

export const metadata: Metadata = {
  title: "Country Decision Atlas",
  description: "Платформа для сравнения стран и принятия решений о переезде.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ru"
      className={`${playfairDisplay.variable} ${crimsonText.variable} ${imFellEnglish.variable}`}
    >
      <body>
        <BackgroundTexture />
        <BackgroundFX />
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
        <Toaster />
      </body>
    </html>
  );
}
