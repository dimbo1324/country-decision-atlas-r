import { useMemo, useState } from "react";
import { TopBar } from "@/components/shell/TopBar";
import { HorizontalPager } from "@/components/shell/HorizontalPager";
import { MobileStack } from "@/components/shell/MobileStack";
import { BackgroundFX } from "@/components/shell/BackgroundFX";
import { HeroSlide } from "@/slides/HeroSlide";
import { CiiSlide } from "@/slides/CiiSlide";
import { VelocitySlide } from "@/slides/VelocitySlide";
import { DriftSlide } from "@/slides/DriftSlide";
import { MatrixSlide } from "@/slides/MatrixSlide";
import { TrustSlide } from "@/slides/TrustSlide";
import { CommunitySlide } from "@/slides/CommunitySlide";
import type { SlideDef } from "@/lib/types";

export default function App() {
  const [index, setIndex] = useState(0);

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
        navLabel: "CII",
        accent: "gold",
        content: <CiiSlide active={index === 1} />,
      },
      {
        id: "velocity",
        navLabel: "Velocity",
        accent: "blue",
        content: <VelocitySlide active={index === 2} />,
      },
      {
        id: "drift",
        navLabel: "Direction",
        accent: "terra",
        content: <DriftSlide active={index === 3} />,
      },
      {
        id: "matrix",
        navLabel: "Сценарии",
        accent: "sage",
        content: <MatrixSlide active={index === 4} />,
      },
      {
        id: "trust",
        navLabel: "Trust",
        accent: "blue",
        content: <TrustSlide />,
      },
      {
        id: "community",
        navLabel: "Сообщество",
        accent: "plum",
        content: <CommunitySlide />,
      },
    ],
    [index],
  );

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      <BackgroundFX />
      <TopBar
        slides={slides}
        activeIndex={index}
        onNavigate={setIndex}
      />
      <div className="relative z-10 h-full w-full">
        <HorizontalPager
          slides={slides}
          index={index}
          onIndexChange={setIndex}
        />
        <MobileStack slides={slides} />
      </div>
    </div>
  );
}
