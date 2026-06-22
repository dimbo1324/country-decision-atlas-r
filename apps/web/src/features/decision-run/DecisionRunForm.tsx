"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import type { CountryListResponse } from "../../shared/api/countries";
import type { ScenarioListResponse } from "../../shared/api/scenarios";
import type { DecisionRunResponse } from "../../shared/api/decision";
import { countriesApi, scenariosApi, decisionApi } from "../../shared/api";
import { normalizeLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { DecisionResults } from "./DecisionResults";
import {
  DEFAULT_DECISION_READY_SCENARIO_SLUG,
  isDecisionReadyScenario,
} from "./decision-ready-scenarios";
import { DecisionCiiComparison } from "../decision-visual-comparison";

type RunError = { error?: { code?: string; message?: string } } | string | null;

function DecisionFormInner() {
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));

  const [countries, setCountries] = useState<CountryListResponse | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioListResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [originCountrySlug, setOriginCountrySlug] = useState("russia");
  const [candidateCountrySlugs, setCandidateCountrySlugs] = useState<string[]>([
    "russia",
    "uruguay",
  ]);
  const [scenarioSlug, setScenarioSlug] = useState<string>(
    DEFAULT_DECISION_READY_SCENARIO_SLUG,
  );

  const [result, setResult] = useState<DecisionRunResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [runError, setRunError] = useState<RunError>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadError(null);

    Promise.all([
      countriesApi.listCountries({ locale }),
      scenariosApi.listScenarios({ locale }),
    ])
      .then(([c, s]) => {
        if (!cancelled) {
          setCountries(c);
          setScenarios(s);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setLoadError(
            err instanceof Error ? err.message : "Не удалось загрузить данные",
          );
        }
      });

    return () => {
      cancelled = true;
    };
  }, [locale]);

  function toggleCandidate(slug: string) {
    setCandidateCountrySlugs((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug],
    );
  }

  async function handleRun() {
    if (candidateCountrySlugs.length === 0) return;
    setIsRunning(true);
    setRunError(null);
    setResult(null);
    try {
      const res = await decisionApi.runDecision({
        origin_country_slug: originCountrySlug,
        candidate_country_slugs: candidateCountrySlugs,
        scenario_slug: scenarioSlug,
        locale,
      });
      setResult(res);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setRunError(err.message);
      } else {
        setRunError(
          typeof err === "object" && err !== null && "error" in err
            ? (err as { error?: { code?: string; message?: string } })
            : "Произошла ошибка при запросе",
        );
      }
    } finally {
      setIsRunning(false);
    }
  }

  if (loadError) return <ErrorState error={loadError} />;
  if (!countries || !scenarios) {
    return <LoadingState message="Загрузка стран и сценариев…" />;
  }

  const decisionReadyScenarios = scenarios.items.filter((s) =>
    isDecisionReadyScenario(s.slug),
  );

  const noScenariosAvailable = decisionReadyScenarios.length === 0;

  const resolvedRunError =
    runError !== null &&
    typeof runError === "object" &&
    (runError as { error?: { code?: string } }).error?.code ===
      "decision_score_not_found"
      ? "Этот сценарий пока недоступен для выбранных стран. Пожалуйста, выберите один из MVP-сценариев подбора."
      : runError;

  return (
    <div className="decisionLayout">
      <div className="decisionForm">
        <div className="formGroup">
          <label className="formLabel" htmlFor="origin-select">
            Страна отправления
          </label>
          <select
            id="origin-select"
            className="formSelect"
            value={originCountrySlug}
            onChange={(e) => setOriginCountrySlug(e.target.value)}
          >
            {countries.items.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="formGroup">
          <label className="formLabel">Страны-кандидаты</label>
          <div className="checkboxList">
            {countries.items.map((c) => (
              <label key={c.slug} className="checkboxLabel">
                <input
                  type="checkbox"
                  checked={candidateCountrySlugs.includes(c.slug)}
                  onChange={() => toggleCandidate(c.slug)}
                />
                {c.name}
              </label>
            ))}
          </div>
          {candidateCountrySlugs.length === 0 && (
            <p className="formError" role="alert">
              Выберите хотя бы одну страну-кандидат.
            </p>
          )}
        </div>

        <div className="formGroup">
          <label className="formLabel" htmlFor="scenario-select">
            Сценарий
          </label>
          {noScenariosAvailable ? (
            <p className="formError" role="alert">
              Готовые сценарии подбора пока отсутствуют.
            </p>
          ) : (
            <select
              id="scenario-select"
              className="formSelect"
              value={scenarioSlug}
              onChange={(e) => setScenarioSlug(e.target.value)}
              data-testid="decision-scenario-select"
            >
              {decisionReadyScenarios.map((s) => (
                <option key={s.slug} value={s.slug}>
                  {s.name}
                </option>
              ))}
            </select>
          )}
        </div>

        <button
          className="runButton"
          onClick={handleRun}
          disabled={
            isRunning || candidateCountrySlugs.length === 0 || noScenariosAvailable
          }
          aria-busy={isRunning}
          data-testid="decision-run-button"
        >
          {isRunning ? "Выполняется подбор…" : "Запустить подбор"}
        </button>
      </div>

      <div>
        {isRunning && <LoadingState message="Выполняется движок подбора…" />}
        {!isRunning && resolvedRunError !== null && (
          <ErrorState error={resolvedRunError} />
        )}
        {!isRunning && resolvedRunError === null && result === null && (
          <EmptyState message="Выберите сценарий и запустите подбор, чтобы увидеть рейтинг." />
        )}
        {result !== null && <DecisionResults response={result} />}
        {result !== null && candidateCountrySlugs.length === 2 && (
          <DecisionCiiComparison
            countrySlugs={candidateCountrySlugs}
            scenarioSlug={scenarioSlug}
            locale={locale}
          />
        )}
      </div>
    </div>
  );
}

export function DecisionRunForm() {
  return (
    <Suspense fallback={<LoadingState message="Загрузка формы подбора…" />}>
      <DecisionFormInner />
    </Suspense>
  );
}
