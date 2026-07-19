import { getTranslations } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { MigrationBoardDetailView } from "../../../../features/migration-board";
import { routes } from "../../../../shared/lib/routes";
import { AppBreadcrumbs } from "../../../../shared/ui/AppBreadcrumbs";

export const dynamic = "force-dynamic";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function MigrationBoardPostPage({ params }: Props) {
  const { id } = await params;
  const t = await getTranslations("migrationBoardPostPage");
  return (
    <div className="flex flex-col gap-6">
      <AppBreadcrumbs
        items={[
          { label: t("breadcrumbBoard"), href: routes.migrationBoard },
          { label: t("breadcrumbPost") },
        ]}
      />
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
      </header>
      <MigrationBoardDetailView postId={id} />
    </div>
  );
}
