import { useEffect, useRef, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { GitCompareArrows, X } from "lucide-react";
import { cn } from "@/lib/cn";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Counter } from "@/components/ui/Counter";
import { Kicker } from "@/components/ui/Kicker";
import { Toggle } from "@/components/ui/Toggle";
import { Accordion } from "@/components/ui/Accordion";
import { MetricCard } from "@/components/ui/MetricCard";
import { TimelineList } from "@/components/ui/TimelineList";
import { SignalTicker } from "@/components/ui/SignalTicker";
import { DriftBoard } from "@/components/ui/DriftBoard";
import { PassportCard } from "@/components/ui/PassportCard";
import { DataTable } from "@/components/ui/DataTable";
import { RadarChart } from "@/components/charts/RadarChart";
import { SparklineChart } from "@/components/charts/SparklineChart";
import { DivergingMeter } from "@/components/charts/DivergingMeter";
import { Heatmap } from "@/components/charts/Heatmap";
import { RankFlow } from "@/components/charts/RankFlow";
import { BarColumns } from "@/components/charts/BarColumns";
import { ProgressRing } from "@/components/charts/ProgressRing";
import { GaugeArc } from "@/components/charts/GaugeArc";
import { DonutChart } from "@/components/charts/DonutChart";
import { useState } from "react";
import {
  CII_AXES,
  RANK_QUARTERS,
  SCENARIOS,
  type Dataset,
} from "@/data/generator";

interface LibraryOverlayProps {
  open: boolean;
  onClose: () => void;
  dataset: Dataset;
}

function Specimen({
  name,
  note,
  children,
  wide,
}: {
  name: string;
  note: string;
  children: ReactNode;
  wide?: boolean;
}) {
  return (
    <figure
      className={cn(
        "border-warm bg-bg2 flex min-w-0 flex-col border",
        wide && "sm:col-span-2",
      )}
    >
      <figcaption className="border-warm flex items-baseline justify-between gap-4 border-b px-4 py-2.5">
        <span className="font-mono text-gold3 text-[10px] tracking-[0.2em]">
          {name}
        </span>
        <span className="font-mono text-c4 truncate text-[8px] tracking-[0.12em] uppercase">
          {note}
        </span>
      </figcaption>
      <div className="min-w-0 flex-1 p-5">{children}</div>
    </figure>
  );
}

function SectionHeading({ title, index }: { title: string; index: number }) {
  return (
    <div className="mt-14 mb-5 flex items-baseline gap-4 first:mt-0">
      <span className="font-mono text-c4 text-[10px] tracking-[0.3em]">
        {String(index).padStart(2, "0")}
      </span>
      <h3 className="font-display text-c1 text-2xl font-semibold">{title}</h3>
      <span className="border-warm mb-1 flex-1 self-end border-b" />
    </div>
  );
}

function InteractiveToggleSpecimen() {
  const [first, setFirst] = useState(true);
  const [second, setSecond] = useState(false);
  return (
    <div className="flex flex-col gap-3">
      <Toggle
        checked={first}
        onChange={setFirst}
        label="Учитывать налоговое соглашение"
        hint="Пересчитывает скор вживую"
        accent="sage"
      />
      <Toggle
        checked={second}
        onChange={setSecond}
        label="Режим цифрового кочевника"
        hint="Смещает веса сценария"
        accent="blue"
      />
    </div>
  );
}

/** Full-screen, scrollable component catalog: every infographic element of
 * the prototype rendered live under its component name, so pieces can be
 * lifted straight into the main frontend as from a template library. */
