#!/usr/bin/env python3
"""Checkpointed web-search enrichment for VivaTech companies and speakers.

The script performs one web search per entity and appends a compact JSONL record
after each search so it can resume safely. It uses Bing's public HTML result page
because the available SERPER_API_KEY is not authorized for Serper or SerpApi.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent
OUT = BASE / "web_enrichment"
OUT.mkdir(exist_ok=True)
ENTITY_FILE = OUT / "web_enrichment_entities_official.csv"
RESULT_FILE = OUT / "web_search_results_official.jsonl"
FAILURE_FILE = OUT / "web_search_failures_official.csv"
SUMMARY_FILE = OUT / "web_search_summary_official.json"


USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
]


@dataclass(frozen=True)
class Entity:
    entity_id: str
    entity_type: str
    display_name: str
    query: str
    context: dict[str, str]


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def stable_id(prefix: str, *parts: str) -> str:
    raw = "\u241f".join(parts).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()[:20]
    return f"{prefix}_{digest}"


def build_entities() -> list[Entity]:
    companies = read_csv("companies_normalized.csv")
    speakers = read_csv("speakers_normalized.csv")
    entities: list[Entity] = []

    for row in companies:
        name = row["name"].strip()
        country = row["country"].strip()
        tags = row["tags"].strip()
        slug = row["slug"].strip()
        query_parts = ["site:vivatech.com/exhibitors", f'"{name}"', "VivaTech"]
        if slug:
            query_parts.append(slug)
        entities.append(
            Entity(
                entity_id=stable_id("company", row["id"], name),
                entity_type="company",
                display_name=name,
                query=" ".join(query_parts),
                context={
                    "source_id": row["id"],
                    "company_type": row["type"],
                    "country": country,
                    "tags": tags,
                    "fundraising": row["fundraising"],
                    "query_scope": "official_vivatech_site",
                },
            )
        )

    for row in speakers:
        full_name = row["full_name"].strip()
        company = row["company"].strip()
        job_title = row["job_title"].strip()
        slug = row["slug"].strip()
        query_parts = ["site:vivatech.com/speakers", f'"{full_name}"', "VivaTech"]
        if company:
            query_parts.append(f'"{company}"')
        elif job_title:
            query_parts.append(f'"{job_title}"')
        if slug:
            query_parts.append(slug)
        entities.append(
            Entity(
                entity_id=stable_id("speaker", row["id"], full_name, company),
                entity_type="speaker",
                display_name=full_name,
                query=" ".join(query_parts),
                context={
                    "source_id": row["id"],
                    "company": company,
                    "job_title": job_title,
                    "tags": row["tags"],
                    "top": row["top"],
                    "query_scope": "official_vivatech_site",
                },
            )
        )

    return entities


def write_entity_file(entities: list[Entity]) -> None:
    with ENTITY_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=["entity_id", "entity_type", "display_name", "query", "context_json"],
        )
        writer.writeheader()
        for entity in entities:
            writer.writerow(
                {
                    "entity_id": entity.entity_id,
                    "entity_type": entity.entity_type,
                    "display_name": entity.display_name,
                    "query": entity.query,
                    "context_json": json.dumps(entity.context, ensure_ascii=False, sort_keys=True),
                }
            )


def load_completed() -> set[str]:
    completed: set[str] = set()
    if not RESULT_FILE.exists():
        return completed
    with RESULT_FILE.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            entity_id = row.get("entity_id")
            if isinstance(entity_id, str):
                completed.add(entity_id)
    return completed


def decode_bing_link(href: str) -> str:
    href = html.unescape(href)
    parsed = urllib.parse.urlparse(href)
    params = urllib.parse.parse_qs(parsed.query)
    encoded = params.get("u", [None])[0]
    if not encoded:
        return href
    if encoded.startswith("a1"):
        encoded = encoded[2:]
    padded = encoded + "=" * (-len(encoded) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8", errors="replace")
    except Exception:
        return href


def clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_bing_results(page: str, limit: int) -> list[dict[str, object]]:
    chunks = re.findall(r'<li class="b_algo"[^>]*>(.*?)(?=<li class="b_algo"|</ol>)', page, flags=re.S)
    results: list[dict[str, object]] = []
    for chunk in chunks:
        anchor = re.search(r"<h2[^>]*>\s*<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", chunk, flags=re.S)
        if not anchor:
            continue
        snippet_match = re.search(r'<p[^>]*>(.*?)</p>', chunk, flags=re.S)
        results.append(
            {
                "position": len(results) + 1,
                "title": clean_text(anchor.group(2)),
                "link": decode_bing_link(anchor.group(1)),
                "snippet": clean_text(snippet_match.group(1)) if snippet_match else "",
            }
        )
        if len(results) >= limit:
            break
    return results


def search_bing(query: str, result_limit: int, timeout: float) -> tuple[list[dict[str, object]], str]:
    params = urllib.parse.urlencode({"q": query, "setlang": "en-US", "count": str(max(result_limit, 10))})
    url = f"https://www.bing.com/search?{params}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        page = response.read().decode("utf-8", errors="replace")
    results = parse_bing_results(page, result_limit)
    lowered = page.lower()
    challenge_markers = [
        "unusual traffic",
        "verify you are human",
        "solve the challenge",
        "anomaly-modal",
        "captcha challenge",
    ]
    if not results and any(marker in lowered for marker in challenge_markers):
        raise RuntimeError("search page appears to be blocked by anti-bot challenge")
    return results, url


def append_failure(entity: Entity, error: str) -> None:
    new_file = not FAILURE_FILE.exists()
    with FAILURE_FILE.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=["timestamp_utc", "entity_id", "entity_type", "display_name", "query", "error"],
        )
        if new_file:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "entity_id": entity.entity_id,
                "entity_type": entity.entity_type,
                "display_name": entity.display_name,
                "query": entity.query,
                "error": error,
            }
        )


def append_result(entity: Entity, source_url: str, results: list[dict[str, object]]) -> None:
    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "entity_id": entity.entity_id,
        "entity_type": entity.entity_type,
        "display_name": entity.display_name,
        "query": entity.query,
        "search_engine": "bing_html",
        "source_url": source_url,
        "context": entity.context,
        "result_count": len(results),
        "results": results,
    }
    with RESULT_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
        handle.write("\n")


def write_summary(entities: list[Entity], completed: set[str], attempted_this_run: int, failed_this_run: int) -> None:
    type_counts: dict[str, int] = {}
    completed_type_counts: dict[str, int] = {}
    for entity in entities:
        type_counts[entity.entity_type] = type_counts.get(entity.entity_type, 0) + 1
        if entity.entity_id in completed:
            completed_type_counts[entity.entity_type] = completed_type_counts.get(entity.entity_type, 0) + 1
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "entity_file": str(ENTITY_FILE),
        "result_file": str(RESULT_FILE),
        "failure_file": str(FAILURE_FILE),
        "total_entities": len(entities),
        "total_by_type": type_counts,
        "completed_entities": len(completed),
        "completed_by_type": completed_type_counts,
        "remaining_entities": len(entities) - len(completed),
        "attempted_this_run": attempted_this_run,
        "failed_this_run": failed_this_run,
    }
    SUMMARY_FILE.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    entities = build_entities()
    write_entity_file(entities)
    completed = load_completed()
    remaining = [entity for entity in entities if entity.entity_id not in completed]
    if args.entity_type != "all":
        remaining = [entity for entity in remaining if entity.entity_type == args.entity_type]
    if args.offset:
        remaining = remaining[args.offset :]
    if args.max_entities is not None:
        remaining = remaining[: args.max_entities]

    attempted = 0
    failed = 0
    for entity in remaining:
        attempted += 1
        try:
            results, source_url = search_bing(entity.query, args.results, args.timeout)
            append_result(entity, source_url, results)
            completed.add(entity.entity_id)
            print(json.dumps({"ok": True, "entity_id": entity.entity_id, "type": entity.entity_type, "name": entity.display_name, "results": len(results)}, ensure_ascii=False), flush=True)
        except Exception as exc:
            failed += 1
            append_failure(entity, str(exc))
            print(json.dumps({"ok": False, "entity_id": entity.entity_id, "type": entity.entity_type, "name": entity.display_name, "error": str(exc)}, ensure_ascii=False), flush=True)
            if args.stop_on_error:
                break
        if args.delay > 0 and attempted < len(remaining):
            time.sleep(args.delay + random.uniform(0, args.jitter))

    write_summary(entities, completed, attempted, failed)
    return 1 if args.stop_on_error and failed else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-entities", type=int, default=None, help="Maximum number of remaining entities to search this run.")
    parser.add_argument("--entity-type", choices=["all", "company", "speaker"], default="all")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many currently remaining entities before searching.")
    parser.add_argument("--results", type=int, default=5, help="Search results to retain per entity.")
    parser.add_argument("--delay", type=float, default=1.0, help="Base delay between searches in seconds.")
    parser.add_argument("--jitter", type=float, default=0.3, help="Additional random delay in seconds.")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout per search.")
    parser.add_argument("--stop-on-error", action="store_true")
    return parser.parse_args(argv)


def main() -> int:
    return run(parse_args(sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
