import { useTranslations } from "next-intl";
import { DisclaimerNotice } from "./DisclaimerNotice";

export function AppFooter() {
  const t = useTranslations("footer");

  return (
    <footer className="border-warm mt-auto border-t">
      <div className="mx-auto flex max-w-[1400px] flex-col gap-4 px-6 py-8 sm:flex-row sm:items-center sm:justify-between">
        <DisclaimerNotice text={t("disclaimer")} />
        <span className="font-mono text-c4 shrink-0 text-[9px] tracking-[0.2em] uppercase">
          {t("refLabel")} · CDA-WEB
        </span>
      </div>
    </footer>
  );
}
