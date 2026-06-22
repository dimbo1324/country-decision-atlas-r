from app.repositories.cii import (
    get_active_cii_metric_definitions,
    get_cii_for_countries,
    get_cii_metric_values_for_countries,
    get_scenario_for_cii_comparison,
    get_scenario_metric_weights,
)
from app.schemas.cii_comparison import (
    CiiCountryComparisonResponse,
    ComparedCountry,
    ComparedMetric,
    ComparedMetricValue,
    ComparedScenario,
)
from app.schemas.common import LocaleResolution, TranslationStatus, locale_resolution
from psycopg import Connection
from typing import Any


def build_cii_comparison(
    connection: Connection[Any],
    country_slugs: list[str],
    scenario_slug: str,
    locale: str,
) -> CiiCountryComparisonResponse:
    scenario_row = get_scenario_for_cii_comparison(connection, scenario_slug, locale)
    scenario = ComparedScenario(
        slug=scenario_slug,
        title=scenario_row["title"] if scenario_row else scenario_slug,
    )

    scenario_weights_rows = get_scenario_metric_weights(connection, scenario_slug)
    weights_by_metric: dict[str, float] = {
        row["metric_slug"]: float(row["weight"]) for row in scenario_weights_rows
    }
    weights_version = "v1.0" if weights_by_metric else None

    cii_rows = get_cii_for_countries(
        connection, country_slugs, scenario_slug=scenario_slug
    )
    cii_by_slug = {row["country_slug"]: row for row in cii_rows}

    quality_warnings: list[str] = []
    countries: list[ComparedCountry] = []
    for slug in country_slugs:
        row = cii_by_slug.get(slug)
        if row is None:
            quality_warnings.append(f"country '{slug}' not found")
            countries.append(ComparedCountry(slug=slug, name=slug))
            continue
        if row.get("cii_score") is None:
            quality_warnings.append(
                f"country '{slug}' has no CII data for scenario '{scenario_slug}'"
            )
        countries.append(
            ComparedCountry(
                slug=slug,
                name=row["country_name"],
                iso2=row.get("iso2"),
                cii_score=row.get("cii_score"),
                cii_confidence=row.get("cii_confidence"),
                country_drift=row.get("country_drift"),
            )
        )

    metric_defs = get_active_cii_metric_definitions(connection)
    raw_values = get_cii_metric_values_for_countries(connection, country_slugs)

    values_by_metric_by_country: dict[str, dict[str, dict[str, Any]]] = {}
    for row in raw_values:
        metric_slug = row["metric_slug"]
        c_slug = row["country_slug"]
        values_by_metric_by_country.setdefault(metric_slug, {})[c_slug] = row

    formula_version: str | None = None
    aggregation_method: str | None = None
    for slug in country_slugs:
        row = cii_by_slug.get(slug)
        if row:
            formula_version = formula_version or row.get("formula_version")
            aggregation_method = aggregation_method or row.get("aggregation_method")

    metrics: list[ComparedMetric] = []
    for md in metric_defs:
        metric_slug = md["slug"]
        higher_is_better = md["polarity"] != "negative"
        metric_name = md["name_ru"] if locale == "ru" else md["name_en"]
        metric_weight = weights_by_metric.get(metric_slug)

        metric_values: list[ComparedMetricValue] = []
        effective_values: dict[str, float] = {}
        for slug in country_slugs:
            country_vals = values_by_metric_by_country.get(metric_slug, {})
            val_row = country_vals.get(slug)
            mv_warnings: list[str] = []
            if val_row is None:
                mv_warnings.append(f"no value for metric '{metric_slug}'")
                quality_warnings.append(
                    f"country '{slug}' missing metric '{metric_slug}'"
                )
                metric_values.append(
                    ComparedMetricValue(
                        country_slug=slug,
                        value=None,
                        effective_value=None,
                        quality_warnings=mv_warnings,
                    )
                )
            else:
                raw_v = float(val_row["value"])
                eff_v = raw_v if higher_is_better else 100.0 - raw_v
                effective_values[slug] = eff_v
                metric_values.append(
                    ComparedMetricValue(
                        country_slug=slug,
                        value=raw_v,
                        effective_value=eff_v,
                        quality_warnings=[],
                    )
                )

        delta: float | None = None
        winner_slug: str | None = None
        if len(country_slugs) == 2 and len(effective_values) == 2:
            s0, s1 = country_slugs[0], country_slugs[1]
            ev0, ev1 = effective_values[s0], effective_values[s1]
            delta = round(abs(ev0 - ev1), 2)
            if ev0 > ev1:
                winner_slug = s0
            elif ev1 > ev0:
                winner_slug = s1

        metrics.append(
            ComparedMetric(
                metric_slug=metric_slug,
                metric_name=metric_name,
                display_order=md["display_order"],
                higher_is_better=higher_is_better,
                weight=metric_weight,
                delta=delta,
                winner_country_slug=winner_slug,
                values=metric_values,
            )
        )

    resolved_locale = _resolve_locale(locale)

    return CiiCountryComparisonResponse(
        scenario=scenario,
        locale=resolved_locale,
        countries=countries,
        metrics=metrics,
        formula_version=formula_version,
        aggregation_method=aggregation_method,
        weights_version=weights_version,
        quality_warnings=quality_warnings,
    )


def _resolve_locale(locale: str) -> LocaleResolution:
    return locale_resolution(locale, locale, TranslationStatus.source)
