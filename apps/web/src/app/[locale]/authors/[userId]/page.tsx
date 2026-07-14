import { Kicker } from "@country-decision-atlas/ui";
import { AuthorProfileView } from "../../../../features/author-metrics";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ userId: string }>;
};

export default async function AuthorProfilePage({ params }: PageProps) {
  const { userId } = await params;
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Профиль автора</Kicker>
        <h1 className="font-display text-4xl font-bold">Автор платформы</h1>
      </header>
      <AuthorProfileView userId={userId} />
    </div>
  );
}
