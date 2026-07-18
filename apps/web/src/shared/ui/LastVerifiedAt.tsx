import { useTranslations } from "next-intl";
import type { SupportedLocale } from "../lib/locale";
import { useAppLocale } from "../lib/useAppLocale";

type LastVerifiedAtProps = {
  date: string | null | undefined;
};

const DATE_FORMAT_LOCALE: Record<SupportedLocale, string> = {
  en: "en-US",
  ru: "ru-RU",
  es: "es-ES",
};

export function LastVerifiedAt({ date }: LastVerifiedAtProps) {
  const t = useTranslations("lastVerifiedAt");
  const locale = useAppLocale();

  if (!date) {
    return (
      <span className="last-verified-at last-verified-unknown">
        {t("unknown")}
      </span>
    );
  }
  const formatted = new Date(date).toLocaleDateString(
    DATE_FORMAT_LOCALE[locale],
    {
      year: "numeric",
      month: "long",
      day: "numeric",
    },
  );
  return (
    <span className="last-verified-at">
      {t("verified", { date: formatted })}
    </span>
  );
}
