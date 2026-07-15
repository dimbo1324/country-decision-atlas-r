"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Button,
  Card,
  Field,
  FieldLabel,
  Kicker,
  toast,
} from "@country-decision-atlas/ui";
import {
  adminEvidenceApi,
  type EvidenceItemCreate,
  type LegalSignalCreate,
  type SourceCreate,
} from "../../shared/api/admin-evidence";
import { isApiError } from "../../shared/api/http";
import { ADMIN_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";
const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";

/** admin.py exposes only POST (create) and PATCH (by known id) for
 * sources/evidence-items/legal-signals -- no GET/list endpoint for any of
 * the three (confirmed against packages/contracts/generated/types.ts).
 * A browsable table isn't buildable against the real API, so this page
 * is create-only forms with the raw created-item response shown inline
 * for operator confirmation; patch-by-id was scoped out this pass too
 * (documented in task-checklist.md) to keep this page's surface honest
 * about what the backend actually supports. */
function SourceForm() {
  const create = useMutation({
    mutationFn: adminEvidenceApi.createAdminSource,
  });
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [countrySlug, setCountrySlug] = useState("");

  async function handleSubmit() {
    if (!title.trim()) return;
    const payload: SourceCreate = {
      title,
      url: url || null,
      country_slug: countrySlug || null,
      language: "ru",
      confidence: "medium",
      status: "draft",
    };
    try {
      await create.mutateAsync(payload);
      toast.success("Источник создан.");
      setTitle("");
      setUrl("");
      setCountrySlug("");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось создать источник.")
          : "Не удалось создать источник.",
      );
    }
  }

  return (
    <Card
      interactive={false}
      className="flex flex-col gap-4"
    >
      <Kicker>Новый источник</Kicker>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Field>
          <FieldLabel htmlFor="source-title">Название</FieldLabel>
          <input
            id="source-title"
            className={inputClass}
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            data-testid="admin-source-title-input"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="source-url">URL</FieldLabel>
          <input
            id="source-url"
            className={inputClass}
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            data-testid="admin-source-url-input"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="source-country">Страна (slug)</FieldLabel>
          <input
            id="source-country"
            className={inputClass}
            value={countrySlug}
            onChange={(event) => setCountrySlug(event.target.value)}
            data-testid="admin-source-country-input"
          />
        </Field>
      </div>
      <Button
        type="button"
        onClick={() => void handleSubmit()}
        disabled={create.isPending || !title.trim()}
        data-testid="admin-source-submit"
      >
        Создать
      </Button>
    </Card>
  );
}

function EvidenceForm() {
  const create = useMutation({
    mutationFn: adminEvidenceApi.createAdminEvidenceItem,
  });
  const [claim, setClaim] = useState("");
  const [countrySlug, setCountrySlug] = useState("");

  async function handleSubmit() {
    if (!claim.trim()) return;
    const payload: EvidenceItemCreate = {
      claim,
      country_slug: countrySlug || null,
      confidence: "medium",
      status: "draft",
    };
    try {
      await create.mutateAsync(payload);
      toast.success("Доказательство создано.");
      setClaim("");
      setCountrySlug("");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось создать доказательство.")
          : "Не удалось создать доказательство.",
      );
    }
  }

  return (
    <Card
      interactive={false}
      className="flex flex-col gap-4"
    >
      <Kicker>Новое доказательство</Kicker>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field>
          <FieldLabel htmlFor="evidence-claim">Утверждение</FieldLabel>
          <input
            id="evidence-claim"
            className={inputClass}
            value={claim}
            onChange={(event) => setClaim(event.target.value)}
            data-testid="admin-evidence-claim-input"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="evidence-country">Страна (slug)</FieldLabel>
          <input
            id="evidence-country"
            className={inputClass}
            value={countrySlug}
            onChange={(event) => setCountrySlug(event.target.value)}
            data-testid="admin-evidence-country-input"
          />
        </Field>
      </div>
      <Button
        type="button"
        onClick={() => void handleSubmit()}
        disabled={create.isPending || !claim.trim()}
        data-testid="admin-evidence-submit"
      >
        Создать
      </Button>
    </Card>
  );
}

function LegalSignalForm() {
  const create = useMutation({
    mutationFn: adminEvidenceApi.createAdminLegalSignal,
  });
  const [titleEn, setTitleEn] = useState("");
  const [countrySlug, setCountrySlug] = useState("");
  const [legalStatus, setLegalStatus] = useState("unknown");

  async function handleSubmit() {
    if (!titleEn.trim() || !countrySlug.trim()) return;
    const payload: LegalSignalCreate = {
      title_en: titleEn,
      country_slug: countrySlug,
      legal_status: legalStatus as LegalSignalCreate["legal_status"],
      confidence: "medium",
      status: "draft",
    };
    try {
      await create.mutateAsync(payload);
      toast.success("Правовой сигнал создан.");
      setTitleEn("");
      setCountrySlug("");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось создать сигнал.")
          : "Не удалось создать сигнал.",
      );
    }
  }

  return (
    <Card
      interactive={false}
      className="flex flex-col gap-4"
    >
      <Kicker>Новый правовой сигнал</Kicker>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Field>
          <FieldLabel htmlFor="signal-title">Заголовок (en)</FieldLabel>
          <input
            id="signal-title"
            className={inputClass}
            value={titleEn}
            onChange={(event) => setTitleEn(event.target.value)}
            data-testid="admin-legal-signal-title-input"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="signal-country">Страна (slug)</FieldLabel>
          <input
            id="signal-country"
            className={inputClass}
            value={countrySlug}
            onChange={(event) => setCountrySlug(event.target.value)}
            data-testid="admin-legal-signal-country-input"
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="signal-status">Правовой статус</FieldLabel>
          <select
            id="signal-status"
            className={selectClass}
            value={legalStatus}
            onChange={(event) => setLegalStatus(event.target.value)}
            data-testid="admin-legal-signal-status-select"
          >
            <option value="unknown">unknown</option>
            <option value="proposed">proposed</option>
            <option value="adopted">adopted</option>
            <option value="effective">effective</option>
            <option value="expired">expired</option>
            <option value="revoked">revoked</option>
          </select>
        </Field>
      </div>
      <Button
        type="button"
        onClick={() => void handleSubmit()}
        disabled={create.isPending || !titleEn.trim() || !countrySlug.trim()}
        data-testid="admin-legal-signal-submit"
      >
        Создать
      </Button>
    </Card>
  );
}

export function EvidenceAdminView() {
  const { status } = useAuthGuard(ADMIN_ROLES);

  if (status === "loading") {
    return <LoadingState message="Проверка прав…" />;
  }

  if (status !== "ok") {
    return (
      <ErrorState
        error="Недостаточно прав для управления источниками."
        backHref={routes.login}
        backLabel="Войти"
      />
    );
  }

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="admin-evidence-view"
    >
      <p className="text-c4 max-w-2xl text-xs leading-relaxed">
        У бэкенда нет GET/list для источников, доказательств и правовых сигналов
        — только создание и редактирование по известному id. Просматриваемого
        списка здесь поэтому нет: это осознанное ограничение возможностей, а не
        недоработка интерфейса.
      </p>
      <SourceForm />
      <EvidenceForm />
      <LegalSignalForm />
    </div>
  );
}
