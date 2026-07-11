import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { Card } from "@/components/ui/Card";
import { Counter } from "@/components/ui/Counter";
import { ProgressRing } from "@/components/charts/ProgressRing";
import { DonutChart } from "@/components/charts/DonutChart";
import type { Dataset } from "@/data/generator";

interface TrustSlideProps {
  active: boolean;
  dataset: Dataset;
}

export function TrustSlide({ active, dataset }: TrustSlideProps) {
  return (
    <SlideSection className="gap-9">
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-4 text-center">
        <Kicker
          accent="blue"
          className="justify-center"
        >
          Доверие и прозрачность
        </Kicker>
        <h2 className="font-display text-4xl font-bold sm:text-5xl">
          Насколько данным{" "}
          <em className="text-blue3 not-italic">можно верить</em>
        </h2>
      </div>

      <div className="mx-auto grid w-full max-w-5xl grid-cols-1 items-center gap-8 lg:grid-cols-[auto_1fr_auto]">
        <div className="flex justify-center">
          <ProgressRing
            key={dataset.version}
            value={dataset.trustScore}
            label="Скор доверия"
            active={active}
            colorVar="--color-blue3"
          />
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {dataset.trustDimensions.map((dimension) => (
            <Card
              key={dimension.label}
              accent="blue"
              className="flex min-h-[128px] flex-col gap-2 p-5"
            >
              <span className="font-display text-blue3 text-3xl leading-none font-bold">
                <Counter
                  key={`${dataset.version}-${dimension.label}`}
                  value={dimension.value}
                  suffix="%"
                  active
                />
              </span>
              <span className="font-mono text-c2 text-[10px] tracking-[0.2em] uppercase">
                {dimension.label}
              </span>
              <span className="text-c3 text-xs leading-relaxed text-pretty">
                {dimension.detail}
              </span>
            </Card>
          ))}
        </div>

        <div className="border-warm bg-bg3 flex flex-col gap-3 border p-6">
          <span className="font-mono text-c3 text-[10px] tracking-[0.2em] uppercase">
            Состав источников
          </span>
          <DonutChart
            key={dataset.version}
            segments={dataset.donutSegments}
            centerValue={`${dataset.donutSegments.length}`}
            centerLabel="Типа источников"
            active={active}
            size={172}
          />
        </div>
      </div>

      <p className="font-quote text-c4 mx-auto max-w-xl text-center text-xs italic">
        Каждая цифра платформы несёт уровень достоверности и дату верификации —
        прозрачность источника важнее лаконичности.
      </p>
    </SlideSection>
  );
}
