"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import {
  listBoardPosts,
  type BoardPostFilters,
  type MigrationBoardPostListResponse,
} from "../../shared/api";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

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
  const [data, setData] = useState<MigrationBoardPostListResponse | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setError(null);
    listBoardPosts({ ...filters, limit: 40 })
      .then((response) => {
        if (active) setData(response);
      })
      .catch((err: unknown) => {
        if (active) setError(err);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [filters]);

  if (isLoading) {
    return <LoadingState message="Загрузка доски переезда…" />;
  }

  if (error) {
    return <ErrorState error={migrationBoardErrorMessage(error)} />;
  }

  const items = data?.items ?? [];

  return (
    <div className="searchPageContainer" data-testid="migration-board-page">
      <div className="toolbar">
        <input
          className="formInput"
          placeholder="Страна назначения, например uruguay"
          value={filters.destination_country ?? ""}
          onChange={(event) =>
            setFilters((current) => ({
              ...current,
              destination_country: event.target.value,
            }))
          }
          data-testid="migration-board-destination-filter"
        />
        <input
          className="formInput"
          placeholder="Страна отправления"
          value={filters.origin_country ?? ""}
          onChange={(event) =>
            setFilters((current) => ({
              ...current,
              origin_country: event.target.value,
            }))
          }
        />
        <select
          className="formInput"
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
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <select
          className="formInput"
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
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className="notice">
        Контакты, email и Telegram не публикуются. Записи появляются в общем списке
        только после модерации и подтверждения рисков.
      </div>

      <div className="toolbar">
        {authLoading ? null : user ? (
          <>
            <Link className="runButton" href={routes.migrationBoardNew}>
              Создать запись
            </Link>
            <Link className="secondaryButton" href={routes.accountMigrationBoard}>
              Мои записи
            </Link>
          </>
        ) : (
          <Link
            className="runButton"
            href={routes.login}
            data-testid="migration-board-login-cta"
          >
            Войти, чтобы создать запись
          </Link>
        )}
      </div>

      {items.length === 0 ? (
        <EmptyState message="Пока нет опубликованных записей." />
      ) : (
        <div className="cardGrid" data-testid="migration-board-list">
          {items.map((post) => (
            <Link
              className="summaryCard"
              href={routes.migrationBoardPost(post.id)}
              key={post.id}
            >
              <p className="eyebrow">{post.destination_country.name}</p>
              <h2>{post.title}</h2>
              <p>{post.summary}</p>
              <div className="badgeRow">
                <span className="badge">{post.timeline_window}</span>
                <span className="badge">{post.companion_goal}</span>
                <span className="badge">{post.author.display_name}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
