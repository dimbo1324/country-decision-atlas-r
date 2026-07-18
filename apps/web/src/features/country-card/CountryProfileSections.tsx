import { useTranslations } from "next-intl";
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
  labelKey: string;
}[] = [
  { key: "executive_summary", labelKey: "sectionExecutiveSummary" },
  { key: "migration_overview", labelKey: "sectionMigration" },
  { key: "tax_overview", labelKey: "sectionTax" },
  { key: "cost_of_living_overview", labelKey: "sectionCostOfLiving" },
  { key: "business_overview", labelKey: "sectionBusiness" },
  { key: "safety_overview", labelKey: "sectionSafety" },
  { key: "legal_signals_summary", labelKey: "sectionLegalSignals" },
  { key: "risk_summary", labelKey: "sectionRisks" },
  { key: "source_summary", labelKey: "sectionSources" },
];

export function CountryProfileSections({
  profile,
  skipExecutiveSummary = false,
}: CountryProfileSectionsProps) {
  const t = useTranslations("countryProfileSections");
  if (!profile) return <EmptyState message={t("emptyProfile")} />;

  const filled = SECTIONS.filter(
    (s) =>
      profile[s.key] &&
      !(skipExecutiveSummary && s.key === "executive_summary"),
  );
  if (filled.length === 0) return <EmptyState message={t("emptySections")} />;

  const items: AccordionItem[] = filled.map((s) => ({
    title: t(s.labelKey),
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
