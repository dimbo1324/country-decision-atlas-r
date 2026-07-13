"use client";

import { useQuery } from "@tanstack/react-query";
import { Drawer } from "@country-decision-atlas/ui";
import { legalSignalEvidenceQuery } from "../../entities/legal-signals/api";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { EvidenceCard } from "../../shared/ui/EvidenceCard";

type LegalSignalEvidenceDrawerProps = {
  signalId: string | null;
  signalTitle?: string;
  onClose: () => void;
};

export function LegalSignalEvidenceDrawer({
  signalId,
  signalTitle,
  onClose,
}: LegalSignalEvidenceDrawerProps) {
  const { data, isPending, isError } = useQuery({
    ...legalSignalEvidenceQuery(signalId ?? ""),
    enabled: Boolean(signalId),
  });

  return (
    <Drawer
      open={Boolean(signalId)}
      onClose={onClose}
      eyebrow="Доказательства сигнала"
      title={signalTitle ?? "Сигнал"}
    >
      <div
        className="flex flex-col gap-4"
        data-testid="legal-signal-evidence-drawer"
      >
        {isPending && <LoadingState message="Загрузка доказательств…" />}
        {!isPending && isError && (
          <ErrorState error="Не удалось загрузить доказательства." />
        )}
        {!isPending && !isError && (data?.items.length ?? 0) === 0 && (
          <EmptyState message="К этому сигналу доказательства не прикреплены." />
        )}
        {!isPending &&
          !isError &&
          data?.items.map((item) => (
            <EvidenceCard
              key={item.id}
              item={item}
            />
          ))}
      </div>
    </Drawer>
  );
}
