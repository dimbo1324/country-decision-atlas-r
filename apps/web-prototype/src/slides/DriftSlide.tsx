import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { SparklineChart } from "@/components/charts/SparklineChart";
import { DriftBoard } from "@/components/ui/DriftBoard";
import type { Dataset } from "@/data/generator";

interface DriftSlideProps {
  active: boolean;
  dataset: Dataset;
}

export function DriftSlide({ active, dataset }: DriftSlideProps) {
  const timeline = dataset.countryDriftTimeline;
  const netDrift = timeline[timeline.length - 1];
  const trendArrow = netDrift > 1.5 ? "↗" : netDrift < -1.5 ? "↘" : "→";

  return (
    <SlideSection className="grid grid-cols-1 items-center gap-10 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="terra">Индекс дрейфа страны (CDI)</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Куда движется
          <br />
          <em className="text-terra3 not-italic">каждая страна</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Вектор направления юрисдикции из правовых сигналов за окно 180 дней.
          Положительный дрейф — страна открывается, отрицательный — закрывается.
          Нажмите на строку борда, чтобы открыть досье.
        </p>
        <div className="flex gap-10">
          <MetricStat
            value={`${netDrift > 0 ? "+" : ""}${netDrift}`}
            label="Чистый дрейф"
          />
          <MetricStat
            value={trendArrow}
            label="Тенденция"
          />
        </div>
        <ChartFrame
          title="Хронология дрейфа · 24 мес"
          className="h-44 max-lg:hidden"
        >
          <SparklineChart
            key={dataset.version}
            values={timeline}
            active={active}
            colorVar="--color-terra3"
            zeroLine
            yAxisLabel="Индекс дрейфа"
            xAxisLabel="24 месяца"
          />
        </ChartFrame>
      </div>

      <div className="border-warm bg-bg3 flex flex-col border p-5">
        <span className="font-mono text-c3 mb-2 text-[10px] tracking-[0.2em] uppercase">
          Табло направлений · 16 недель
        </span>
        <DriftBoard
          key={dataset.version}
          rows={dataset.driftBoard}
          active={active}
        />
      </div>
    </SlideSection>
  );
}
