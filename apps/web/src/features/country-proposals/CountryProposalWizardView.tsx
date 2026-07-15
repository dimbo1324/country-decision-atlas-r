"use client";

import { useState } from "react";
import { Check } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import {
  Badge,
  Button,
  Card,
  DossierRail,
  Field,
  FieldLabel,
  Kicker,
  ProgressRing,
  toast,
} from "@country-decision-atlas/ui";
import {
  myCountryProposalQuery,
  useCreateCountryProposalEvidenceItemMutation,
  useCreateCountryProposalLegalSignalMutation,
  useCreateCountryProposalSourceMutation,
  useCreateCountryProposalTimelineEventMutation,
  useSubmitCountryProposalMutation,
  useUpsertCountryProposalCardMutation,
  useUpsertCountryProposalMetricValuesMutation,
} from "../../entities/country-proposals/api";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { Link } from "../../i18n/navigation";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";
const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";

const SECTIONS = [
  { id: "proposal-section-sources", label: "Источники" },
  { id: "proposal-section-evidence", label: "Доказательства" },
  { id: "proposal-section-signals", label: "Правовые сигналы" },
  { id: "proposal-section-timeline", label: "Таймлайн" },
  { id: "proposal-section-metrics", label: "Метрики" },
  { id: "proposal-section-card", label: "Карточка страны" },
  { id: "proposal-section-submit", label: "Отправка" },
];

/** Every section below only has a create endpoint on the backend -- there is
 * no GET/list for country-proposal sources, evidence items, legal signals,
 * timeline events, or metric values (confirmed against
 * packages/contracts/generated/types.ts: only POST/PATCH exist, no GET).
 * Rows added persist server-side but can't be re-read by this page, so each
 * section tracks "added this session" locally for feedback only -- a
 * reload loses that local list even though the data itself is safe. This
 * is a real backend gap, not a frontend shortcut; documented here and in
 * the Stage 10 task-checklist. */
