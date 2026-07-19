import { getTranslations } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { AuthorProfileView } from "../../../../features/author-metrics/AuthorProfileView";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ userId: string }>;
};

export default async function AuthorProfilePage({ params }: PageProps) {
  const { userId } = await params;
  const t = await getTranslations("authorProfilePage");
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>{t("kicker")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
      </header>
      <AuthorProfileView userId={userId} />
    </div>
  );
}
