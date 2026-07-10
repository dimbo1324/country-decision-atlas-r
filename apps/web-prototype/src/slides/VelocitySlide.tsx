import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { SparklineChart } from "@/components/charts/SparklineChart";
import type { Dataset } from "@/data/generator";

interface VelocitySlideProps {
  active: boolean;
  dataset: Dataset;
}

export function VelocitySlide({ active, dataset }: VelocitySlideProps) {
  const timeline = dataset.legalVelocityTimeline;
  const avgSignal = (
    timeline.reduce((sum, value) => sum + value, 0) / timeline.length
  ).toFixed(1);
  const delta = (timeline[timeline.length - 1] - timeline[0]).toFixed(1);

  return (
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="blue">Индекс скорости права (LVI)</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Скорость
          <br />
          <em className="text-blue3 not-italic">перемен закона</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Уникальная метрика платформы: как часто юрисдикция меняет правила
          игры. Считается из потока правовых сигналов — колоколообразная норма,
          где и застой, и турбулентность одинаково рискованны.
        </p>
        <div className="flex gap-10">
          <MetricStat
            value={avgSignal}
            label="Сигналов / квартал"
          />
          <MetricStat
            value={`${Number(delta) >= 0 ? "+" : ""}${delta}`}
            label="За 24 мес"
          />
        </div>
      </div>

      <ChartFrame title="Скорость права · 24 месяца">
        <SparklineChart
          key={dataset.version}
          values={timeline}
          active={active}
          colorVar="--color-blue3"
          yAxisLabel="Сигналов / квартал"
          xAxisLabel="24 месяца"
        />
      </ChartFrame>
    </SlideSection>
  );
}
