import { Skeleton as SkeletonShell } from "@country-decision-atlas/ui";

type SkeletonProps = {
  lines?: number;
};

export function Skeleton({ lines = 3 }: SkeletonProps) {
  return <SkeletonShell lines={lines} />;
}
