import { getLocale } from "next-intl/server";
import { ShieldCheck } from "lucide-react";
import { Badge, Card, Kicker } from "@country-decision-atlas/ui";
import { getPathname, Link } from "../../../../../i18n/navigation";
import { CreateTripFromPassportButton } from "../../../../../features/decision-passports";
import { DecisionResults } from "../../../../../features/decision-run";
import { decisionPassportsApi } from "../../../../../shared/api";
import { routes } from "../../../../../shared/lib/routes";
import { AppBreadcrumbs } from "../../../../../shared/ui/AppBreadcrumbs";
import { ErrorState } from "../../../../../shared/ui/ErrorState";
import { formatDateTime } from "../../../../../shared/lib/format";

export const dynamic = "force-dynamic";

type PageProps = {
  params: Promise<{ token: string }>;
};

export default async function DecisionPassportPage({ params }: PageProps) {
  const { token } = await params;
  const locale = await getLocale();

  try {
    const passport = await decisionPassportsApi.getDecisionPassport(token);
    return (
      <div
        className="flex flex-col gap-6"
        data-testid="decision-passport-page"
      >
        <AppBreadcrumbs
          items={[
            { label: "Подбор", href: routes.decision },
            { label: "Паспорт решения" },
          ]}
        />
        {/* Decorative document fragments ported from
            packages/ui/src/charts/PassportCard.tsx (the web-prototype's
            mockup component) -- the perforated edge and stamp seal only,
            not the component itself and not its live recompute toggles.
            This page stays a plain server-rendered, immutable snapshot;
            methodology_snapshot/status/generated_at below are exactly
            what the API returned, never recalculated client-side. */}
        <div className="border-warm bg-bg2 relative flex flex-col border">
          <div
            aria-hidden
            className="border-warm h-[3px] w-full border-b"
            style={{
              backgroundImage:
                "repeating-linear-gradient(90deg, transparent 0 7px, rgb(239 230 212 / 0.14) 7px 10px)",
            }}
          />
          <div className="flex items-start justify-between gap-4 p-6 pb-4">
            <header className="flex flex-col gap-3">
              <Kicker>Decision Passport</Kicker>
              <h1 className="font-display text-3xl font-bold">
                Decision Passport
              </h1>
              <div className="flex flex-wrap items-center gap-3">
                <span className="font-mono text-c4 text-[9px] tracking-[0.25em] uppercase">
                  REF · {passport.id.slice(0, 8)}
                </span>
                <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
                  Создан: {formatDateTime(passport.generated_at)}
                </span>
                {passport.expires_at && (
                  <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
                    Истекает: {formatDateTime(passport.expires_at)}
                  </span>
                )}
                <Badge variant="trust">{passport.status}</Badge>
              </div>
            </header>
            <span
              aria-hidden
              className="border-gold2/70 text-gold flex h-14 w-14 shrink-0 rotate-6 items-center justify-center rounded-full border-2 border-dashed"
            >
              <ShieldCheck
                width={22}
                height={22}
                strokeWidth={1.5}
              />
            </span>
          </div>
        </div>

        <div data-testid="passport-trip-cta">
          <CreateTripFromPassportButton token={token} />
        </div>

        <DecisionResults response={passport.decision_result} />

        <section data-testid="passport-methodology">
          <Card
            interactive={false}
            className="flex flex-col gap-3"
          >
            <h2 className="font-display text-lg font-semibold">Методология</h2>
            <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <dt className="font-mono text-c4 text-[9px] tracking-[0.15em] uppercase">
                  Версия движка
                </dt>
                <dd className="text-c2 text-sm">
                  {passport.methodology_snapshot.decision_engine_version}
                </dd>
              </div>
              <div>
                <dt className="font-mono text-c4 text-[9px] tracking-[0.15em] uppercase">
                  Сценарий
                </dt>
                <dd className="text-c2 text-sm">
                  {passport.methodology_snapshot.scenario_slug}
                </dd>
              </div>
              {passport.methodology_snapshot.persona_slug && (
                <div>
                  <dt className="font-mono text-c4 text-[9px] tracking-[0.15em] uppercase">
                    Персона
                  </dt>
                  <dd className="text-c2 text-sm">
                    {passport.methodology_snapshot.persona_slug}
                  </dd>
                </div>
              )}
              {passport.methodology_snapshot.origin_country_slug && (
                <div>
                  <dt className="font-mono text-c4 text-[9px] tracking-[0.15em] uppercase">
                    Страна отправления
                  </dt>
                  <dd className="text-c2 text-sm">
                    {passport.methodology_snapshot.origin_country_slug}
                  </dd>
                </div>
              )}
              <div>
                <dt className="font-mono text-c4 text-[9px] tracking-[0.15em] uppercase">
                  Кастомные веса
                </dt>
                <dd className="text-c2 text-sm">
                  {passport.methodology_snapshot.custom_weights_applied
                    ? "Да"
                    : "Нет"}
                </dd>
              </div>
              <div>
                <dt className="font-mono text-c4 text-[9px] tracking-[0.15em] uppercase">
                  Режим ранжирования
                </dt>
                <dd className="text-c2 text-sm">
                  {passport.methodology_snapshot.ranking_policy}
                </dd>
              </div>
            </dl>
          </Card>
        </section>
      </div>
    );
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="flex flex-col gap-6">
        <header className="flex flex-col gap-3">
          <Kicker>Decision Passport</Kicker>
          <h1 className="font-display text-3xl font-bold">
            Decision Passport недоступен
          </h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={getPathname({ href: "/decision", locale })}
          backLabel="Назад к подбору"
        />
        <Link
          href="/decision"
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          Запустить новый подбор
        </Link>
      </div>
    );
  }
}
