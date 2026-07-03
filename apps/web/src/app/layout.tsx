import type { Metadata } from "next";
import { AuthProvider } from "../shared/auth/AuthProvider";
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
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
