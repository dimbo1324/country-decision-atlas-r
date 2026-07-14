import { TripDetailView } from "../../../../features/trips";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function TripDetailPage({ params }: PageProps) {
  const { id } = await params;
  return (
    <div className="flex flex-col gap-6">
      <TripDetailView tripId={id} />
    </div>
  );
}
