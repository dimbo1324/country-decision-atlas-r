import { Suspense } from "react";
import { AppHeader } from "./AppHeader";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="appShell">
      <Suspense fallback={null}>
        <AppHeader />
      </Suspense>
      <main className="appMain">{children}</main>
    </div>
  );
}
