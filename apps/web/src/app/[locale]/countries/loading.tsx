import { Skeleton } from "../../../shared/ui/Skeleton";

export default function CountriesLoading() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-3">
        <Skeleton lines={2} />
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Skeleton lines={3} />
        <Skeleton lines={3} />
      </div>
    </div>
  );
}
