from __future__ import annotations

import html
from collections import Counter
from pathlib import Path
from typing import cast
from utils.synthetic_data.core.world_models import (
    FICTIONAL_NOTICE,
    SyntheticCountry,
    SyntheticScenario,
    SyntheticWorld,
)


_STYLE = """
body { font-family: system-ui, sans-serif; margin: 2rem; color: #1a1a1a; }
h1 { margin-bottom: 0.25rem; }
h2 { margin-top: 2.5rem; border-bottom: 2px solid #ddd; padding-bottom: 0.25rem; }
.notice { background: #fff3cd; border: 1px solid #ffe08a; padding: 0.75rem 1rem;
  border-radius: 6px; font-weight: 600; margin: 1rem 0; }
.meta { color: #555; font-size: 0.9rem; }
.meta dt { font-weight: 600; display: inline; }
.meta dd { display: inline; margin: 0 1.5rem 0 0.35rem; }
table { border-collapse: collapse; width: 100%; margin: 0.75rem 0 1.5rem; }
th, td { border: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left;
  vertical-align: top; font-size: 0.92rem; }
th { background: #f5f5f5; }
.country-card { border: 1px solid #ddd; border-radius: 8px; padding: 1rem 1.25rem;
  margin-bottom: 1.25rem; }
.country-card h3 { margin-top: 0; }
.tag { display: inline-block; background: #eef; border-radius: 4px;
  padding: 0.1rem 0.5rem; margin: 0.1rem 0.25rem 0.1rem 0; font-size: 0.85rem; }
.risk { background: #fee; }
.strength { background: #efe; }
.uncertainty { background: #ffe; }
footer { margin-top: 3rem; color: #777; font-size: 0.85rem; }
a { color: #1a5fb4; }
"""


def _escape(value: object) -> str:
    return html.escape(str(value))


def _tag_list(values: tuple[str, ...], css_class: str) -> str:
    if not values:
        return '<span class="meta">none</span>'
    return "".join(
        f'<span class="tag {css_class}">{_escape(value)}</span>'
        for value in values
    )


def _metrics_table(metrics: dict[str, int]) -> str:
    rows = "".join(
        f"<tr><th>{_escape(name)}</th><td>{value}</td></tr>"
        for name, value in sorted(metrics.items())
    )
    return f"<table>{rows}</table>"


def _country_card(country: SyntheticCountry) -> str:
    return f"""
<div class="country-card">
  <h3>{_escape(country.name)} <span class="meta">({_escape(country.code)} / {_escape(country.slug)})</span></h3>
  <p class="meta">Archetype: <strong>{_escape(country.archetype)}</strong>
    &middot; {len(country.events)} event(s) &middot; {len(country.sources)} source(s)</p>
  {_metrics_table(country.current_metrics)}
  <p><strong>Strengths:</strong> {_tag_list(country.strengths, "strength")}</p>
  <p><strong>Risks:</strong> {_tag_list(country.risks, "risk")}</p>
  <p><strong>Uncertainties:</strong> {_tag_list(country.uncertainties, "uncertainty")}</p>
</div>
"""


def _scenario_row(scenario: SyntheticScenario) -> str:
    return f"""<tr>
  <td>{_escape(scenario.title)}</td>
  <td>{_escape(scenario.category)}</td>
  <td>{len(scenario.steps)}</td>
  <td>{len(scenario.expected_results)}</td>
  <td>{_tag_list(scenario.risk_labels, "risk")}</td>
</tr>"""


def _artifact_rows(manifest: dict[str, object]) -> str:
    artifacts = cast(list[dict[str, object]], manifest["artifacts"])
    counts: Counter[tuple[str, str]] = Counter()
    example_href: dict[tuple[str, str], str] = {}
    for entry in artifacts:
        # World-level files (canonical JSON, SQL fixtures) carry no
        # locale — they're already linked from the footer, so only
        # locale-specific rendered documents belong in this table.
        locale = entry.get("locale")
        if locale is None:
            continue
        file_format = cast(str, entry["format"])
        key = (cast(str, locale), file_format)
        counts[key] += 1
        example_href.setdefault(key, f"../{entry['path']}")

    rows = []
    for (locale, file_format), count in sorted(counts.items()):
        href = example_href[(locale, file_format)]
        rows.append(
            f"<tr><td>{_escape(locale)}</td><td>{_escape(file_format)}</td>"
            f'<td>{count}</td><td><a href="{_escape(href)}">example</a></td></tr>'
        )
    return "".join(rows)


def render_dashboard(
    *,
    world: SyntheticWorld,
    manifest: dict[str, object],
    dataset_dir: Path,
) -> Path:
    """A single self-contained HTML page summarizing a generated dataset
    (countries, metrics, scenarios, artifact counts with links) so a
    reviewer can sanity-check a run without opening dozens of files by
    hand. Reads only from the already-built canonical `world` and
    `manifest` — it never invents facts of its own."""
    metadata = world.metadata
    countries_html = "".join(
        _country_card(country) for country in world.countries
    )
    scenarios_html = "".join(
        _scenario_row(scenario) for scenario in world.scenarios
    )
    artifact_rows = _artifact_rows(manifest)

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Synthetic dataset {_escape(metadata.dataset_id)}</title>
<style>{_STYLE}</style>
</head>
<body>
<h1>Synthetic dataset {_escape(metadata.dataset_id)}</h1>
<div class="notice">{_escape(FICTIONAL_NOTICE)}</div>
<dl class="meta">
  <dt>Profile</dt><dd>{_escape(metadata.profile)}</dd>
  <dt>Seed</dt><dd>{metadata.seed}</dd>
  <dt>Schema</dt><dd>{_escape(metadata.schema_version)}</dd>
  <dt>Generator</dt><dd>{_escape(metadata.generator_version)}</dd>
  <dt>Generated on</dt><dd>{_escape(metadata.generated_on)}</dd>
  <dt>Locales</dt><dd>{len(metadata.supported_locales)}</dd>
  <dt>Countries</dt><dd>{len(world.countries)}</dd>
  <dt>Scenarios</dt><dd>{len(world.scenarios)}</dd>
</dl>

<h2>Countries</h2>
{countries_html}

<h2>Scenarios</h2>
<table>
  <tr><th>Title</th><th>Category</th><th>Steps</th><th>Expected results</th><th>Risk labels</th></tr>
  {scenarios_html}
</table>

<h2>Documents by locale &amp; format</h2>
<table>
  <tr><th>Locale</th><th>Format</th><th>Count</th><th>Open one</th></tr>
  {artifact_rows}
</table>

<footer>
  <a href="../manifest.json">manifest.json</a> &middot;
  <a href="validation_report.json">validation_report.json</a> &middot;
  <a href="generation_summary.md">generation_summary.md</a> &middot;
  <a href="manifest.sha256">manifest.sha256</a>
</footer>
</body>
</html>
"""
    path = dataset_dir / "reports" / "dashboard.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")
    return path
