import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { HeatmapChart } from "@/components/charts/HeatmapChart";
import { SCENARIO_MATRIX } from "@/data/fixtures";

interface MatrixSlideProps {
  active: boolean;
}

export function MatrixSlide({ active }: MatrixSlideProps) {
  return (
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="sage">Scenario Matrix</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Сценарии против
          <br />
          <em className="text-sage3 not-italic">юрисдикций</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Тепловая матрица: скор каждой страны под конкретный жизненный сценарий
          — переезд, бизнес, ограниченный бюджет, безопасность. Веса сценариев
          неизменны, персонализация — отдельным слоем поверх.
        </p>
        <div className="flex gap-10">
          <MetricStat
            value={`${SCENARIO_MATRIX.countries.length}×${SCENARIO_MATRIX.scenarios.length}`}
            label="Матрица"
          />
          <MetricStat
            value="92"
            label="Лучший скор"
          />
        </div>
      </div>

      <ChartFrame
        title="Heatmap · сценарий × страна"
        className="h-80"
      >
        <HeatmapChart
          rows={SCENARIO_MATRIX.scenarios}
          columns={SCENARIO_MATRIX.countries}
          values={SCENARIO_MATRIX.values}
          active={active}
        />
      </ChartFrame>
    </SlideSection>
  );
}
