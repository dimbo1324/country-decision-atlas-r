import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { RadarChart } from "@/components/charts/RadarChart";
import { CII_AXES, type Dataset } from "@/data/generator";

interface CiiSlideProps {
  active: boolean;
  dataset: Dataset;
}

export function CiiSlide({ active, dataset }: CiiSlideProps) {
  const [countryA, countryB] = dataset.ciiSeries;
  const [catalogA] = dataset.catalog;

  return (
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="gold">Индекс странового интеллекта (CII)</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Восемь измерений
          <br />
          <em className="text-gold3 not-italic">одной страны</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Политическая стабильность, верховенство закона, экономическая свобода,
          стоимость жизни, доступность ВНЖ, качество жизни, цифровая
          инфраструктура и дрейф страны — сведённые в единый живой профиль по
          методологии ОЭСР.
        </p>
        <div className="flex gap-10">
          <MetricStat
            value={String(catalogA.ciiScore)}
            label={`CII · ${countryA.name}`}
          />
          <MetricStat
            value={catalogA.confidence.toFixed(2)}
            label="Достоверность"
          />
        </div>
      </div>

      <ChartFrame title={`${countryA.name} и ${countryB.name}`}>
        <RadarChart
          key={dataset.version}
          axes={CII_AXES}
          active={active}
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
      </ChartFrame>
    </SlideSection>
  );
}
