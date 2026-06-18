"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { DEFAULT_LOCALE, SUPPORTED_LOCALES } from "../lib/locale";

export function LocaleSwitcher() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const router = useRouter();

  const currentLocale = searchParams.get("locale") ?? DEFAULT_LOCALE;

  function switchLocale(locale: string) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("locale", locale);
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="localeSwitcher">
      {SUPPORTED_LOCALES.map((locale) => (
        <button
          key={locale}
          onClick={() => switchLocale(locale)}
          data-active={currentLocale === locale}
          className="localeButton"
        >
          {locale.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
