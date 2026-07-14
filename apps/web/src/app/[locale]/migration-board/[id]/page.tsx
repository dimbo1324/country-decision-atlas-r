import { Kicker } from "@country-decision-atlas/ui";
import { MigrationBoardDetailView } from "../../../../features/migration-board";

export const dynamic = "force-dynamic";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function MigrationBoardPostPage({ params }: Props) {
  const { id } = await params;
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Migration board</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Запись доски переезда
        </h1>
      </header>
      <MigrationBoardDetailView postId={id} />
    </div>
  );
}
