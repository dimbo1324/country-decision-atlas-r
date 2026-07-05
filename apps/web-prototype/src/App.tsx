import { useMemo, useState } from "react";
import { TopBar } from "@/components/shell/TopBar";
import { HorizontalPager } from "@/components/shell/HorizontalPager";
import { MobileStack } from "@/components/shell/MobileStack";
import { BackgroundFX } from "@/components/shell/BackgroundFX";
import { BackgroundTexture } from "@/components/shell/BackgroundTexture";
import { AnalysisOverlay } from "@/components/shell/AnalysisOverlay";
import { DatasetProvider, useDataset } from "@/state/DatasetContext";
import { HeroSlide } from "@/slides/HeroSlide";
import { CiiSlide } from "@/slides/CiiSlide";
import { VelocitySlide } from "@/slides/VelocitySlide";
import { DriftSlide } from "@/slides/DriftSlide";
import { MatrixSlide } from "@/slides/MatrixSlide";
import { TrustSlide } from "@/slides/TrustSlide";
import { CommunitySlide } from "@/slides/CommunitySlide";
import type { SlideDef } from "@/lib/types";

function AppShell() {
  const [index, setIndex] = useState(0);
  const { dataset, isRunning, runAnalysis } = useDataset();

  const slides = useMemo<SlideDef[]>(
    () => [
      {
        id: "hero",
        navLabel: "Обзор",
        accent: "gold",
        content: <HeroSlide active={index === 0} />,
      },
      {
        id: "cii",
        navLabel: "Индекс",
        accent: "gold",
        content: (
          <CiiSlide
            active={index === 1}
            dataset={dataset}
          />
        ),
      },
      {
        id: "velocity",
        navLabel: "Скорость",
        accent: "blue",
        content: (
          <VelocitySlide
            active={index === 2}
            dataset={dataset}
          />
        ),
      },
      {
        id: "drift",
        navLabel: "Дрейф",
        accent: "terra",
        content: (
          <DriftSlide
            active={index === 3}
            dataset={dataset}
          />
        ),
      },
      {
        id: "matrix",
        navLabel: "Сценарии",
        accent: "sage",
        content: (
          <MatrixSlide
            active={index === 4}
            dataset={dataset}
          />
        ),
      },
      {
        id: "trust",
        navLabel: "Доверие",
        accent: "blue",
        content: <TrustSlide dataset={dataset} />,
      },
      {
        id: "community",
        navLabel: "Сообщество",
        accent: "plum",
        content: <CommunitySlide dataset={dataset} />,
      },
    ],
    [index, dataset],
  );

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      <BackgroundTexture />
      <BackgroundFX />
      <TopBar
        slides={slides}
        activeIndex={index}
        onNavigate={setIndex}
        isRunning={isRunning}
        onRunAnalysis={runAnalysis}
      />
      <div className="relative z-10 h-full w-full">
        <HorizontalPager
          slides={slides}
          index={index}
          onIndexChange={setIndex}
        />
        <MobileStack slides={slides} />
      </div>
      <AnalysisOverlay active={isRunning} />
    </div>
  );
}

export default function App() {
  return (
    <DatasetProvider>
      <AppShell />
    </DatasetProvider>
  );
}
