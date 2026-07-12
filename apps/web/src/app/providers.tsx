"use client";

import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FeatureProvider } from "../shared/features/FeatureProvider";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Content pages (country cards, methodology, glossary) change
            // rarely; live-metric-style data opts into a shorter staleTime
            // per query instead of lowering this global default.
            staleTime: 60_000,
            retry: 1,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <FeatureProvider>{children}</FeatureProvider>
    </QueryClientProvider>
  );
}
