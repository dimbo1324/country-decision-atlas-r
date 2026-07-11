import { GitCompareArrows, ShieldAlert, Zap } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { MetricCard } from "@/components/ui/MetricCard";
import { GaugeArc } from "@/components/charts/GaugeArc";
import type { Dataset } from "@/data/generator";

const METRIC_ICONS: Record<string, LucideIcon> = {
  lvi: Zap,
  ssrs: ShieldAlert,
  cs: GitCompareArrows,
};

interface MetricsSlideProps {
  active: boolean;
  dataset: Dataset;
}

export function MetricsSlide({ active, dataset }: MetricsSlideProps) {
  return (
    <SlideSection className="gap-10">
      <div className="flex flex-col items-center gap-4 text-center">
        <Kicker className="justify-center">Собственный интеллект</Kicker>
        <h2 className="font-display text-4xl font-bold sm:text-5xl">
          Метрики, которых{" "}
          <em className="text-gold3 not-italic">нет ни у кого</em>
        </h2>
        <p className="text-c3 max-w-xl text-sm leading-relaxed">
          Уникальные показатели, вычисляемые из собственных данных платформы —
          без внешних API и без вмешательства в формулу CII.
        </p>
      </div>

      <div className="mx-auto grid w-full max-w-5xl grid-cols-1 items-stretch gap-5 lg:grid-cols-[1fr_1fr_1fr_auto]">
        {dataset.metricHighlights.map((metric) => (
          <MetricCard
            key={`${dataset.version}-${metric.id}`}
            icon={METRIC_ICONS[metric.id] ?? Zap}
            name={metric.name}
            tag={metric.tag}
            description={metric.description}
            value={metric.value}
            unit={metric.unit}
            accent={metric.accent}
          />
        ))}
        <div className="border-warm bg-bg3 flex flex-col items-center justify-center gap-2 border p-5">
          <GaugeArc
            key={dataset.version}
            value={dataset.riskGauge.value}
            valueLabel={dataset.riskGauge.label}
            label="Суммарный риск-фон"
            active={active}
            width={200}
          />
          <span className="font-mono text-c4 max-w-[200px] text-center text-[8px] leading-relaxed tracking-[0.15em] uppercase">
            Сводка трёх метрик по всем юрисдикциям
          </span>
        </div>
      </div>
    </SlideSection>
  );
}
