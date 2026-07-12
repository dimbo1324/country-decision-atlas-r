import { Skeleton } from "../../../shared/ui/Skeleton";

export default function CountriesLoading() {
  return (
    <div className="pageShell">
      <div className="pageHeader">
        <Skeleton lines={2} />
      </div>
      <div className="dataGrid">
        <Skeleton lines={3} />
        <Skeleton lines={3} />
      </div>
    </div>
  );
}