function SessionAddedList({ items }: { items: string[] }) {
  if (items.length === 0) return null;
  return (
    <ul className="text-c3 flex flex-col gap-1 text-sm">
      {items.map((item, index) => (
        <li
          key={index}
          className="flex items-start gap-2"
        >
          <Check
            width={12}
            height={12}
            strokeWidth={1.5}
            aria-hidden
            className="text-sage mt-1 shrink-0"
          />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function SourcesSection({ proposalId }: { proposalId: string }) {
  const createSource = useCreateCountryProposalSourceMutation(proposalId);
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [added, setAdded] = useState<string[]>([]);

  async function handleAdd() {
    if (!title.trim()) return;
    try {
      await createSource.mutateAsync({
        title,
        url: url || null,
        confidence: "medium",
        language: "en",
      });
      setAdded((current) => [...current, title]);
      setTitle("");
      setUrl("");
      toast.success("Источник добавлен.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось добавить источник.")
          : "Не удалось добавить источник.",
      );
    }
  }

  return (
    <div id="proposal-section-sources">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Источники</Kicker>
        <SessionAddedList items={added} />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[2fr_2fr_auto] sm:items-end">
          <Field>
            <FieldLabel htmlFor="source-title">Название</FieldLabel>
            <input
              id="source-title"
              className={inputClass}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              data-testid="proposal-source-title-input"
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="source-url">URL</FieldLabel>
            <input
              id="source-url"
              className={inputClass}
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              data-testid="proposal-source-url-input"
            />
          </Field>
          <Button
            onClick={() => void handleAdd()}
            disabled={createSource.isPending || !title.trim()}
            data-testid="proposal-source-add"
          >
            Добавить
          </Button>
        </div>
      </Card>
    </div>
  );
}

function EvidenceSection({ proposalId }: { proposalId: string }) {
  const createEvidence =
    useCreateCountryProposalEvidenceItemMutation(proposalId);
  const [claim, setClaim] = useState("");
  const [added, setAdded] = useState<string[]>([]);

  async function handleAdd() {
    if (!claim.trim()) return;
    try {
      await createEvidence.mutateAsync({ claim, confidence: "medium" });
      setAdded((current) => [...current, claim]);
      setClaim("");
      toast.success("Доказательство добавлено.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось добавить доказательство.")
          : "Не удалось добавить доказательство.",
      );
    }
  }

  return (
    <div id="proposal-section-evidence">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Доказательства</Kicker>
        <SessionAddedList items={added} />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[3fr_auto] sm:items-end">
          <Field>
            <FieldLabel htmlFor="evidence-claim">Утверждение</FieldLabel>
            <input
              id="evidence-claim"
              className={inputClass}
              value={claim}
              onChange={(event) => setClaim(event.target.value)}
              data-testid="proposal-evidence-claim-input"
            />
          </Field>
          <Button
            onClick={() => void handleAdd()}
            disabled={createEvidence.isPending || !claim.trim()}
            data-testid="proposal-evidence-add"
          >
            Добавить
          </Button>
        </div>
      </Card>
    </div>
  );
}

function LegalSignalsSection({ proposalId }: { proposalId: string }) {
  const createSignal = useCreateCountryProposalLegalSignalMutation(proposalId);
  const [titleEn, setTitleEn] = useState("");
  const [added, setAdded] = useState<string[]>([]);

  async function handleAdd() {
    if (!titleEn.trim()) return;
    try {
      await createSignal.mutateAsync({
        title_en: titleEn,
        legal_status: "unknown",
        confidence: "medium",
      });
      setAdded((current) => [...current, titleEn]);
      setTitleEn("");
      toast.success("Правовой сигнал добавлен.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось добавить сигнал.")
          : "Не удалось добавить сигнал.",
      );
    }
  }

  return (
    <div id="proposal-section-signals">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Правовые сигналы</Kicker>
        <SessionAddedList items={added} />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[3fr_auto] sm:items-end">
          <Field>
            <FieldLabel htmlFor="signal-title">Заголовок (en)</FieldLabel>
            <input
              id="signal-title"
              className={inputClass}
              value={titleEn}
              onChange={(event) => setTitleEn(event.target.value)}
              data-testid="proposal-signal-title-input"
            />
          </Field>
          <Button
            onClick={() => void handleAdd()}
            disabled={createSignal.isPending || !titleEn.trim()}
            data-testid="proposal-signal-add"
          >
            Добавить
          </Button>
        </div>
      </Card>
    </div>
  );
}

function TimelineSection({ proposalId }: { proposalId: string }) {
  const createEvent = useCreateCountryProposalTimelineEventMutation(proposalId);
  const [legalSignalId, setLegalSignalId] = useState("");
  const [eventDate, setEventDate] = useState("");
  const [title, setTitle] = useState("");
  const [added, setAdded] = useState<string[]>([]);

  async function handleAdd() {
    if (!legalSignalId.trim() || !eventDate || !title.trim()) return;
    try {
      await createEvent.mutateAsync({
        legal_signal_id: legalSignalId,
        event_date: eventDate,
        event_type: "update",
        impact_direction: "neutral",
        impact_level: "low",
        title,
      });
      setAdded((current) => [...current, title]);
      setTitle("");
      toast.success("Событие таймлайна добавлено.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось добавить событие.")
          : "Не удалось добавить событие.",
      );
    }
  }

  return (
    <div id="proposal-section-timeline">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Таймлайн</Kicker>
        <p className="text-c4 text-xs">
          Требует ID уже добавленного правового сигнала (виден в ответе сервера
          после добавления).
        </p>
        <SessionAddedList items={added} />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_1fr_2fr_auto] sm:items-end">
          <Field>
            <FieldLabel htmlFor="timeline-signal-id">
              ID правового сигнала
            </FieldLabel>
            <input
              id="timeline-signal-id"
              className={inputClass}
              value={legalSignalId}
              onChange={(event) => setLegalSignalId(event.target.value)}
              data-testid="proposal-timeline-signal-id-input"
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="timeline-date">Дата события</FieldLabel>
            <input
              id="timeline-date"
              type="date"
              className={inputClass}
              value={eventDate}
              onChange={(event) => setEventDate(event.target.value)}
              data-testid="proposal-timeline-date-input"
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="timeline-title">Заголовок</FieldLabel>
            <input
              id="timeline-title"
              className={inputClass}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              data-testid="proposal-timeline-title-input"
            />
          </Field>
          <Button
            onClick={() => void handleAdd()}
            disabled={
              createEvent.isPending ||
              !legalSignalId.trim() ||
              !eventDate ||
              !title.trim()
            }
            data-testid="proposal-timeline-add"
          >
            Добавить
          </Button>
        </div>
      </Card>
    </div>
  );
}

function MetricsSection({ proposalId }: { proposalId: string }) {
  const upsertValues = useUpsertCountryProposalMetricValuesMutation(proposalId);
  const [metricSlug, setMetricSlug] = useState("");
  const [rawValue, setRawValue] = useState("");
  const [added, setAdded] = useState<string[]>([]);

  async function handleAdd() {
    const raw = Number(rawValue);
    if (!metricSlug.trim() || Number.isNaN(raw)) return;
    try {
      await upsertValues.mutateAsync([
        {
          metric_slug: metricSlug,
          raw_value: raw,
          normalized_value: raw,
          reliability: "medium",
        },
      ]);
      setAdded((current) => [...current, `${metricSlug}: ${raw}`]);
      setMetricSlug("");
      setRawValue("");
      toast.success("Значение метрики сохранено.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось сохранить значение.")
          : "Не удалось сохранить значение.",
      );
    }
  }

  return (
    <div id="proposal-section-metrics">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Метрики</Kicker>
        <SessionAddedList items={added} />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[2fr_1fr_auto] sm:items-end">
          <Field>
            <FieldLabel htmlFor="metric-slug">Slug метрики</FieldLabel>
            <input
              id="metric-slug"
              className={inputClass}
              value={metricSlug}
              onChange={(event) => setMetricSlug(event.target.value)}
              data-testid="proposal-metric-slug-input"
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="metric-value">Значение</FieldLabel>
            <input
              id="metric-value"
              type="number"
              className={inputClass}
              value={rawValue}
              onChange={(event) => setRawValue(event.target.value)}
              data-testid="proposal-metric-value-input"
            />
          </Field>
          <Button
            onClick={() => void handleAdd()}
            disabled={upsertValues.isPending || !metricSlug.trim() || !rawValue}
            data-testid="proposal-metric-add"
          >
            Сохранить
          </Button>
        </div>
      </Card>
    </div>
  );
}

