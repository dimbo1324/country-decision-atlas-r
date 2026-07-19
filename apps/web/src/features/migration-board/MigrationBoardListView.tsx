"use client";

import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import {
  Badge,
  Button,
  Card,
  Field,
  FieldLabel,
} from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import { boardPostsQuery } from "../../entities/migration-board/api";
import type { BoardPostFilters } from "../../shared/api/migrationBoard";
import { useAuth } from "../../shared/auth/AuthProvider";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";
import { GOAL_LABELS, TIMELINE_LABELS } from "./migration-board-labels";

const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";
const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

export function MigrationBoardListView() {
  const t = useTranslations("migrationBoard");
  const locale = useAppLocale();
  const searchParams = useSearchParams();
  const { user, isLoading: authLoading } = useAuth();
  const [filters, setFilters] = useState<BoardPostFilters>({
    destination_country: searchParams.get("destination") ?? "",
    origin_country: "",
    timeline_window: "",
    companion_goal: "",
  });

  const posts = useQuery(boardPostsQuery({ ...filters, limit: 40 }));

  if (posts.isPending) {
    return <LoadingState message={t("loadingList")} />;
  }

  if (posts.isError) {
    return (
      <ErrorState error={migrationBoardErrorMessage(posts.error, locale)} />
    );
  }

  const items = posts.data.items ?? [];

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="migration-board-page"
    >
      <Card
        interactive={false}
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        <Field>
          <FieldLabel htmlFor="board-destination-filter">
            {t("destinationCountryLabel")}
          </FieldLabel>
          <input
            id="board-destination-filter"
            className={inputClass}
            placeholder={t("destinationPlaceholder")}
            value={filters.destination_country ?? ""}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                destination_country: event.target.value,
              }))
            }
            data-testid="migration-board-destination-filter"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="board-origin-filter">
            {t("originCountryLabel")}
          </FieldLabel>
          <input
            id="board-origin-filter"
            className={inputClass}
            value={filters.origin_country ?? ""}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                origin_country: event.target.value,
              }))
            }
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="board-timeline-filter">
            {t("timelineLabel")}
          </FieldLabel>
          <select
            id="board-timeline-filter"
            className={selectClass}
            value={filters.timeline_window ?? ""}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                timeline_window: event.target.value,
              }))
            }
            data-testid="migration-board-timeline-filter"
          >
            {Object.entries(TIMELINE_LABELS[locale]).map(([value, label]) => (
              <option
                key={value}
                value={value}
              >
                {label}
              </option>
            ))}
          </select>
        </Field>
        <Field>
          <FieldLabel htmlFor="board-goal-filter">{t("goalLabel")}</FieldLabel>
          <select
            id="board-goal-filter"
            className={selectClass}
            value={filters.companion_goal ?? ""}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                companion_goal: event.target.value,
              }))
            }
            data-testid="migration-board-goal-filter"
          >
            {Object.entries(GOAL_LABELS[locale]).map(([value, label]) => (
              <option
                key={value}
                value={value}
              >
                {label}
              </option>
            ))}
          </select>
        </Field>
      </Card>

      <p className="text-c3 text-sm">{t("privacyNotice")}</p>

      <div className="flex flex-wrap gap-3">
        {authLoading ? null : user ? (
          <>
            <Link href={routes.migrationBoardNew}>
              <Button>{t("createPost")}</Button>
            </Link>
            <Link href={routes.accountMigrationBoard}>
              <Button variant="ghost">{t("myPosts")}</Button>
            </Link>
          </>
        ) : (
          <Link href={routes.login}>
            <Button data-testid="migration-board-login-cta">
              {t("loginToCreate")}
            </Button>
          </Link>
        )}
      </div>

      {items.length === 0 ? (
        <EmptyState message={t("emptyList")} />
      ) : (
        <div
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
          data-testid="migration-board-list"
        >
          {items.map((post) => (
            <Link
              href={routes.migrationBoardPost(post.id)}
              key={post.id}
            >
              <Card className="flex h-full flex-col gap-3">
                <span className="text-c4 text-xs">
                  {post.destination_country.name}
                </span>
                <span className="font-display text-lg font-semibold">
                  {post.title}
                </span>
                <p className="text-c3 line-clamp-3 text-sm">{post.summary}</p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="default">{post.timeline_window}</Badge>
                  <Badge variant="default">{post.companion_goal}</Badge>
                  <Badge variant="default">{post.author.display_name}</Badge>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
