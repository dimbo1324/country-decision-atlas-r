import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { Card } from "@/components/ui/Card";
import { Drawer } from "@/components/ui/Drawer";
import { Counter } from "@/components/ui/Counter";
import type { CatalogCountry, Dataset } from "@/data/generator";

function driftIcon(value: number) {
  if (value > 1.5)
    return (
      <TrendingUp
        width={14}
        height={14}
        strokeWidth={1.5}
      />
    );
  if (value < -1.5)
    return (
      <TrendingDown
        width={14}
        height={14}
        strokeWidth={1.5}
      />
    );
  return (
    <Minus
      width={14}
      height={14}
      strokeWidth={1.5}
    />
  );
}

interface CommunitySlideProps {
  dataset: Dataset;
}

export function CommunitySlide({ dataset }: CommunitySlideProps) {
  const [selected, setSelected] = useState<CatalogCountry | null>(null);

  useEffect(() => {
    setSelected(null);
  }, [dataset.version]);

  return (
    <SlideSection className="gap-10">
      <div className="flex flex-col items-center gap-4 text-center">
        <Kicker
          accent="plum"
          className="justify-center"
        >
          Рейтинговый регистр
        </Kicker>
        <h2 className="font-display text-4xl font-bold sm:text-5xl">
          Каталог <em className="text-plum3 not-italic">юрисдикций</em>
        </h2>
        <p className="text-c3 max-w-xl text-sm">
          Нажмите на карточку страны, чтобы открыть детальное досье.
        </p>
      </div>

      <div className="mx-auto grid w-full max-w-5xl grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {dataset.catalog.map((country) => (
          <Card
            key={country.slug}
            accent="plum"
            onClick={() => setSelected(country)}
            className="flex flex-col gap-4"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-c4 text-[10px] tracking-[0.2em]">
                {country.flag}
              </span>
              <span
                className={
                  country.driftValue > 1.5
                    ? "text-sage3 flex items-center gap-1 text-xs"
                    : country.driftValue < -1.5
                      ? "text-terra3 flex items-center gap-1 text-xs"
                      : "text-c3 flex items-center gap-1 text-xs"
                }
              >
                {driftIcon(country.driftValue)}
                {country.driftValue > 0 ? "+" : ""}
                {country.driftValue}
              </span>
            </div>
            <h3 className="font-display text-xl font-semibold">
              {country.name}
            </h3>
            <div className="flex items-baseline gap-2">
              <span className="font-display text-gold3 text-2xl font-bold">
                <Counter
                  key={`${dataset.version}-${country.slug}`}
                  value={country.ciiScore}
                  active
                />
              </span>
              <span className="font-mono text-c3 text-[9px] tracking-[0.15em] uppercase">
                CII · дост. {Math.round(country.confidence * 100)}%
              </span>
            </div>
          </Card>
        ))}
      </div>

      <Drawer
        open={selected !== null}
        onClose={() => setSelected(null)}
        accent="plum"
        eyebrow={selected ? `REF № CA-2026-${selected.flag}` : ""}
        title={selected?.name ?? ""}
      >
        {selected && (
          <div className="flex flex-col gap-6">
            <div className="flex gap-8">
              <div>
                <div className="font-display text-gold3 text-3xl font-bold">
                  {selected.ciiScore}
                </div>
                <div className="font-mono text-c3 text-[9px] tracking-[0.2em] uppercase">
                  Балл CII
                </div>
              </div>
              <div>
                <div className="font-display text-c1 text-3xl font-bold">
                  {Math.round(selected.confidence * 100)}%
                </div>
                <div className="font-mono text-c3 text-[9px] tracking-[0.2em] uppercase">
                  Достоверность
                </div>
              </div>
            </div>

            <p className="text-c2 text-sm leading-relaxed">
              {selected.summary}
            </p>

            <div>
              <div className="font-mono text-c3 mb-2 text-[9px] tracking-[0.2em] uppercase">
                Дрейф страны
              </div>
              <div className="border-warm flex items-center gap-2 border p-3">
                {driftIcon(selected.driftValue)}
                <span className="text-c1 text-sm">{selected.driftLabel}</span>
                <span className="font-mono text-c3 ml-auto text-xs">
                  {selected.driftValue > 0 ? "+" : ""}
                  {selected.driftValue}
                </span>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              {selected.tags.map((tag) => (
                <span
                  key={tag}
                  className="border-warm text-c3 font-mono px-2 py-1 text-[9px] tracking-[0.15em] uppercase"
                >
                  {tag}
                </span>
              ))}
            </div>

            <p className="font-quote text-c4 text-xs italic">
              Это не юридическая консультация — данные носят справочный
              характер.
            </p>
          </div>
        )}
      </Drawer>
    </SlideSection>
  );
}
