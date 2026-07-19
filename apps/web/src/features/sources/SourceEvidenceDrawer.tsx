"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("sourceEvidenceDrawer");
  const { data, isPending, isError } = useQuery({
    ...sourceEvidenceQuery(sourceId ?? ""),
    enabled: Boolean(sourceId),
  });

  return (
    <Drawer
      open={Boolean(sourceId)}
      onClose={onClose}
      eyebrow={t("eyebrow")}
      title={sourceTitle ?? t("titleFallback")}
      closeLabel={t("close")}
    >
      <div
        className="flex flex-col gap-4"
        data-testid="source-evidence-drawer"
      >
        {isPending && <LoadingState message={t("loading")} />}
        {!isPending && isError && <ErrorState error={t("loadError")} />}
        {!isPending && !isError && (data?.items.length ?? 0) === 0 && (
          <EmptyState message={t("noEvidence")} />
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
