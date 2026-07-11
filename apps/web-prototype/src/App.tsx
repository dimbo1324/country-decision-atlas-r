import { useMemo, useState } from "react";
import { TopBar } from "@/components/shell/TopBar";
import { HorizontalPager } from "@/components/shell/HorizontalPager";
import { MobileStack } from "@/components/shell/MobileStack";
import { BackgroundFX } from "@/components/shell/BackgroundFX";
import { BackgroundTexture } from "@/components/shell/BackgroundTexture";
import { AnalysisOverlay } from "@/components/shell/AnalysisOverlay";
import { LibraryOverlay } from "@/components/shell/LibraryOverlay";
import { DatasetProvider, useDataset } from "@/state/DatasetContext";
import { HeroSlide } from "@/slides/HeroSlide";
import { CiiSlide } from "@/slides/CiiSlide";
import { MetricsSlide } from "@/slides/MetricsSlide";
import { VelocitySlide } from "@/slides/VelocitySlide";
import { DriftSlide } from "@/slides/DriftSlide";
import { SignalsSlide } from "@/slides/SignalsSlide";
import { MatrixSlide } from "@/slides/MatrixSlide";
import { PassportSlide } from "@/slides/PassportSlide";
import { TrustSlide } from "@/slides/TrustSlide";
import { CommunitySlide } from "@/slides/CommunitySlide";
import type { SlideDef } from "@/lib/types";

function AppShell() {
  const [index, setIndex] = useState(0);
  const [libraryOpen, setLibraryOpen] = useState(false);
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
        id: "metrics",
        navLabel: "Метрики",
        accent: "gold",
        content: (
          <MetricsSlide
            active={index === 2}
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
            active={index === 3}
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
            active={index === 4}
            dataset={dataset}
          />
        ),
      },
      {
        id: "signals",
        navLabel: "Сигналы",
        accent: "terra",
        content: (
          <SignalsSlide
            active={index === 5}
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
            active={index === 6}
            dataset={dataset}
          />
        ),
      },
      {
        id: "passport",
        navLabel: "Паспорт",
        accent: "gold",
        content: (
          <PassportSlide
            active={index === 7}
            dataset={dataset}
          />
        ),
      },
      {
        id: "trust",
        navLabel: "Доверие",
        accent: "blue",
        content: (
          <TrustSlide
            active={index === 8}
            dataset={dataset}
          />
        ),
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
        onOpenLibrary={() => setLibraryOpen(true)}
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
      <LibraryOverlay
        open={libraryOpen}
        onClose={() => setLibraryOpen(false)}
        dataset={dataset}
      />
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
