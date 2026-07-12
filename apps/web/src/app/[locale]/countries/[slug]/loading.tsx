import { Skeleton } from "../../../../shared/ui/Skeleton";

export default function CountryLoading() {
  return (
    <div className="pageShell">
      <div className="pageHeader">
        <Skeleton lines={2} />
      </div>
      <div className="cardSections">
        <Skeleton lines={4} />
        <Skeleton lines={6} />
        <Skeleton lines={4} />
      </div>
    </div>
  );
}
