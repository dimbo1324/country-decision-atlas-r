import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { Card } from "@/components/ui/Card";
import { Counter } from "@/components/ui/Counter";
import type { Dataset } from "@/data/generator";

interface TrustSlideProps {
  dataset: Dataset;
}

export function TrustSlide({ dataset }: TrustSlideProps) {
  return (
    <SlideSection className="gap-12">
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
        <p className="text-c2 text-base leading-relaxed">
          Каждая цифра платформы несёт уровень достоверности и дату верификации.
          Прозрачность источника важнее лаконичности.
        </p>
      </div>

      <div className="mx-auto grid w-full max-w-4xl grid-cols-2 gap-5 lg:grid-cols-4">
        {dataset.trustDimensions.map((dimension) => (
          <Card
            key={dimension.label}
            accent="blue"
            className="flex flex-col gap-3"
          >
            <span className="font-display text-blue3 text-3xl font-bold">
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
            <span className="text-c3 text-xs leading-relaxed">
              {dimension.detail}
            </span>
          </Card>
        ))}
      </div>
    </SlideSection>
  );
}
