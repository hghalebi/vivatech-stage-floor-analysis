# VivaTech Web Enrichment Status

Status: Partial, not complete for all entities.

## Target Scope

- Total one-by-one web-search entities: 4286
- Companies: 3153
- Speakers: 1133

## What Worked

- Generated a checkpointed entity list: `/Users/hamzeghalebi/Downloads/vivatech_analysis_20260617/web_enrichment/web_enrichment_entities_official.csv`
- Generated a resumable search script: `/Users/hamzeghalebi/Downloads/vivatech_analysis_20260617/enrich_entities_with_web_search.py`
- Broad Bing HTML mode saved 71 successful company searches to `/Users/hamzeghalebi/Downloads/vivatech_analysis_20260617/web_enrichment/web_search_results.jsonl`.
- Viral/polemic report and SVG visuals were generated independently from the validated VivaTech data.

## What Failed Or Is Not Reliable

- `SERPER_API_KEY` exists, but Serper returned `HTTP 403 Unauthorized`.
- The same key is not valid for SerpApi: `HTTP 401 Invalid API key`.
- The cloned `serpscraper` repo expects SerpApi JSON and failed with `missing field search_metadata`.
- Public Bing HTML search began returning anti-bot challenge pages during sustained batches.
- Generic broad-web search is noisy for ambiguous company names like `10%`; official-site-scoped search is more relevant but was fully challenged by Bing in the sample run.
- Direct VivaTech detail page probes timed out or reset, so they are not a proven bulk enrichment path yet.

## Current Evidence Files

- Broad search results: `/Users/hamzeghalebi/Downloads/vivatech_analysis_20260617/web_enrichment/web_search_results.jsonl`
- Broad search failures: `/Users/hamzeghalebi/Downloads/vivatech_analysis_20260617/web_enrichment/web_search_failures.csv`
- Official-site search failures: `/Users/hamzeghalebi/Downloads/vivatech_analysis_20260617/web_enrichment/web_search_failures_official.csv`
- Summary JSON: `/Users/hamzeghalebi/Downloads/vivatech_analysis_20260617/web_enrichment/web_search_summary_official.json`

## Next Concrete Action

To complete all 4286 one-by-one searches reliably, use a valid search API credential or a browser-backed search workflow with long throttling and checkpointing. The current script is already checkpointed and can resume once a reliable search backend is available.
