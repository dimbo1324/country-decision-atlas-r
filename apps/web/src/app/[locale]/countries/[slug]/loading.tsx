import { Skeleton } from "../../../../shared/ui/Skeleton";

export default function CountryLoading() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-3">
        <Skeleton lines={2} />
      </div>
      <div className="flex flex-col gap-4">
        <Skeleton lines={4} />
        <Skeleton lines={6} />
        <Skeleton lines={4} />
      </div>
    </div>
  );
}
