"use client";

import { useQuery } from "@tanstack/react-query";
import { Command } from "cmdk";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { searchQuery } from "../../entities/search/api";
import { useAuth } from "../auth/AuthProvider";
import { useRouter } from "../../i18n/navigation";
import { useAppLocale } from "../lib/useAppLocale";
import { routes } from "../lib/routes";
import type { SearchResultItem } from "../api/search";

const SEARCH_DEBOUNCE_MS = 280;
const PALETTE_RESULT_LIMIT = 8;

const ENTITY_TYPE_LABELS: Record<SearchResultItem["entity_type"], string> = {
  country: "Страна",
  route: "Маршрут",
  route_checklist_item: "Пункт чек-листа",
  legal_signal: "Правовой сигнал",
  source: "Источник",
  evidence_item: "Доказательство",
  country_pair_compatibility: "Совместимость стран",
  methodology: "Методология",
  glossary_term: "Термин глоссария",
};

/** ⌘K shell: static navigation sections when the input is empty, live
 * debounced `/search` results once something is typed (Stage 5). */
export function CommandPalette() {
  const t = useTranslations("search");
  const tNav = useTranslations("nav");
  const tAuth = useTranslations("auth");
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const router = useRouter();
  const { user } = useAuth();
  const locale = useAppLocale();

  useEffect(() => {
    const id = window.setTimeout(
      () => setDebouncedQuery(query.trim()),
      SEARCH_DEBOUNCE_MS,
    );
    return () => window.clearTimeout(id);
  }, [query]);

  const hasQuery = debouncedQuery.length > 0;
  const { data: searchResult, isFetching } = useQuery({
    ...searchQuery({
      q: debouncedQuery,
      locale,
      limit: PALETTE_RESULT_LIMIT,
    }),
    enabled: open && hasQuery,
  });
  const results = searchResult?.items ?? [];

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((prev) => !prev);
      }
      if (event.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  function go(href: string) {
    setOpen(false);
    setQuery("");
    router.push(href);
  }

  const sections = [
    {
      label: t("sectionSections"),
      items: [
        { label: tNav("countries"), href: routes.countries },
        { label: tNav("decision"), href: routes.decision },
        { label: tNav("migrationBoard"), href: routes.migrationBoard },
        { label: tNav("legalSignals"), href: routes.legalSignals },
        { label: tNav("sources"), href: routes.sources },
      ],
    },
    {
      label: t("sectionActions"),
      items: user
        ? [{ label: tAuth("account"), href: routes.account }]
        : [{ label: tAuth("signIn"), href: routes.login }],
    },
  ];

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label={t("paletteTrigger")}
        className="border-warm text-c3 hover:border-warm-hi hover:text-c1 font-mono inline-flex items-center gap-2 border px-3 py-2 text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
        data-testid="command-palette-trigger"
      >
        <Search
          width={13}
          height={13}
          strokeWidth={1.5}
        />
        <span className="hidden 2xl:inline">{t("paletteTrigger")}</span>
        <kbd className="text-c4 border-warm hidden border px-1 py-0.5 text-[9px] 2xl:inline">
          ⌘K
        </kbd>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-[95] flex items-start justify-center bg-black/60 pt-[15vh] backdrop-blur-sm"
          onClick={() => setOpen(false)}
          data-testid="command-palette-overlay"
        >
          <Command
            className="bg-bg4 border-warm-hi w-full max-w-lg border shadow-[0_24px_64px_rgb(0_0_0/0.5)]"
            onClick={(event) => event.stopPropagation()}
            label={t("paletteTitle")}
            shouldFilter={false}
          >
            <Command.Input
              autoFocus
              value={query}
              onValueChange={setQuery}
              placeholder={t("placeholder")}
              data-testid="command-palette-input"
              className="border-warm text-c1 placeholder:text-c4 font-body w-full border-b bg-transparent px-4 py-3.5 text-sm outline-none"
            />
            <Command.List className="scrollbar-thin max-h-80 overflow-y-auto p-2">
              <Command.Empty className="text-c4 font-mono px-3 py-6 text-center text-[10px] tracking-[0.15em] uppercase">
                {hasQuery && isFetching ? t("searching") : t("paletteEmpty")}
              </Command.Empty>
              {hasQuery ? (
                <Command.Group
                  heading={t("sectionResults")}
                  className="[&_[cmdk-group-heading]]:text-c4 [&_[cmdk-group-heading]]:font-mono [&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-2 [&_[cmdk-group-heading]]:text-[9px] [&_[cmdk-group-heading]]:tracking-[0.2em] [&_[cmdk-group-heading]]:uppercase"
                >
                  {results.map((item) => (
                    <Command.Item
                      key={item.id}
                      value={item.id}
                      onSelect={() => go(item.path)}
                      data-testid="command-palette-result"
                      className="text-c2 data-[selected=true]:bg-bg3 data-[selected=true]:text-c1 font-body flex cursor-pointer items-center justify-between gap-3 px-3 py-2.5 text-sm outline-none"
                    >
                      <span className="truncate">{item.title}</span>
                      <span className="font-mono text-c4 shrink-0 text-[8px] tracking-[0.15em] uppercase">
                        {ENTITY_TYPE_LABELS[item.entity_type] ??
                          item.entity_type}
                      </span>
                    </Command.Item>
                  ))}
                  <Command.Item
                    value={`show-all:${debouncedQuery}`}
                    onSelect={() =>
                      go(`/search?q=${encodeURIComponent(debouncedQuery)}`)
                    }
                    data-testid="command-palette-show-all"
                    className="text-gold3 data-[selected=true]:bg-bg3 data-[selected=true]:text-gold font-mono cursor-pointer px-3 py-2.5 text-[10px] tracking-[0.15em] uppercase outline-none"
                  >
                    {t("showAllResults")}
                  </Command.Item>
                </Command.Group>
              ) : (
                sections.map((section) => (
                  <Command.Group
                    key={section.label}
                    heading={section.label}
                    className="[&_[cmdk-group-heading]]:text-c4 [&_[cmdk-group-heading]]:font-mono [&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-2 [&_[cmdk-group-heading]]:text-[9px] [&_[cmdk-group-heading]]:tracking-[0.2em] [&_[cmdk-group-heading]]:uppercase"
                  >
                    {section.items.map((item) => (
                      <Command.Item
                        key={item.href}
                        value={item.href}
                        onSelect={() => go(item.href)}
                        className="text-c2 data-[selected=true]:bg-bg3 data-[selected=true]:text-c1 font-body cursor-pointer px-3 py-2.5 text-sm outline-none"
                      >
                        {item.label}
                      </Command.Item>
                    ))}
                  </Command.Group>
                ))
              )}
            </Command.List>
          </Command>
        </div>
      )}
    </>
  );
}
