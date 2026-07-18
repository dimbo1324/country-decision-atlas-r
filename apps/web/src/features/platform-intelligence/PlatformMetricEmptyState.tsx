import { useTranslations } from "next-intl";
import { EmptyState } from "../../shared/ui/EmptyState";

export function PlatformMetricEmptyState() {
  const t = useTranslations("platformIntelligence");
  return (
    <div data-testid="platform-intelligence-empty">
      <EmptyState message={t("emptyMessage")} />
    </div>
  );
}
