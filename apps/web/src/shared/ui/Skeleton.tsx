type SkeletonProps = {
  lines?: number;
};

export function Skeleton({ lines = 3 }: SkeletonProps) {
  return (
    <div className="skeletonWrap">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeletonLine" />
      ))}
    </div>
  );
}
