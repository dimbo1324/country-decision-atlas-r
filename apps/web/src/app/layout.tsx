import type { Metadata } from "next";
import { AppShell } from "../shared/ui/AppShell";
import "./styles.css";

export const metadata: Metadata = {
  title: "Country Decision Atlas",
  description: "A relocation and country decision workspace.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