function CardSection({ proposalId }: { proposalId: string }) {
  const upsertCard = useUpsertCountryProposalCardMutation(proposalId);
  const [locale, setLocale] = useState<"ru" | "en">("ru");
  const [executiveSummary, setExecutiveSummary] = useState("");

  async function handleSave() {
    if (!executiveSummary.trim()) return;
    try {
      await upsertCard.mutateAsync({
        locale,
        payload: {
          executive_summary: executiveSummary,
          migration_overview: "",
          tax_overview: "",
          cost_of_living_overview: "",
          business_overview: "",
          safety_overview: "",
          legal_signals_summary: "",
          risk_summary: "",
          source_summary: "",
        },
      });
      toast.success("Карточка страны сохранена.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось сохранить карточку.")
          : "Не удалось сохранить карточку.",
      );
    }
  }

  return (
    <div id="proposal-section-card">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Карточка страны (превью локали)</Kicker>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_3fr]">
          <Field>
            <FieldLabel htmlFor="card-locale">Локаль</FieldLabel>
            <select
              id="card-locale"
              className={selectClass}
              value={locale}
              onChange={(event) => setLocale(event.target.value as "ru" | "en")}
              data-testid="proposal-card-locale-select"
            >
              <option value="ru">ru</option>
              <option value="en">en</option>
            </select>
          </Field>
          <Field>
            <FieldLabel htmlFor="card-summary">Executive summary</FieldLabel>
            <textarea
              id="card-summary"
              className={inputClass}
              rows={3}
              value={executiveSummary}
              onChange={(event) => setExecutiveSummary(event.target.value)}
              data-testid="proposal-card-summary-input"
            />
          </Field>
        </div>
        <Button
          onClick={() => void handleSave()}
          disabled={upsertCard.isPending || !executiveSummary.trim()}
          data-testid="proposal-card-save"
        >
          Сохранить карточку
        </Button>
      </Card>
    </div>
  );
}

function SubmitSection({
  proposalId,
  status,
}: {
  proposalId: string;
  status: string;
}) {
  const submitProposal = useSubmitCountryProposalMutation(proposalId);

  return (
    <div id="proposal-section-submit">
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Отправка на модерацию</Kicker>
        <Badge variant="default">Текущий статус: {status}</Badge>
        <Button
          onClick={() => submitProposal.mutate()}
          disabled={status !== "draft" || submitProposal.isPending}
          data-testid="proposal-submit"
        >
          Отправить на модерацию
        </Button>
      </Card>
    </div>
  );
}

export function CountryProposalWizardView({
  proposalId,
}: {
  proposalId: string;
}) {
  const { user, isLoading: authLoading } = useAuth();
  const proposal = useQuery({
    ...myCountryProposalQuery(proposalId),
    enabled: Boolean(user),
  });

  if (authLoading) {
    return <LoadingState message="Загрузка…" />;
  }

  if (!user) {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="country-proposal-wizard-unauthenticated"
      >
        <p className="text-c3 text-sm">
          Войдите, чтобы редактировать заявку.{" "}
          <Link
            href={routes.login}
            className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
          >
            Войти
          </Link>
        </p>
      </div>
    );
  }

  if (proposal.isPending) {
    return <LoadingState message="Загрузка заявки…" />;
  }

  if (proposal.isError) {
    return (
      <ErrorState
        error={isApiError(proposal.error) ? proposal.error : undefined}
      />
    );
  }

  const item = proposal.data.item;

  return (
    <div
      className="grid grid-cols-1 gap-8 lg:grid-cols-[200px_1fr]"
      data-testid="country-proposal-wizard"
    >
      <div className="hidden lg:block">
        <DossierRail
          sections={SECTIONS}
          className="sticky top-24"
        />
        <div className="mt-6">
          <ProgressRing
            value={0}
            label="Готовность"
            active
            size={120}
          />
        </div>
      </div>

      <div className="flex flex-col gap-6">
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-display text-2xl font-bold">
            {item.name_ru}
          </span>
          <Badge variant="default">{item.slug}</Badge>
        </div>

        <SourcesSection proposalId={proposalId} />
        <EvidenceSection proposalId={proposalId} />
        <LegalSignalsSection proposalId={proposalId} />
        <TimelineSection proposalId={proposalId} />
        <MetricsSection proposalId={proposalId} />
        <CardSection proposalId={proposalId} />
        <SubmitSection
          proposalId={proposalId}
          status={item.status}
        />
      </div>
    </div>
  );
}
