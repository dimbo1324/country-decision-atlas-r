import type { DataJournalEntry } from "../../shared/api/data-journal";

type DataJournalEntryCardProps = {
  entry: DataJournalEntry;
};

export function DataJournalEntryCard({ entry }: DataJournalEntryCardProps) {
  const eventDate = new Date(entry.event_date).toLocaleDateString("ru-RU");

  return (
    <article
      className="sourceCard"
      data-testid="data-journal-entry"
    >
      <div className="sourceCardHeader">
        <h3>{entry.title}</h3>
        <span className="metaChip">{eventDate}</span>
      </div>
      <p>{entry.summary}</p>
      <div className="sourceMeta">
        <span>{entry.entry_type}</span>
        {entry.is_source_backed && <span>source-backed</span>}
      </div>
    </article>
  );
}
