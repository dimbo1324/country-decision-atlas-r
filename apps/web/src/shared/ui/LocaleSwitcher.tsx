"use client";

import { cn } from "@country-decision-atlas/ui";
import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { usePathname, useRouter } from "../../i18n/navigation";
import { SUPPORTED_LOCALES } from "../lib/locale";

export function LocaleSwitcher({ className }: { className?: string }) {
  const t = useTranslations("locale");
  const currentLocale = useLocale();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();

  function switchLocale(locale: string) {
    const query = searchParams.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { locale });
  }

  return (
    <div className={cn("border-warm flex items-center border", className)}>
      {SUPPORTED_LOCALES.map((locale) => (
        <button
          type="button"
          key={locale}
          onClick={() => switchLocale(locale)}
          data-active={currentLocale === locale}
          className="font-mono text-c3 hover:text-c1 data-[active=true]:bg-bg3 data-[active=true]:text-gold3 px-2 py-1.5 text-[10px] tracking-[0.1em] transition-colors duration-200"
          aria-label={t("switchTo", { locale: locale.toUpperCase() })}
          data-testid={`locale-switch-${locale}`}
        >
          {locale.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
