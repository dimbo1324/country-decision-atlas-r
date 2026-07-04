"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import {
  createBoardPost,
  submitBoardPost,
  type CreateMigrationBoardPostRequest,
} from "../../shared/api";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";

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
  const router = useRouter();
  const searchParams = useSearchParams();
  const [payload, setPayload] = useState<CreateMigrationBoardPostRequest>({
    ...initialPayload,
    destination_country_slug: searchParams.get("destination") ?? "",
    route_id: searchParams.get("route_id") ?? undefined,
  });
  const [tagInput, setTagInput] = useState("");
  const [error, setError] = useState<unknown | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  if (isLoading) {
    return <LoadingState message="Проверка доступа…" />;
  }

  if (!user) {
    return (
      <ErrorState
        error="Войдите, чтобы создать запись на доске переезда."
        backHref={routes.login}
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
    setIsSaving(true);
    setError(null);
    try {
      const tags = tagInput
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean);
      const created = await createBoardPost({ ...payload, tags });
      if (submit) {
        await submitBoardPost(created.id);
      }
      router.push(routes.accountMigrationBoard);
    } catch (err: unknown) {
      setError(err);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <form
      className="authForm"
      data-testid="migration-board-new-form"
    >
      {error !== null && (
        <ErrorState error={migrationBoardErrorMessage(error)} />
      )}
      <label className="formGroup">
        <span className="formLabel">Страна назначения</span>
        <input
          className="formInput"
          value={payload.destination_country_slug}
          onChange={(event) =>
            update("destination_country_slug", event.target.value)
          }
          placeholder="uruguay"
          required
          data-testid="migration-board-destination-input"
        />
      </label>
      <label className="formGroup">
        <span className="formLabel">Страна отправления</span>
        <input
          className="formInput"
          value={payload.origin_country_slug ?? ""}
          onChange={(event) =>
            update("origin_country_slug", event.target.value)
          }
          placeholder="russia"
        />
      </label>
      <label className="formGroup">
        <span className="formLabel">Route ID</span>
        <input
          className="formInput"
          value={payload.route_id ?? ""}
          onChange={(event) =>
            update("route_id", event.target.value || undefined)
          }
        />
      </label>
      <div className="toolbar">
        <label className="formGroup">
          <span className="formLabel">Scenario</span>
          <input
            className="formInput"
            value={payload.scenario_slug ?? ""}
            onChange={(event) =>
              update("scenario_slug", event.target.value || undefined)
            }
          />
        </label>
        <label className="formGroup">
          <span className="formLabel">Persona</span>
          <input
            className="formInput"
            value={payload.persona_slug ?? ""}
            onChange={(event) =>
              update("persona_slug", event.target.value || undefined)
            }
          />
        </label>
      </div>
      <label className="formGroup">
        <span className="formLabel">Заголовок</span>
        <input
          className="formInput"
          value={payload.title}
          onChange={(event) => update("title", event.target.value)}
          minLength={6}
          maxLength={140}
          required
          data-testid="migration-board-title-input"
        />
      </label>
      <label className="formGroup">
        <span className="formLabel">Описание</span>
        <textarea
          className="formInput"
          value={payload.summary}
          onChange={(event) => update("summary", event.target.value)}
          minLength={30}
          maxLength={1200}
          rows={6}
          required
          data-testid="migration-board-summary-input"
        />
      </label>
      <div className="toolbar">
        <label className="formGroup">
          <span className="formLabel">Срок</span>
          <select
            className="formInput"
            value={payload.timeline_window}
            onChange={(event) => update("timeline_window", event.target.value)}
          >
            <option value="unknown">Пока не знаю</option>
            <option value="0_3_months">0-3 месяца</option>
            <option value="3_6_months">3-6 месяцев</option>
            <option value="6_12_months">6-12 месяцев</option>
            <option value="12_plus_months">12+ месяцев</option>
          </select>
        </label>
        <label className="formGroup">
          <span className="formLabel">Стадия</span>
          <select
            className="formInput"
            value={payload.migration_stage}
            onChange={(event) => update("migration_stage", event.target.value)}
          >
            <option value="researching">Изучаю</option>
            <option value="preparing_documents">Готовлю документы</option>
            <option value="applying">Подаюсь</option>
            <option value="waiting_decision">Жду решение</option>
            <option value="relocating_soon">Скоро переезжаю</option>
            <option value="already_relocated">Уже переехал</option>
            <option value="on_hold">На паузе</option>
          </select>
        </label>
        <label className="formGroup">
          <span className="formLabel">Цель</span>
          <select
            className="formInput"
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
        </label>
        <label className="formGroup">
          <span className="formLabel">Видимость</span>
          <select
            className="formInput"
            value={payload.visibility}
            onChange={(event) => update("visibility", event.target.value)}
          >
            <option value="members_only">Только участники</option>
            <option value="public">Публично</option>
            <option value="private">Приватно</option>
          </select>
        </label>
      </div>
      <label className="formGroup">
        <span className="formLabel">Теги через запятую</span>
        <input
          className="formInput"
          value={tagInput}
          onChange={(event) => setTagInput(event.target.value)}
          placeholder="housing, documents, remote_work"
        />
      </label>
      <label className="checkboxRow">
        <input
          type="checkbox"
          checked={payload.risk_acknowledged}
          onChange={(event) =>
            update("risk_acknowledged", event.target.checked)
          }
          data-testid="migration-board-risk-checkbox"
        />
        <span>Я понимаю риски переезда и публичной записи.</span>
      </label>
      <label className="checkboxRow">
        <input
          type="checkbox"
          checked={payload.legal_disclaimer_acknowledged}
          onChange={(event) =>
            update("legal_disclaimer_acknowledged", event.target.checked)
          }
          data-testid="migration-board-legal-checkbox"
        />
        <span>Я понимаю, что это не юридическая консультация.</span>
      </label>
      <label className="checkboxRow">
        <input
          type="checkbox"
          checked={payload.contact_requests_enabled}
          onChange={(event) =>
            update("contact_requests_enabled", event.target.checked)
          }
        />
        <span>Разрешить contact requests через платформу.</span>
      </label>
      <div className="toolbar">
        <button
          type="button"
          className="secondaryButton"
          disabled={isSaving}
          onClick={() => void save(false)}
          data-testid="migration-board-save-draft"
        >
          Сохранить черновик
        </button>
        <button
          type="button"
          className="runButton"
          disabled={isSaving}
          onClick={() => void save(true)}
          data-testid="migration-board-submit"
        >
          Отправить на модерацию
        </button>
      </div>
    </form>
  );
}
