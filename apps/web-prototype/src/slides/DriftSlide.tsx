import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { SparklineChart } from "@/components/charts/SparklineChart";
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
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="terra">Индекс дрейфа страны (CDI)</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Куда движется
          <br />
          <em className="text-terra3 not-italic">каждая страна</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Главное конкурентное преимущество платформы: вектор направления
          юрисдикции из правовых сигналов за окно 180 дней. Положительный дрейф
          — страна открывается, отрицательный — закрывается. При выборке менее
          трёх событий честно помечаем «недостаточно данных».
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
      </div>

      <ChartFrame title="Хронология дрейфа · 24 мес">
        <SparklineChart
          key={dataset.version}
          values={timeline}
          active={active}
          colorVar="--color-terra3"
          zeroLine
        />
      </ChartFrame>
    </SlideSection>
  );
}
