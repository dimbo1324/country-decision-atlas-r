import { useTranslations } from "next-intl";
import { EmptyState as EmptyStateShell } from "@country-decision-atlas/ui";

type EmptyStateProps = {
  message?: string;
};

export function EmptyState({ message }: EmptyStateProps) {
  const t = useTranslations("emptyState");
  return <EmptyStateShell message={message ?? t("default")} />;
}
