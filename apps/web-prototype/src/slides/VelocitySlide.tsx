import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame, MetricStat } from "@/components/ui/ChartFrame";
import { SparklineChart } from "@/components/charts/SparklineChart";
import { LEGAL_VELOCITY_TIMELINE } from "@/data/fixtures";

interface VelocitySlideProps {
  active: boolean;
}

export function VelocitySlide({ active }: VelocitySlideProps) {
  return (
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
      <div className="flex flex-col gap-6">
        <Kicker accent="blue">Legal Velocity Index</Kicker>
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
            value="6.4"
            label="Сигналов / квартал"
          />
          <MetricStat
            value="+2"
            label="За 24 мес"
          />
        </div>
      </div>

      <ChartFrame title="Legal Velocity · 24 месяца">
        <SparklineChart
          values={LEGAL_VELOCITY_TIMELINE}
          active={active}
          colorVar="--color-blue3"
        />
      </ChartFrame>
    </SlideSection>
  );
}
