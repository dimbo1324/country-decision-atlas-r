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

type RunError = { error?: { code?: string; message?: string } } | string | null;

function DecisionFormInner() {
  const searchParams = useSearchParams();
  const locale = normalizeLocale(searchParams.get("locale"));

  const [countries, setCountries] = useState<CountryListResponse | null>(null);
  const [scenarios, setScenarios] = useState<ScenarioListResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [originCountrySlug, setOriginCountrySlug] = useState("russia");
  const [candidateCountrySlugs, setCandidateCountrySlugs] = useState<string[]>(
    ["russia", "uruguay"],
  );
  const [scenarioSlug, setScenarioSlug] = useState("relocation_residence");

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
            err instanceof Error ? err.message : "Failed to load data",
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
        setRunError(err as { error?: { code?: string; message?: string } });
      }
    } finally {
      setIsRunning(false);
    }
  }

  if (loadError) return <ErrorState error={loadError} />;
  if (!countries || !scenarios) {
    return <LoadingState message="Loading countries and scenarios…" />;
  }

  return (
    <div className="decisionFormWrap">
      <div className="decisionForm">
        <div className="formGroup">
          <label className="formLabel" htmlFor="origin-select">
            Origin country
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
          <label className="formLabel">Candidate countries</label>
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
              Select at least one candidate country.
            </p>
          )}
        </div>

        <div className="formGroup">
          <label className="formLabel" htmlFor="scenario-select">
            Scenario
          </label>
          <select
            id="scenario-select"
            className="formSelect"
            value={scenarioSlug}
            onChange={(e) => setScenarioSlug(e.target.value)}
          >
            {scenarios.items.map((s) => (
              <option key={s.slug} value={s.slug}>
                {s.name}
              </option>
            ))}
          </select>
        </div>

        <button
          className="runButton"
          onClick={handleRun}
          disabled={isRunning || candidateCountrySlugs.length === 0}
          aria-busy={isRunning}
          data-testid="decision-run-button"
        >
          {isRunning ? "Running decision…" : "Run decision"}
        </button>
      </div>

      {isRunning && <LoadingState message="Running decision engine…" />}
      {!isRunning && runError !== null && <ErrorState error={runError} />}
      {!isRunning && runError === null && result === null && (
        <EmptyState message="Choose a scenario and run a decision to see the ranking." />
      )}
      {result !== null && <DecisionResults response={result} />}
    </div>
  );
}

export function DecisionRunForm() {
  return (
    <Suspense fallback={<LoadingState message="Loading decision form…" />}>
      <DecisionFormInner />
    </Suspense>
  );
}
