import { AppHeader } from "./AppHeader";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="appShell">
      <AppHeader />
      <main className="appMain">{children}</main>
    </div>
  );
}
