import { getTranslations } from "next-intl/server";
import { TripDetailView } from "../../../../features/trips/TripDetailView";
import { routes } from "../../../../shared/lib/routes";
import { AppBreadcrumbs } from "../../../../shared/ui/AppBreadcrumbs";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function TripDetailPage({ params }: PageProps) {
  const { id } = await params;
  const t = await getTranslations("tripDetailPage");
  return (
    <div className="flex flex-col gap-6">
      <AppBreadcrumbs
        items={[
          { label: t("trips"), href: routes.trips },
          { label: t("trip") },
        ]}
      />
      <TripDetailView tripId={id} />
    </div>
  );
}
