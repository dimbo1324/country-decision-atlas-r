"use client";

import {
  cn,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@country-decision-atlas/ui";
import { ChevronDown } from "lucide-react";
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
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        {/* Locale codes are always 2 letters, so a fixed width here never
         * shifts when the interface locale changes -- unlike the previous
         * three-button layout, this trigger's own size is locale-invariant
         * by construction. */}
        <button
          type="button"
          className={cn(
            "border-warm text-c3 hover:border-warm-hi hover:text-c1 font-mono flex w-[4.5rem] shrink-0 items-center justify-between border px-2.5 py-1.5 text-[10px] tracking-[0.1em] uppercase outline-none transition-colors duration-200",
            className,
          )}
          aria-label={t("switchTo", { locale: currentLocale.toUpperCase() })}
          data-testid="locale-switcher-trigger"
        >
          {currentLocale.toUpperCase()}
          <ChevronDown
            width={12}
            height={12}
            strokeWidth={1.5}
          />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="min-w-[4.5rem]"
      >
        {SUPPORTED_LOCALES.map((locale) => (
          <DropdownMenuItem
            key={locale}
            onSelect={() => switchLocale(locale)}
            data-active={currentLocale === locale}
            className="font-mono data-[active=true]:text-gold3 justify-center text-[10px] tracking-[0.1em] uppercase"
            aria-label={t("switchTo", { locale: locale.toUpperCase() })}
            data-testid={`locale-switch-${locale}`}
          >
            {locale.toUpperCase()}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
