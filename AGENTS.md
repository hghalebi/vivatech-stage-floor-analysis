# AGENTS.md

## Project Goal

Maintain a public, static VivaTech 2026 exhibitor/speaker analysis dashboard with downloadable normalized data, derived analysis tables, visualizations, and publish-ready media assets.

## Architecture

- Source data lives in normalized CSV and JSON files at the repository root.
- Build scripts are Python entrypoints named `build_*.py`.
- The public dashboard lives in `dynamic_dashboard/`.
- Dashboard templates live in `dashboard_templates/` and are copied by `build_dynamic_dashboard.py`.
- No backend is required; the dashboard runs from local files or a static host.

## Category-Theory Framing

- Objects: companies, speakers, speaker-company matches, claims, chart rows, evidence cards, downloadable assets.
- Morphisms: scrape normalization, conservative matching, aggregation, chart rendering, claim filtering, table search, and bundle packaging.
- Composition: raw public listings -> normalized data -> derived analysis -> dashboard data bundle -> interactive UI.
- Invariant: provocative claims must remain linked to evidence and caveats, and must not become unsupported accusations of sponsorship causality.

## Validation Commands

```bash
python3 -m py_compile build_dynamic_dashboard.py
python3 build_dynamic_dashboard.py
node --check dynamic_dashboard/dashboard.js
```

For rendered checks, run a local static server from `dynamic_dashboard/`:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Then validate desktop and mobile behavior with a browser or Playwright.

## Public-Release Safety

- Do not commit secrets, credentials, tokens, private browser/session state, or raw local artifacts.
- Keep `.DS_Store`, Python caches, raw fetched HTML, and temporary validation screenshots out of Git.
- This repository contains public listing data and derived analysis; preserve methodology caveats.
- Do not claim sponsorship causality unless future evidence directly proves it.

## Editing Rules

- Keep the dashboard static and shareable.
- Prefer rebuilding generated dashboard files with `build_dynamic_dashboard.py`.
- Preserve source CSVs and derived CSVs used by the dashboard.
- Use clear, evidence-linked language for controversial claims.
