"use client";

import type { ReactNode } from "react";
import { useFeatureEnabled } from "./FeatureProvider";

interface FeatureProps {
  flag: string;
  children: ReactNode;
  fallback?: ReactNode;
}

/** Gates a surface behind a platform feature flag — the server invariant
 * "new user-facing surfaces launch behind flags, disabled until acceptance"
 * needs a client-side counterpart or every new screen ships silently on. */
export function Feature({ flag, children, fallback = null }: FeatureProps) {
  const enabled = useFeatureEnabled(flag);
  return enabled ? <>{children}</> : <>{fallback}</>;
}
