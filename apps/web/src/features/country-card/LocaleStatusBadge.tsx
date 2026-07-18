import { useTranslations } from "next-intl";
import { Badge } from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";

type LocaleStatusBadgeProps = {
  locale: CountryReadModelResponse["locale"];
};

const STATUS_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    source: "Source language",
    translated: "Translated",
    fallback: "Fallback version",
    missing: "No translation",
  },
  ru: {
    source: "Исходный язык",
    translated: "Переведено",
    fallback: "Резервная версия",
    missing: "Перевод отсутствует",
  },
  es: {
    source: "Idioma original",
    translated: "Traducido",
    fallback: "Versión alternativa",
    missing: "Sin traducción",
  },
};

export function LocaleStatusBadge({ locale }: LocaleStatusBadgeProps) {
  const t = useTranslations("localeStatus");
  const uiLocale = useAppLocale();
  const isFallback = locale.translation_status === "fallback";

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-c3 text-sm">{t("requestedLocale")}</span>
        <Badge variant="default">{locale.requested_locale}</Badge>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-c3 text-sm">{t("resolvedLocale")}</span>
        <Badge variant="default">{locale.resolved_locale}</Badge>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-c3 text-sm">{t("translationStatus")}</span>
        <Badge variant={isFallback ? "warning" : "default"}>
          {STATUS_LABELS[uiLocale][locale.translation_status] ??
            locale.translation_status}
        </Badge>
      </div>
      {isFallback && locale.requested_locale === "ru" && (
        <p className="text-terra3 font-quote text-sm italic">
          {t("fallbackNotice")}
        </p>
      )}
    </div>
  );
}
