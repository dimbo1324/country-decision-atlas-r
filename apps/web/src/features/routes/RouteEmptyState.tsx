import { useTranslations } from "next-intl";
import { EmptyState } from "../../shared/ui/EmptyState";

export function RouteEmptyState({ message }: { message?: string }) {
  const t = useTranslations("routes");
  return (
    <div data-testid="routes-empty">
      <EmptyState message={message ?? t("empty")} />
    </div>
  );
}
