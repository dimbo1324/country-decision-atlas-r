"use client";

import { useLocale } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import {
  Button,
  Card,
  Field,
  FieldHint,
  FieldLabel,
} from "@country-decision-atlas/ui";
import { getPathname, useRouter } from "../../i18n/navigation";
import {
  useCreateBoardPostMutation,
  useSubmitBoardPostMutation,
} from "../../entities/migration-board/api";
import type { CreateMigrationBoardPostRequest } from "../../shared/api/migrationBoard";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";
const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";

const initialPayload: CreateMigrationBoardPostRequest = {
  destination_country_slug: "",
  origin_country_slug: "",
  title: "",
  summary: "",
  timeline_window: "unknown",
  budget_range: "undisclosed",
  household_type: "undisclosed",
  migration_stage: "researching",
  companion_goal: "info_exchange",
  preferred_language: "undisclosed",
  visibility: "members_only",
  risk_acknowledged: false,
  legal_disclaimer_acknowledged: false,
  contact_requests_enabled: true,
  tags: [],
};

export function MigrationBoardFormView() {
  const { user, isLoading } = useAuth();
  const locale = useLocale();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [payload, setPayload] = useState<CreateMigrationBoardPostRequest>({
    ...initialPayload,
    destination_country_slug: searchParams.get("destination") ?? "",
    route_id: searchParams.get("route_id") ?? undefined,
  });
  const [tagInput, setTagInput] = useState("");
  const createBoardPost = useCreateBoardPostMutation();
  const submitBoardPost = useSubmitBoardPostMutation();
  const isSaving = createBoardPost.isPending || submitBoardPost.isPending;

  if (isLoading) {
    return <LoadingState message="Проверка доступа…" />;
  }

  if (!user) {
    return (
      <ErrorState
        error="Войдите, чтобы создать запись на доске переезда."
        backHref={getPathname({ href: routes.login, locale })}
        backLabel="Войти"
      />
    );
  }

  function update<K extends keyof CreateMigrationBoardPostRequest>(
    key: K,
    value: CreateMigrationBoardPostRequest[K],
  ) {
    setPayload((current) => ({ ...current, [key]: value }));
  }

  async function save(submit: boolean) {
    try {
      const tags = tagInput
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean);
      const created = await createBoardPost.mutateAsync({ ...payload, tags });
      if (submit) {
        await submitBoardPost.mutateAsync(created.id);
      }
      router.push(routes.accountMigrationBoard);
    } catch {
      // surfaced via createBoardPost.error / submitBoardPost.error below
    }
  }

  return (
    <form
      className="flex flex-col gap-5"
      data-testid="migration-board-new-form"
    >
      {(createBoardPost.error ?? submitBoardPost.error) != null && (
        <ErrorState
          error={migrationBoardErrorMessage(
            createBoardPost.error ?? submitBoardPost.error,
          )}
        />
      )}

      <Card
        interactive={false}
        className="flex flex-col gap-5"
      >
        <Field>
          <FieldLabel htmlFor="board-destination">Страна назначения</FieldLabel>
          <input
            id="board-destination"
            className={inputClass}
            value={payload.destination_country_slug}
            onChange={(event) =>
              update("destination_country_slug", event.target.value)
            }
            placeholder="uruguay"
            required
            data-testid="migration-board-destination-input"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="board-origin">Страна отправления</FieldLabel>
          <input
            id="board-origin"
            className={inputClass}
            value={payload.origin_country_slug ?? ""}
            onChange={(event) =>
              update("origin_country_slug", event.target.value)
            }
            placeholder="russia"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="board-route-id">Route ID</FieldLabel>
          <input
            id="board-route-id"
            className={inputClass}
            value={payload.route_id ?? ""}
            onChange={(event) =>
              update("route_id", event.target.value || undefined)
            }
          />
        </Field>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field>
            <FieldLabel htmlFor="board-scenario">Scenario</FieldLabel>
            <input
              id="board-scenario"
              className={inputClass}
              value={payload.scenario_slug ?? ""}
              onChange={(event) =>
                update("scenario_slug", event.target.value || undefined)
              }
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="board-persona">Persona</FieldLabel>
            <input
              id="board-persona"
              className={inputClass}
              value={payload.persona_slug ?? ""}
              onChange={(event) =>
                update("persona_slug", event.target.value || undefined)
              }
            />
          </Field>
        </div>
        <Field>
          <FieldLabel htmlFor="board-title">Заголовок</FieldLabel>
          <input
            id="board-title"
            className={inputClass}
            value={payload.title}
            onChange={(event) => update("title", event.target.value)}
            minLength={6}
            maxLength={140}
            required
            data-testid="migration-board-title-input"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="board-summary">Описание</FieldLabel>
          <textarea
            id="board-summary"
            className={inputClass}
            value={payload.summary}
            onChange={(event) => update("summary", event.target.value)}
            minLength={30}
            maxLength={1200}
            rows={6}
            required
            data-testid="migration-board-summary-input"
          />
          <FieldHint>
            Не публикуйте контакты (email, телефон, Telegram) в открытом тексте.
          </FieldHint>
        </Field>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Field>
            <FieldLabel htmlFor="board-timeline">Срок</FieldLabel>
            <select
              id="board-timeline"
              className={selectClass}
              value={payload.timeline_window}
              onChange={(event) =>
                update("timeline_window", event.target.value)
              }
            >
              <option value="unknown">Пока не знаю</option>
              <option value="0_3_months">0-3 месяца</option>
              <option value="3_6_months">3-6 месяцев</option>
              <option value="6_12_months">6-12 месяцев</option>
              <option value="12_plus_months">12+ месяцев</option>
            </select>
          </Field>
          <Field>
            <FieldLabel htmlFor="board-stage">Стадия</FieldLabel>
            <select
              id="board-stage"
              className={selectClass}
              value={payload.migration_stage}
              onChange={(event) =>
                update("migration_stage", event.target.value)
              }
            >
              <option value="researching">Изучаю</option>
              <option value="preparing_documents">Готовлю документы</option>
              <option value="applying">Подаюсь</option>
              <option value="waiting_decision">Жду решение</option>
              <option value="relocating_soon">Скоро переезжаю</option>
              <option value="already_relocated">Уже переехал</option>
              <option value="on_hold">На паузе</option>
            </select>
          </Field>
          <Field>
            <FieldLabel htmlFor="board-goal">Цель</FieldLabel>
            <select
              id="board-goal"
              className={selectClass}
              value={payload.companion_goal}
              onChange={(event) => update("companion_goal", event.target.value)}
            >
              <option value="info_exchange">Обмен информацией</option>
              <option value="travel_together">Поездка вместе</option>
              <option value="housing_search">Поиск жилья</option>
              <option value="document_support">Документы</option>
              <option value="study_group">Учёба</option>
              <option value="business_network">Бизнес</option>
              <option value="family_network">Семья</option>
            </select>
          </Field>
          <Field>
            <FieldLabel htmlFor="board-visibility">Видимость</FieldLabel>
            <select
              id="board-visibility"
              className={selectClass}
              value={payload.visibility}
              onChange={(event) => update("visibility", event.target.value)}
            >
              <option value="members_only">Только участники</option>
              <option value="public">Публично</option>
              <option value="private">Приватно</option>
            </select>
          </Field>
        </div>
        <Field>
          <FieldLabel htmlFor="board-tags">Теги через запятую</FieldLabel>
          <input
            id="board-tags"
            className={inputClass}
            value={tagInput}
            onChange={(event) => setTagInput(event.target.value)}
            placeholder="housing, documents, remote_work"
          />
        </Field>
        <label className="text-c2 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            className="accent-gold"
            checked={payload.risk_acknowledged}
            onChange={(event) =>
              update("risk_acknowledged", event.target.checked)
            }
            data-testid="migration-board-risk-checkbox"
          />
          Я понимаю риски переезда и публичной записи.
        </label>
        <label className="text-c2 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            className="accent-gold"
            checked={payload.legal_disclaimer_acknowledged}
            onChange={(event) =>
              update("legal_disclaimer_acknowledged", event.target.checked)
            }
            data-testid="migration-board-legal-checkbox"
          />
          Я понимаю, что это не юридическая консультация.
        </label>
        <label className="text-c2 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            className="accent-gold"
            checked={payload.contact_requests_enabled}
            onChange={(event) =>
              update("contact_requests_enabled", event.target.checked)
            }
          />
          Разрешить contact requests через платформу.
        </label>
        <div className="flex gap-3">
          <Button
            type="button"
            variant="ghost"
            disabled={isSaving}
            onClick={() => void save(false)}
            data-testid="migration-board-save-draft"
          >
            Сохранить черновик
          </Button>
          <Button
            type="button"
            disabled={isSaving}
            onClick={() => void save(true)}
            data-testid="migration-board-submit"
          >
            Отправить на модерацию
          </Button>
        </div>
      </Card>
    </form>
  );
}
