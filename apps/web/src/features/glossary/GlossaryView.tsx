"use client";

import { useQuery } from "@tanstack/react-query";
import { Kicker } from "@country-decision-atlas/ui";
import { parseAsString, useQueryState } from "nuqs";
import { Suspense, useMemo } from "react";
import { glossaryTermsQuery } from "../../entities/glossary/api";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { toApiLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { GlossaryFilters } from "./GlossaryFilters";
import { GlossaryTermEntry } from "./GlossaryTermEntry";

function GlossaryViewInner() {
  const locale = useAppLocale();
  const [q, setQ] = useQueryState("q", parseAsString.withDefault(""));
  const [category, setCategory] = useQueryState(
    "category",
    parseAsString.withDefault(""),
  );

  const { data, isPending, isError } = useQuery(
    glossaryTermsQuery(
      toApiLocale(locale),
      category || undefined,
      q || undefined,
    ),
  );

  const groups = useMemo(() => {
    const items = [...(data?.items ?? [])].sort((a, b) =>
      a.term.localeCompare(b.term),
    );
    const byLetter = new Map<string, typeof items>();
    for (const term of items) {
      const letter = term.term.charAt(0).toUpperCase();
      const bucket = byLetter.get(letter) ?? [];
      bucket.push(term);
      byLetter.set(letter, bucket);
    }
    return [...byLetter.entries()].sort(([a], [b]) => a.localeCompare(b));
  }, [data]);

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="glossary-page"
    >
      <GlossaryFilters
        q={q}
        category={category}
        onQueryChange={(value) => void setQ(value || null)}
        onCategoryChange={(value) => void setCategory(value || null)}
      />

      {data && <Kicker>Терминов: {data.items.length}</Kicker>}

      {isPending && <LoadingState message="Загрузка глоссария…" />}
      {!isPending && isError && (
        <ErrorState error="Не удалось загрузить глоссарий." />
      )}
      {!isPending && !isError && groups.length === 0 && (
        <EmptyState message="По выбранным фильтрам термины не найдены." />
      )}
      {!isPending && !isError && groups.length > 0 && (
        <div
          className="flex flex-col gap-8"
          data-testid="glossary-term-list"
        >
          {groups.map(([letter, terms]) => (
            <section
              key={letter}
              className="flex flex-col gap-4"
            >
              <h2 className="font-display text-c1 text-2xl font-semibold">
                {letter}
              </h2>
              <div className="flex flex-col gap-3">
                {terms.map((term) => (
                  <GlossaryTermEntry
                    key={term.slug}
                    term={term}
                  />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}

export function GlossaryView() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка глоссария…" />}>
      <GlossaryViewInner />
    </Suspense>
  );
}
