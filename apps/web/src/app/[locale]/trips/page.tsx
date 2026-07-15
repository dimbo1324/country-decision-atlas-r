import { Kicker } from "@country-decision-atlas/ui";
import { TripListView } from "../../../features/trips/TripListView";

export const dynamic = "force-dynamic";

export default function TripsPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Личный кабинет</Kicker>
        <h1 className="font-display text-4xl font-bold">Поездки</h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Планируйте маршрут, чек-лист и напоминания для каждой поездки.
        </p>
      </header>
      <TripListView />
    </div>
  );
}
