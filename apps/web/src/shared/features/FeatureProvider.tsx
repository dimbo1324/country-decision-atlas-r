"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { featureFlagsApi } from "../api/feature-flags";
import type { FeatureFlag } from "../api/feature-flags";
import { isFeatureEnabled } from "../lib/features";

interface FeatureContextValue {
  features: FeatureFlag[];
  isLoading: boolean;
}

const FeatureContext = createContext<FeatureContextValue>({
  features: [],
  isLoading: true,
});

/** Reads /platform/features once per session. A client-only fetch for now
 * (no SSR prefetch) — the invariant this exists to protect ("new surfaces
 * ship disabled by default") holds either way, since `<Feature>` renders
 * nothing until this resolves. */
export function FeatureProvider({ children }: { children: React.ReactNode }) {
  const [features, setFeatures] = useState<FeatureFlag[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    featureFlagsApi
      .getFeatures()
      .then((response) => {
        if (active) setFeatures(response.items);
      })
      .catch(() => {
        if (active) setFeatures([]);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <FeatureContext.Provider value={{ features, isLoading }}>
      {children}
    </FeatureContext.Provider>
  );
}

export function useFeatures(): FeatureContextValue {
  return useContext(FeatureContext);
}

export function useFeatureEnabled(featureKey: string): boolean {
  const { features } = useFeatures();
  return isFeatureEnabled(features, featureKey);
}
