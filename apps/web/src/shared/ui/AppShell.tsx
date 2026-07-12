import { Suspense } from "react";
import { AppFooter } from "./AppFooter";
import { AppHeader } from "./AppHeader";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="relative z-[1] flex min-h-screen flex-col">
      <Suspense fallback={null}>
        <AppHeader />
      </Suspense>
      <main className="mx-auto w-full max-w-[1400px] flex-1 px-6 py-8">
        {children}
      </main>
      <AppFooter />
    </div>
  );
}
