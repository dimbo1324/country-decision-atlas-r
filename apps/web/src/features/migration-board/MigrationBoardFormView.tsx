"use client";

import { useTranslations } from "next-intl";
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
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { migrationBoardErrorMessage } from "./errorMessage";
import {
  GOAL_LABELS,
  STAGE_LABELS,
  TIMELINE_LABELS,
  VISIBILITY_LABELS,
} from "./migration-board-labels";

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
  const t = useTranslations("migrationBoardForm");
  const { user, isLoading } = useAuth();
  const locale = useAppLocale();
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
    return <LoadingState message={t("loadingAccess")} />;
  }

  if (!user) {
    return (
      <ErrorState
        error={t("loginRequired")}
        backHref={getPathname({ href: routes.login, locale })}
        backLabel={t("loginLabel")}
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
            locale,
          )}
        />
      )}

      <Card
        interactive={false}
        className="flex flex-col gap-5"
      >
        <Field>
          <FieldLabel htmlFor="board-destination">
            {t("destinationLabel")}
          </FieldLabel>
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
          <FieldLabel htmlFor="board-origin">{t("originLabel")}</FieldLabel>
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
          <FieldLabel htmlFor="board-route-id">{t("routeIdLabel")}</FieldLabel>
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
            <FieldLabel htmlFor="board-scenario">
              {t("scenarioLabel")}
            </FieldLabel>
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
            <FieldLabel htmlFor="board-persona">{t("personaLabel")}</FieldLabel>
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
          <FieldLabel htmlFor="board-title">{t("titleLabel")}</FieldLabel>
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
          <FieldLabel htmlFor="board-summary">{t("summaryLabel")}</FieldLabel>
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
          <FieldHint>{t("summaryHint")}</FieldHint>
        </Field>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Field>
            <FieldLabel htmlFor="board-timeline">
              {t("timelineLabel")}
            </FieldLabel>
            <select
              id="board-timeline"
              className={selectClass}
              value={payload.timeline_window}
              onChange={(event) =>
                update("timeline_window", event.target.value)
              }
            >
              {Object.entries(TIMELINE_LABELS[locale])
                .filter(([value]) => value !== "")
                .map(([value, label]) => (
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
            <FieldLabel htmlFor="board-stage">{t("stageLabel")}</FieldLabel>
            <select
              id="board-stage"
              className={selectClass}
              value={payload.migration_stage}
              onChange={(event) =>
                update("migration_stage", event.target.value)
              }
            >
              {Object.entries(STAGE_LABELS[locale]).map(([value, label]) => (
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
            <FieldLabel htmlFor="board-goal">{t("goalLabel")}</FieldLabel>
            <select
              id="board-goal"
              className={selectClass}
              value={payload.companion_goal}
              onChange={(event) => update("companion_goal", event.target.value)}
            >
              {Object.entries(GOAL_LABELS[locale])
                .filter(([value]) => value !== "")
                .map(([value, label]) => (
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
            <FieldLabel htmlFor="board-visibility">
              {t("visibilityLabel")}
            </FieldLabel>
            <select
              id="board-visibility"
              className={selectClass}
              value={payload.visibility}
              onChange={(event) => update("visibility", event.target.value)}
            >
              {Object.entries(VISIBILITY_LABELS[locale]).map(
                ([value, label]) => (
                  <option
                    key={value}
                    value={value}
                  >
                    {label}
                  </option>
                ),
              )}
            </select>
          </Field>
        </div>
        <Field>
          <FieldLabel htmlFor="board-tags">{t("tagsLabel")}</FieldLabel>
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
          {t("riskLabel")}
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
          {t("legalLabel")}
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
          {t("contactRequestsLabel")}
        </label>
        <div className="flex gap-3">
          <Button
            type="button"
            variant="ghost"
            disabled={isSaving}
            onClick={() => void save(false)}
            data-testid="migration-board-save-draft"
          >
            {t("saveDraft")}
          </Button>
          <Button
            type="button"
            disabled={isSaving}
            onClick={() => void save(true)}
            data-testid="migration-board-submit"
          >
            {t("submitForModeration")}
          </Button>
        </div>
      </Card>
    </form>
  );
}
