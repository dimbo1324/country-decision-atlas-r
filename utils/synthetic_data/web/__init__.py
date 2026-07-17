"""Synthetic Web Environment: a browsable, deterministic web of fictional
sites rendered over an already-built SyntheticWorld (core/world_models.py).

Module map:
  models.py         SyntheticSite/SitePage/LinkEdge/PageAnomaly -- pure data
  archetypes.py      WebConfig -- reads/validates input_data/web_config.json
  graph.py           build_web_graph() -- deterministic site/page/link graph
  anomalies.py       assign_anomalies() -- intentionally broken pages/links
  html_renderer.py   renders SitePage entries to real .html files (stdlib
                     templating only, no jinja2)
  assets.py          shared inline CSS, favicon, placeholder image
  validation.py      link/download resolution checks over a built graph
  server.py          FastAPI app serving /sites/... and /files/...

This package never invents world facts of its own -- every site page is
grounded in an existing SyntheticCountry/SyntheticSource/SyntheticArticle/
SyntheticLegalSignal. Anomaly pages (404/500/redirect/duplicate/empty/huge/
broken-encoding) are the one deliberate exception: they exist to be broken,
by design, for testing link-handling code.
"""

from __future__ import annotations