export function LibraryOverlay({
  open,
  onClose,
  dataset,
}: LibraryOverlayProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  if (!open) return null;

  const [countryA, countryB] = dataset.ciiSeries;

  return createPortal(
    <div className="bg-bg/80 fixed inset-0 z-[90] flex flex-col backdrop-blur-md">
      <header className="border-warm bg-bg3/90 flex shrink-0 items-center justify-between border-b px-8 py-4">
        <div className="flex items-baseline gap-4">
          <span className="font-display text-c1 text-lg font-bold">
            Библиотека компонентов
          </span>
          <span className="font-mono text-c4 text-[9px] tracking-[0.25em] uppercase max-sm:hidden">
            Живые образцы · извлекайте в основной фронтенд
          </span>
        </div>
        <button
          onClick={onClose}
          aria-label="Закрыть библиотеку"
          className="border-warm text-c2 hover:border-warm-hi hover:text-c1 flex h-9 w-9 shrink-0 items-center justify-center border transition-transform duration-300 hover:rotate-90"
        >
          <X
            width={16}
            height={16}
            strokeWidth={1.5}
          />
        </button>
      </header>

      <div
        ref={scrollRef}
        className="scrollbar-thin min-h-0 flex-1 overflow-y-auto px-8 py-8 sm:px-14"
      >
        <div className="mx-auto max-w-5xl pb-16">
          <SectionHeading
            title="Диаграммы"
            index={1}
          />
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Specimen
              name="RadarChart"
              note="canvas · дышащие данные"
            >
              <div className="h-72">
                <RadarChart
                  axes={CII_AXES}
                  active={open}
                  series={[
                    {
                      label: countryA.name,
                      values: countryA.values,
                      colorVar: "--color-gold",
                    },
                    {
                      label: countryB.name,
                      values: countryB.values,
                      colorVar: "--color-blue3",
                    },
                  ]}
                />
              </div>
            </Specimen>
            <Specimen
              name="SparklineChart"
              note="canvas · оси на ховере"
            >
              <div className="h-72">
                <SparklineChart
                  values={dataset.legalVelocityTimeline}
                  active={open}
                  colorVar="--color-blue3"
                  yAxisLabel="Сигналов / квартал"
                  xAxisLabel="24 месяца"
                />
              </div>
            </Specimen>
            <Specimen
              name="Heatmap"
              note="canvas · ховер-ячейки"
              wide
            >
              <div className="h-64">
                <Heatmap
                  data={dataset.heatmap}
                  active={open}
                />
              </div>
            </Specimen>
            <Specimen
              name="RankFlow"
              note="canvas · bump-chart рангов"
              wide
            >
              <div className="h-60">
                <RankFlow
                  series={dataset.rankFlow}
                  columns={RANK_QUARTERS}
                  active={open}
                />
              </div>
            </Specimen>
            <Specimen
              name="DivergingMeter"
              note="css · двустороннее сравнение"
            >
              <div className="h-56">
                <DivergingMeter
                  categories={SCENARIOS}
                  leftLabel={dataset.scenarioLeftName}
                  rightLabel={dataset.scenarioRightName}
                  leftValues={dataset.scenarioLeftValues}
                  rightValues={dataset.scenarioRightValues}
                  leftColorVar="--color-gold"
                  rightColorVar="--color-sage3"
                  active={open}
                />
              </div>
            </Specimen>
            <Specimen
              name="BarColumns"
              note="css · значения на ховере"
            >
              <div className="h-56">
                <BarColumns
                  items={dataset.quarterSignals}
                  active={open}
                />
              </div>
            </Specimen>
          </div>

          <SectionHeading
            title="Индикаторы"
            index={2}
          />
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <Specimen
              name="ProgressRing"
              note="svg · кольцо прогресса"
            >
              <div className="flex justify-center">
                <ProgressRing
                  value={dataset.trustScore}
                  label="Скор доверия"
                  active={open}
                  colorVar="--color-blue3"
                />
              </div>
            </Specimen>
            <Specimen
              name="GaugeArc"
              note="svg · гравированный циферблат"
            >
              <div className="flex justify-center">
                <GaugeArc
                  value={dataset.riskGauge.value}
                  valueLabel={dataset.riskGauge.label}
                  label="Риск-фон"
                  active={open}
                />
              </div>
            </Specimen>
            <Specimen
              name="DonutChart"
              note="svg · ховер-сегменты"
            >
              <DonutChart
                segments={dataset.donutSegments}
                centerValue={`${dataset.donutSegments.length}`}
                centerLabel="Типа источников"
                active={open}
                size={130}
              />
            </Specimen>
            <Specimen
              name="Counter"
              note="raf · ease-out cubic"
            >
              <div className="flex items-baseline gap-2">
                <span className="font-display text-gold3 text-5xl font-bold">
                  <Counter
                    value={dataset.trustScore}
                    suffix="%"
                    active={open}
                  />
                </span>
                <span className="font-mono text-c3 text-[9px] tracking-[0.15em] uppercase">
                  Долетает, не прыгает
                </span>
              </div>
            </Specimen>
            <Specimen
              name="Kicker"
              note="метка секции с точкой"
            >
              <div className="flex flex-col gap-3">
                <Kicker>Золотой акцент</Kicker>
                <Kicker accent="terra">Терракота · риски</Kicker>
                <Kicker accent="sage">Шалфей · рост</Kicker>
              </div>
            </Specimen>
            <Specimen
              name="Button"
              note="чернильная заливка снизу"
            >
              <div className="flex flex-col items-start gap-4">
                <Button variant="primary">Запустить анализ</Button>
                <Button variant="ghost">Читать методологию →</Button>
              </div>
            </Specimen>
          </div>

          <SectionHeading
            title="Блоки данных"
            index={3}
          />
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Specimen
              name="MetricCard"
              note="фирменная карточка метрики"
            >
              <MetricCard
                icon={GitCompareArrows}
                name={dataset.metricHighlights[2].name}
                tag={dataset.metricHighlights[2].tag}
                description={dataset.metricHighlights[2].description}
                value={dataset.metricHighlights[2].value}
                unit={dataset.metricHighlights[2].unit}
                accent="terra"
              />
            </Specimen>
            <Specimen
              name="DriftBoard"
              note="строки-спарклайны · клик = досье"
            >
              <DriftBoard
                rows={dataset.driftBoard.slice(0, 4)}
                active={open}
              />
            </Specimen>
            <Specimen
              name="PassportCard"
              note="документ с живым пересчётом"
              wide
            >
              <PassportCard
                passport={dataset.passport}
                active={open}
              />
            </Specimen>
            <Specimen
              name="TimelineList"
              note="лента изменений"
              wide
            >
              <TimelineList events={dataset.signalEvents.slice(0, 4)} />
            </Specimen>
            <Specimen
              name="SignalTicker"
              note="бегущая строка · пауза на ховере"
              wide
            >
              <SignalTicker items={dataset.tickerItems} />
            </Specimen>
            <Specimen
              name="DataTable"
              note="только горизонтальные границы"
              wide
            >
              <DataTable
                columns={[
                  { header: "Юрисдикция" },
                  { header: "CII", align: "right", numeric: true },
                  { header: "Достоверность", align: "right", numeric: true },
                  { header: "Дрейф", align: "right", numeric: true },
                ]}
                rows={dataset.catalog.map((country) => [
                  country.name,
                  String(country.ciiScore),
                  country.confidence.toFixed(2),
                  `${country.driftValue > 0 ? "+" : ""}${country.driftValue}`,
                ])}
              />
            </Specimen>
          </div>

          <SectionHeading
            title="Управление"
            index={4}
          />
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <Specimen
              name="Toggle"
              note="пружинный тумблер"
            >
              <InteractiveToggleSpecimen />
            </Specimen>
            <Specimen
              name="Accordion"
              note="grid-rows · без max-height"
            >
              <Accordion
                items={[
                  {
                    title: "Как считается скор",
                    meta: "Методология",
                    content:
                      "Базовый скор плюс явные бонусы — каждое слагаемое видно отдельно.",
                  },
                  {
                    title: "Откуда данные",
                    meta: "Источники",
                    content:
                      "Каждая ячейка подкреплена источником с датой верификации.",
                  },
                ]}
              />
            </Specimen>
            <Specimen
              name="Card"
              note="лазерная обводка на ховере"
              wide
            >
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Card
                  accent="gold"
                  className="min-h-[96px]"
                >
                  <span className="text-c2 text-sm">
                    Наведите курсор — по периметру пробежит луч.
                  </span>
                </Card>
                <Card
                  accent="plum"
                  className="min-h-[96px]"
                >
                  <span className="text-c2 text-sm">
                    У каждого блока ровно один акцентный цвет.
                  </span>
                </Card>
              </div>
            </Specimen>
          </div>

          <p className="font-quote text-c4 mt-14 text-center text-xs italic">
            Все данные на этой странице — вымышленные и носят демонстрационный
            характер.
          </p>
        </div>
      </div>
    </div>,
    document.body,
  );
}
