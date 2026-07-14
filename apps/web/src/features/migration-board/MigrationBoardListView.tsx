"use client";

import { useQuery } from "@tanstack/react-query";
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
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";
const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

const TIMELINES = [
  ["", "Любой срок"],
  ["0_3_months", "0-3 месяца"],
  ["3_6_months", "3-6 месяцев"],
  ["6_12_months", "6-12 месяцев"],
  ["12_plus_months", "12+ месяцев"],
  ["unknown", "Пока не знаю"],
];

const GOALS = [
  ["", "Любая цель"],
  ["info_exchange", "Обмен информацией"],
  ["travel_together", "Поездка вместе"],
  ["housing_search", "Поиск жилья"],
  ["document_support", "Документы"],
  ["study_group", "Учёба"],
  ["business_network", "Бизнес"],
  ["family_network", "Семья"],
];

export function MigrationBoardListView() {
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
    return <LoadingState message="Загрузка доски переезда…" />;
  }

  if (posts.isError) {
    return <ErrorState error={migrationBoardErrorMessage(posts.error)} />;
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
            Страна назначения
          </FieldLabel>
          <input
            id="board-destination-filter"
            className={inputClass}
            placeholder="например uruguay"
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
            Страна отправления
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
          <FieldLabel htmlFor="board-timeline-filter">Срок</FieldLabel>
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
            {TIMELINES.map(([value, label]) => (
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
          <FieldLabel htmlFor="board-goal-filter">Цель</FieldLabel>
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
            {GOALS.map(([value, label]) => (
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

      <p className="text-c3 text-sm">
        Контакты, email и Telegram не публикуются. Записи появляются в общем
        списке только после модерации и подтверждения рисков.
      </p>

      <div className="flex flex-wrap gap-3">
        {authLoading ? null : user ? (
          <>
            <Link href={routes.migrationBoardNew}>
              <Button>Создать запись</Button>
            </Link>
            <Link href={routes.accountMigrationBoard}>
              <Button variant="ghost">Мои записи</Button>
            </Link>
          </>
        ) : (
          <Link href={routes.login}>
            <Button data-testid="migration-board-login-cta">
              Войти, чтобы создать запись
            </Button>
          </Link>
        )}
      </div>

      {items.length === 0 ? (
        <EmptyState message="Пока нет опубликованных записей." />
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
