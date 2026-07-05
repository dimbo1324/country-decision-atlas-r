import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { SparklineChart } from "@/components/charts/SparklineChart";
import { COUNTRY_DRIFT_TIMELINE } from "@/data/fixtures";

interface DriftSlideProps {
  active: boolean;
}

export function DriftSlide({ active }: DriftSlideProps) {
  return (
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="terra">Country Drift Index</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Куда движется
          <br />
          <em className="text-terra3 not-italic">каждая страна</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Главный moat платформы: вектор направления юрисдикции из правовых
          сигналов за окно 180 дней. Положительный дрейф — страна открывается,
          отрицательный — закрывается. При выборке менее трёх событий честно
          помечаем «недостаточно данных».
        </p>
        <div className="flex gap-10">
          <MetricStat
            value="+7.2"
            label="Net drift"
          />
          <MetricStat
            value="↗"
            label="Momentum"
          />
        </div>
      </div>

      <ChartFrame title="Drift Timeline · 24 мес">
        <SparklineChart
          values={COUNTRY_DRIFT_TIMELINE}
          active={active}
          colorVar="--color-terra3"
          zeroLine
        />
      </ChartFrame>
    </SlideSection>
  );
}
