import { useTranslations } from "next-intl";
import { EmptyState } from "../../shared/ui/EmptyState";

export function DataJournalEmptyState() {
  const t = useTranslations("dataJournal");
  return (
    <div data-testid="data-journal-empty">
      <EmptyState message={t("empty")} />
    </div>
  );
}
