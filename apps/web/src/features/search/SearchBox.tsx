"use client";

import { cn } from "@country-decision-atlas/ui";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { useRouter } from "../../i18n/navigation";

export function SearchBox({ className }: { className?: string }) {
  const t = useTranslations("search");
  const router = useRouter();
  const [value, setValue] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = value.trim();
    if (!query) return;
    router.push(`/search?q=${encodeURIComponent(query)}`);
  }

  return (
    <form
      role="search"
      onSubmit={handleSubmit}
      data-testid="search-box-form"
      className={cn("border-warm flex items-center border", className)}
    >
      <input
        type="search"
        placeholder={t("placeholder")}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        aria-label={t("placeholder")}
        data-testid="search-box-input"
        className="text-c1 placeholder:text-c4 font-body w-40 bg-transparent px-3 py-2 text-sm outline-none xl:w-56"
      />
      <button
        type="submit"
        data-testid="search-box-submit"
        className="font-mono text-c3 hover:text-gold3 border-warm border-l px-3 py-2 text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
      >
        {t("submit")}
      </button>
    </form>
  );
}
