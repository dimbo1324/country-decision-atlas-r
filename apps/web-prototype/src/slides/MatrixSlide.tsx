import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { DivergingMeter } from "@/components/charts/DivergingMeter";
import { RankFlow } from "@/components/charts/RankFlow";
import { RANK_QUARTERS, SCENARIOS, type Dataset } from "@/data/generator";

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
    <SlideSection className="grid grid-cols-1 items-center gap-10 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="sage">Матрица сценариев</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Сценарии против
          <br />
          <em className="text-sage3 not-italic">юрисдикций</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Прямое сравнение двух юрисдикций по одинаковым жизненным сценариям и
          поток рангов по кварталам: видно не только «кто лучше сейчас», но и
          кто кого обгоняет со временем. Веса сценариев неизменны.
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

      <div className="flex flex-col gap-5">
        <ChartFrame
          title={`${dataset.scenarioLeftName} ↔ ${dataset.scenarioRightName}`}
          className="h-64 flex-none"
        >
          <DivergingMeter
            categories={SCENARIOS}
            leftLabel={dataset.scenarioLeftName}
            rightLabel={dataset.scenarioRightName}
            leftValues={dataset.scenarioLeftValues}
            rightValues={dataset.scenarioRightValues}
            leftColorVar="--color-gold"
            rightColorVar="--color-sage3"
            active={active}
          />
        </ChartFrame>
        <ChartFrame
          title="Поток рангов · 6 кварталов"
          className="h-56 flex-none"
        >
          <RankFlow
            key={dataset.version}
            series={dataset.rankFlow}
            columns={RANK_QUARTERS}
            active={active}
          />
        </ChartFrame>
      </div>
    </SlideSection>
  );
}
