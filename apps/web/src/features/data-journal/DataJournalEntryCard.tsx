import { Badge, Card } from "@country-decision-atlas/ui";
import type { DataJournalEntry } from "../../shared/api/data-journal";

type DataJournalEntryCardProps = {
  entry: DataJournalEntry;
};

export function DataJournalEntryCard({ entry }: DataJournalEntryCardProps) {
  const eventDate = new Date(entry.event_date).toLocaleDateString("ru-RU");

  return (
    <div data-testid="data-journal-entry">
    <Card
      interactive={false}
      className="flex flex-col gap-2"
    >
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-display text-base font-semibold">{entry.title}</h3>
        <Badge variant="default">{eventDate}</Badge>
      </div>
      <p className="text-c3 text-sm leading-relaxed">{entry.summary}</p>
      <div className="flex flex-wrap gap-2">
        <Badge variant="default">{entry.entry_type}</Badge>
        {entry.is_source_backed && <Badge variant="trust">source-backed</Badge>}
      </div>
    </Card>
    </div>
  );
}
