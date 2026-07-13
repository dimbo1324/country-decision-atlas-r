import { getLocale } from "next-intl/server";
import { Badge, Card, Kicker } from "@country-decision-atlas/ui";
import { getPathname, Link } from "../../../../../i18n/navigation";
import { DecisionResults } from "../../../../../features/decision-run";
import { decisionPassportsApi } from "../../../../../shared/api";
import { ErrorState } from "../../../../../shared/ui/ErrorState";

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
        <header className="flex flex-col gap-3">
          <Kicker>Decision Passport</Kicker>
          <h1 className="font-display text-3xl font-bold">Decision Passport</h1>
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">
              Создан: {new Date(passport.generated_at).toLocaleString("ru")}
            </Badge>
            {passport.expires_at && (
              <Badge variant="default">
                Истекает: {new Date(passport.expires_at).toLocaleString("ru")}
              </Badge>
            )}
            <Badge variant="trust">{passport.status}</Badge>
          </div>
        </header>

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
