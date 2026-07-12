import { EmptyState as EmptyStateShell } from "@country-decision-atlas/ui";

type EmptyStateProps = {
  message?: string;
};

export function EmptyState({
  message = "Данные отсутствуют.",
}: EmptyStateProps) {
  return <EmptyStateShell message={message} />;
}
