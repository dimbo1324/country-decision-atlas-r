import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { DivergingBarChart } from "@/components/charts/DivergingBarChart";
import { SCENARIOS, type Dataset } from "@/data/generator";

interface MatrixSlideProps {
  active: boolean;
  dataset: Dataset;
}

export function MatrixSlide({ active, dataset }: MatrixSlideProps) {
  const bestScore = Math.max(
    ...dataset.scenarioLeftValues,
    ...dataset.scenarioRightValues,
  );

  return (
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="sage">Матрица сценариев</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Сценарии против
          <br />
          <em className="text-sage3 not-italic">юрисдикций</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Прямое сравнение двух юрисдикций по одинаковым жизненным сценариям —
          релокация, резидентство, бизнес, ограниченный бюджет. Веса сценариев
          неизменны, персонализация — отдельным слоем поверх.
        </p>
        <div className="flex gap-10">
          <MetricStat
            value={`${SCENARIOS.length}×2`}
            label="Сравнение"
          />
          <MetricStat
            value={String(bestScore)}
            label="Лучший скор"
          />
        </div>
      </div>

      <ChartFrame
        title={`${dataset.scenarioLeftName} ↔ ${dataset.scenarioRightName}`}
        className="h-80"
      >
        <div className="flex h-full flex-col gap-2">
          <div className="flex items-center justify-between px-1 font-mono text-[9px] tracking-[0.2em] uppercase">
            <span className="text-gold3">{dataset.scenarioLeftName}</span>
            <span className="text-sage3">{dataset.scenarioRightName}</span>
          </div>
          <div className="flex-1">
            <DivergingBarChart
              key={dataset.version}
              categories={SCENARIOS}
              leftValues={dataset.scenarioLeftValues}
              rightValues={dataset.scenarioRightValues}
              leftColorVar="--color-gold"
              rightColorVar="--color-sage3"
              active={active}
            />
          </div>
        </div>
      </ChartFrame>
    </SlideSection>
  );
}
