import { Accordion, type AccordionItem } from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";

type CountryProfileSectionsProps = {
  profile: CountryReadModelResponse["profile"];
  skipExecutiveSummary?: boolean;
};

type ProfileTextKey = Exclude<
  keyof NonNullable<CountryReadModelResponse["profile"]>,
  "localization"
>;

const SECTIONS: {
  key: ProfileTextKey;
  label: string;
}[] = [
  { key: "executive_summary", label: "Обзор" },
  { key: "migration_overview", label: "Миграция / резидентство" },
  { key: "tax_overview", label: "Налоги" },
  { key: "cost_of_living_overview", label: "Стоимость жизни" },
  { key: "business_overview", label: "Бизнес" },
  { key: "safety_overview", label: "Безопасность" },
  { key: "legal_signals_summary", label: "Правовые сигналы" },
  { key: "risk_summary", label: "Риски" },
  { key: "source_summary", label: "Источники" },
];

export function CountryProfileSections({
  profile,
  skipExecutiveSummary = false,
}: CountryProfileSectionsProps) {
  if (!profile) return <EmptyState message="Данные профиля отсутствуют." />;

  const filled = SECTIONS.filter(
    (s) =>
      profile[s.key] &&
      !(skipExecutiveSummary && s.key === "executive_summary"),
  );
  if (filled.length === 0)
    return <EmptyState message="Разделы профиля отсутствуют." />;

  const items: AccordionItem[] = filled.map((s) => ({
    title: s.label,
    content: (
      <p className="text-c3 text-sm leading-relaxed">{profile[s.key]}</p>
    ),
  }));

  return (
    <div className="flex flex-col gap-4">
      <LocalizationBadge localization={profile.localization} />
      <Accordion items={items} />
    </div>
  );
}
