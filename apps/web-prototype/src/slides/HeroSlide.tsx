import { ArrowRight } from "lucide-react";
import { SlideSection } from "@/components/shell/SlideSection";
import { Counter } from "@/components/ui/Counter";
import { Kicker } from "@/components/ui/Kicker";

interface HeroSlideProps {
  active: boolean;
}

const STATS = [
  { value: 195, label: "Юрисдикций" },
  { value: 8, label: "Измерений CII" },
  { value: 12, label: "Модулей" },
  { value: 94, suffix: "%", label: "Ср. достоверность" },
];

export function HeroSlide({ active }: HeroSlideProps) {
  return (
    <SlideSection className="items-center text-center">
      <Kicker>Аналитическая платформа · Осн. MMXXVI · Онлайн</Kicker>
      <h1 className="text-shimmer font-display py-2 text-6xl leading-[1.15] font-bold sm:text-7xl lg:text-8xl">
        CountryAtlas
      </h1>
      <p className="font-body text-c2 max-w-2xl text-lg italic sm:text-xl">
        Разведывательная платформа для решений о релокации, резидентстве и
        юрисдикции
      </p>
      <p className="text-c3 max-w-xl text-sm">
        Композитный индекс из открытых международных источников, уникальные
        метрики, считаемые из собственных данных, и живой поток правовых
        сигналов — всё в одном архивном кабинете.
      </p>

      <div className="mt-4 flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
        {STATS.map((stat) => (
          <div
            key={stat.label}
            className="flex flex-col items-center gap-1"
          >
            <span className="font-display text-gold3 text-4xl font-bold">
              <Counter
                value={stat.value}
                suffix={stat.suffix}
                active={active}
              />
            </span>
            <span className="font-mono text-c3 text-[10px] tracking-[0.2em] uppercase">
              {stat.label}
            </span>
          </div>
        ))}
      </div>

      <div className="font-mono text-c3 mt-6 inline-flex items-center gap-2 text-[10px] tracking-[0.25em] uppercase">
        Далее — движение вбок
        <ArrowRight
          width={14}
          height={14}
          strokeWidth={1.5}
        />
      </div>

      <p className="font-quote text-c4 mt-10 text-xs italic">
        Это не юридическая консультация. Данные носят справочный характер ·
        обновлено 07.2026
      </p>
    </SlideSection>
  );
}
