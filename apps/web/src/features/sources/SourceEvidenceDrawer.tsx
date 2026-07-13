"use client";

import { useQuery } from "@tanstack/react-query";
import { Drawer } from "@country-decision-atlas/ui";
import { sourceEvidenceQuery } from "../../entities/sources/api";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { EvidenceCard } from "../../shared/ui/EvidenceCard";

type SourceEvidenceDrawerProps = {
  sourceId: string | null;
  sourceTitle?: string;
  onClose: () => void;
};

export function SourceEvidenceDrawer({
  sourceId,
  sourceTitle,
  onClose,
}: SourceEvidenceDrawerProps) {
  const { data, isPending, isError } = useQuery({
    ...sourceEvidenceQuery(sourceId ?? ""),
    enabled: Boolean(sourceId),
  });

  return (
    <Drawer
      open={Boolean(sourceId)}
      onClose={onClose}
      eyebrow="Доказательства источника"
      title={sourceTitle ?? "Источник"}
    >
      <div
        className="flex flex-col gap-4"
        data-testid="source-evidence-drawer"
      >
        {isPending && <LoadingState message="Загрузка доказательств…" />}
        {!isPending && isError && (
          <ErrorState error="Не удалось загрузить доказательства." />
        )}
        {!isPending && !isError && (data?.items.length ?? 0) === 0 && (
          <EmptyState message="К этому источнику доказательства не прикреплены." />
        )}
        {!isPending &&
          !isError &&
          data?.items.map((item) => (
            <EvidenceCard
              key={item.id}
              item={item}
              sourceTitle={sourceTitle}
            />
          ))}
      </div>
    </Drawer>
  );
}
