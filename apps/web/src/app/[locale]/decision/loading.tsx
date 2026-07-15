import { Skeleton } from "../../../shared/ui/Skeleton";

export default function DecisionLoading() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-3">
        <Skeleton lines={2} />
      </div>
      <div className="flex flex-col gap-4">
        <Skeleton lines={5} />
      </div>
    </div>
  );
}
