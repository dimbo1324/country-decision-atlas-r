import type { Metadata } from "next";
import { AppShell } from "../shared/ui/AppShell";
import "./styles.css";

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
    <html lang="ru">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
