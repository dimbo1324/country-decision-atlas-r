import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { RadarChart } from "@/components/charts/RadarChart";
import { CII_AXES, CII_COUNTRIES } from "@/data/fixtures";

interface CiiSlideProps {
  active: boolean;
}

export function CiiSlide({ active }: CiiSlideProps) {
  return (
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="gold">Country Intelligence Index</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Восемь измерений
          <br />
          <em className="text-gold3 not-italic">одной страны</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Политическая стабильность, верховенство закона, экономическая свобода,
          стоимость жизни, доступность ВНЖ, качество жизни, цифровая
          инфраструктура и Country Drift — сведённые в единый живой профиль по
          методологии OECD.
        </p>
        <div className="flex gap-10">
          <MetricStat
            value="91"
            label={`CII · ${CII_COUNTRIES.a.name}`}
          />
          <MetricStat
            value="0.96"
            label="Confidence"
          />
        </div>
      </div>

      <ChartFrame title={`${CII_COUNTRIES.a.name} vs ${CII_COUNTRIES.b.name}`}>
        <RadarChart
          axes={CII_AXES}
          active={active}
          series={[
            {
              label: CII_COUNTRIES.a.name,
              values: CII_COUNTRIES.a.values,
              colorVar: "--color-gold",
            },
            {
              label: CII_COUNTRIES.b.name,
              values: CII_COUNTRIES.b.values,
              colorVar: "--color-blue3",
            },
          ]}
        />
      </ChartFrame>
    </SlideSection>
  );
}
