import { Skeleton } from "../../shared/ui/Skeleton";

export default function DecisionLoading() {
  return (
    <div className="pageShell">
      <div className="pageHeader">
        <Skeleton lines={2} />
      </div>
      <div className="decisionFormWrap">
        <Skeleton lines={5} />
      </div>
    </div>
  );
}
