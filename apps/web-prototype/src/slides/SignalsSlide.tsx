import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { ChartFrame } from "@/components/ui/ChartFrame";
import { Heatmap } from "@/components/charts/Heatmap";
import { TimelineList } from "@/components/ui/TimelineList";
import { SignalTicker } from "@/components/ui/SignalTicker";
import type { Dataset } from "@/data/generator";

interface SignalsSlideProps {
  active: boolean;
  dataset: Dataset;
}

export function SignalsSlide({ active, dataset }: SignalsSlideProps) {
  return (
    <SlideSection className="gap-7">
      <div className="flex flex-col gap-4">
        <Kicker accent="terra">Поток правовых сигналов</Kicker>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
            Что изменилось
            <br />
            <em className="text-terra3 not-italic">в юрисдикциях</em>
          </h2>
          <p className="text-c3 max-w-md text-sm leading-relaxed">
            Дифф по каждой стране: новые правовые сигналы и смена направления
            дрейфа с момента вашего последнего визита. Карта активности
            показывает, где право «кипит».
          </p>
        </div>
      </div>

      <SignalTicker items={dataset.tickerItems} />

      <div className="grid min-h-0 flex-1 grid-cols-1 gap-6 lg:grid-cols-2">
        <ChartFrame
          title="Активность сигналов · юрисдикция × месяц"
          className="min-h-[260px]"
        >
          <Heatmap
            key={dataset.version}
            data={dataset.heatmap}
            active={active}
          />
        </ChartFrame>
        <div className="border-warm bg-bg3 scrollbar-thin flex min-h-[260px] flex-col overflow-y-auto border p-5">
          <span className="font-mono text-c3 mb-2 text-[10px] tracking-[0.2em] uppercase">
            Лента изменений · с прошлого визита
          </span>
          <TimelineList events={dataset.signalEvents} />
        </div>
      </div>
    </SlideSection>
  );
}
