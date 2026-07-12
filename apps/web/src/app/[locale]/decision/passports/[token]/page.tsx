import { getLocale } from "next-intl/server";
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
        className="pageShell"
        data-testid="decision-passport-page"
      >
        <header className="pageHeader">
          <p className="eyebrow">Decision Passport</p>
          <h1>Decision Passport</h1>
          <div className="routeBadges">
            <span className="metaChip">
              Создан: {new Date(passport.generated_at).toLocaleString("ru")}
            </span>
            {passport.expires_at && (
              <span className="metaChip">
                Истекает: {new Date(passport.expires_at).toLocaleString("ru")}
              </span>
            )}
            <span className="metaChip">{passport.status}</span>
          </div>
        </header>

        <DecisionResults response={passport.decision_result} />

        <section
          className="cardSection"
          data-testid="passport-methodology"
        >
          <h2 className="cardSectionTitle">Методология</h2>
          <dl className="routeFacts">
            <div>
              <dt>Версия движка</dt>
              <dd>{passport.methodology_snapshot.decision_engine_version}</dd>
            </div>
            <div>
              <dt>Сценарий</dt>
              <dd>{passport.methodology_snapshot.scenario_slug}</dd>
            </div>
            {passport.methodology_snapshot.persona_slug && (
              <div>
                <dt>Персона</dt>
                <dd>{passport.methodology_snapshot.persona_slug}</dd>
              </div>
            )}
            {passport.methodology_snapshot.origin_country_slug && (
              <div>
                <dt>Страна отправления</dt>
                <dd>{passport.methodology_snapshot.origin_country_slug}</dd>
              </div>
            )}
            <div>
              <dt>Кастомные веса</dt>
              <dd>
                {passport.methodology_snapshot.custom_weights_applied
                  ? "Да"
                  : "Нет"}
              </dd>
            </div>
            <div>
              <dt>Режим ранжирования</dt>
              <dd>{passport.methodology_snapshot.ranking_policy}</dd>
            </div>
          </dl>
        </section>
      </div>
    );
  } catch (err: unknown) {
    const errProp =
      err instanceof Error
        ? err.message
        : (err as { error?: { code?: string; message?: string } });
    return (
      <div className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Decision Passport</p>
          <h1>Decision Passport недоступен</h1>
        </header>
        <ErrorState
          error={errProp}
          backHref={getPathname({ href: "/decision", locale })}
          backLabel="Назад к подбору"
        />
        <Link
          href="/decision"
          className="internalLink"
        >
          Запустить новый подбор
        </Link>
      </div>
    );
  }
}
