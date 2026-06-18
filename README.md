# VivaTech Stage vs Floor Analysis

Static public-data dashboard and analysis bundle for VivaTech 2026 exhibitor and speaker listings.

## What This Contains

- `dynamic_dashboard/`: shareable static dashboard, no backend required.
- `companies_normalized.csv`, `speakers_normalized.csv`, `speaker_company_matches.csv`: normalized source tables.
- Derived analysis CSVs for company type coverage, country leverage, tag gaps, funding maturity, role buckets, and data quality.
- SVG visualization packs, polemic claim cards, and a publish media kit.
- Python scripts used to build the reports, visualizations, dashboard, and enrichment status files.

## Open The Dashboard

Open:

```text
dynamic_dashboard/index.html
```

The dashboard is plain HTML/CSS/JS and uses embedded data from:

```text
dynamic_dashboard/data/dashboard_data.js
```

## Rebuild

```bash
python3 build_dynamic_dashboard.py
```

Optional validation:

```bash
python3 -m py_compile build_dynamic_dashboard.py
node --check dynamic_dashboard/dashboard.js
```

## Methodology Caveat

The analysis uses public VivaTech listings and conservative company-speaker matching. It supports an evidence-backed governance critique about concentration of public speaker attention, but it does not prove sponsorship causality or any specific pay-for-stage transaction.

## Data Source

Public VivaTech 2026 pages were used as the source for exhibitor and speaker listings. Web-search enrichment remained partial because available search credentials were unauthorized and public search challenged sustained batches.
