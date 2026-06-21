import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";

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
    (s) => profile[s.key] && !(skipExecutiveSummary && s.key === "executive_summary"),
  );
  if (filled.length === 0) return <EmptyState message="Разделы профиля отсутствуют." />;

  return (
    <div className="sectionStack">
      {filled.map((s) => (
        <div key={s.key} className="profileSection">
          <h3 className="sectionTitle">{s.label}</h3>
          <p>{profile[s.key]}</p>
        </div>
      ))}
    </div>
  );
}
