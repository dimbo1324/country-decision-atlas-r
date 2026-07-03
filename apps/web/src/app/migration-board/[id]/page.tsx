import { MigrationBoardDetailView } from "../../../features/migration-board";

export const dynamic = "force-dynamic";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function MigrationBoardPostPage({ params }: Props) {
  const { id } = await params;
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Migration board</p>
        <h1>Запись доски переезда</h1>
      </header>
      <MigrationBoardDetailView postId={id} />
    </div>
  );
}
