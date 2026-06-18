#!/usr/bin/env python3
"""Build a sharper VivaTech claim bank and visual report from normalized CSVs.

This script intentionally uses only the Python standard library so it remains
portable in the current workspace.
"""

from __future__ import annotations

import csv
import html
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BASE = Path(__file__).resolve().parent
OUT = BASE / "viral_outputs"
OUT.mkdir(exist_ok=True)


@dataclass(frozen=True)
class Claim:
    short_name: str
    viral_headline: str
    evidence: str
    why_it_could_spread: str
    caveat: str
    controversy_score: int
    defensibility_score: int
    chart_file: str


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def pct(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator * 100.0


def one_decimal(value: float) -> str:
    return f"{value:.1f}"


def split_tags(value: str) -> list[str]:
    return [part.strip() for part in value.split(" | ") if part.strip()]


def as_int(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value == "":
        return 0
    return int(float(value))


def as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value == "":
        return 0.0
    return float(value)


def html_text(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_bar_chart(
    title: str,
    subtitle: str,
    rows: list[dict[str, object]],
    label_key: str,
    value_key: str,
    unit: str,
    filename: str,
    color: str = "#2454A6",
    compare_key: str | None = None,
    compare_label: str | None = None,
    compare_color: str = "#C94343",
    width: int = 1180,
    row_height: int = 48,
) -> str:
    left = 330
    top = 120
    right = 70
    bottom = 60
    plot_width = width - left - right
    height = top + bottom + max(1, len(rows)) * row_height
    values = [float(row[value_key]) for row in rows]
    if compare_key:
        values.extend(float(row[compare_key]) for row in rows)
    max_value = max(values) if values else 1.0
    if max_value <= 0:
        max_value = 1.0
    max_value *= 1.08

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"<title>{html_text(title)}</title>",
        f"<desc>{html_text(subtitle)}</desc>",
        '<rect width="100%" height="100%" fill="#fbfaf7"/>',
        f'<text x="40" y="48" font-family="Inter, Arial, sans-serif" font-size="28" font-weight="800" fill="#1b1b1b">{html_text(title)}</text>',
        f'<text x="40" y="82" font-family="Inter, Arial, sans-serif" font-size="16" fill="#4f4a45">{html_text(subtitle)}</text>',
    ]

    for idx, row in enumerate(rows):
        y = top + idx * row_height
        label = str(row[label_key])
        value = float(row[value_key])
        bar_width = max(1, value / max_value * plot_width)
        parts.append(f'<text x="40" y="{y + 27}" font-family="Inter, Arial, sans-serif" font-size="15" fill="#26221f">{html_text(label)}</text>')
        if compare_key:
            comp = float(row[compare_key])
            comp_width = max(1, comp / max_value * plot_width)
            parts.append(f'<rect x="{left}" y="{y + 8}" width="{comp_width:.1f}" height="12" rx="2" fill="{compare_color}" opacity="0.70"/>')
            parts.append(f'<rect x="{left}" y="{y + 24}" width="{bar_width:.1f}" height="12" rx="2" fill="{color}" opacity="0.90"/>')
            parts.append(f'<text x="{left + max(bar_width, comp_width) + 8:.1f}" y="{y + 34}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#26221f">{one_decimal(value)}{unit}</text>')
        else:
            parts.append(f'<rect x="{left}" y="{y + 10}" width="{bar_width:.1f}" height="24" rx="3" fill="{color}" opacity="0.92"/>')
            parts.append(f'<text x="{left + bar_width + 8:.1f}" y="{y + 29}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#26221f">{one_decimal(value)}{unit}</text>')

    if compare_key:
        legend_y = height - 28
        parts.append(f'<rect x="40" y="{legend_y - 11}" width="16" height="10" fill="{compare_color}" opacity="0.70"/>')
        parts.append(f'<text x="64" y="{legend_y}" font-family="Inter, Arial, sans-serif" font-size="13" fill="#4f4a45">{html_text(compare_label or compare_key)}</text>')
        parts.append(f'<rect x="240" y="{legend_y - 11}" width="16" height="10" fill="{color}" opacity="0.90"/>')
        parts.append(f'<text x="264" y="{legend_y}" font-family="Inter, Arial, sans-serif" font-size="13" fill="#4f4a45">{html_text(str(value_key))}</text>')

    parts.append("</svg>")
    svg = "\n".join(parts)
    (OUT / filename).write_text(svg, encoding="utf-8")
    return filename


def svg_diverging_bar_chart(
    title: str,
    subtitle: str,
    rows: list[dict[str, object]],
    label_key: str,
    value_key: str,
    filename: str,
    width: int = 1180,
    row_height: int = 46,
) -> str:
    left = 360
    right = 70
    top = 120
    bottom = 50
    plot_width = width - left - right
    center = left + plot_width / 2
    height = top + bottom + max(1, len(rows)) * row_height
    max_abs = max(abs(float(row[value_key])) for row in rows) if rows else 1.0
    max_abs = max(max_abs * 1.1, 1.0)
    half = plot_width / 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"<title>{html_text(title)}</title>",
        f"<desc>{html_text(subtitle)}</desc>",
        '<rect width="100%" height="100%" fill="#fbfaf7"/>',
        f'<text x="40" y="48" font-family="Inter, Arial, sans-serif" font-size="28" font-weight="800" fill="#1b1b1b">{html_text(title)}</text>',
        f'<text x="40" y="82" font-family="Inter, Arial, sans-serif" font-size="16" fill="#4f4a45">{html_text(subtitle)}</text>',
        f'<line x1="{center:.1f}" y1="{top - 14}" x2="{center:.1f}" y2="{height - bottom + 8}" stroke="#7c756d" stroke-width="1"/>',
        f'<text x="{center + 8:.1f}" y="{top - 20}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#625b54">speaker over-index</text>',
        f'<text x="{center - 145:.1f}" y="{top - 20}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#625b54">speaker under-index</text>',
    ]
    for idx, row in enumerate(rows):
        y = top + idx * row_height
        label = str(row[label_key])
        value = float(row[value_key])
        bar_width = abs(value) / max_abs * half
        if value < 0:
            x = center - bar_width
            color = "#C94343"
        else:
            x = center
            color = "#2454A6"
        parts.append(f'<text x="40" y="{y + 26}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#26221f">{html_text(label)}</text>')
        parts.append(f'<rect x="{x:.1f}" y="{y + 10}" width="{bar_width:.1f}" height="22" rx="3" fill="{color}" opacity="0.88"/>')
        tx = x - 50 if value < 0 else x + bar_width + 8
        parts.append(f'<text x="{tx:.1f}" y="{y + 27}" font-family="Inter, Arial, sans-serif" font-size="13" fill="#26221f">{value:+.1f} pp</text>')
    parts.append("</svg>")
    svg = "\n".join(parts)
    (OUT / filename).write_text(svg, encoding="utf-8")
    return filename


def write_claim_bank(claims: list[Claim]) -> None:
    with (OUT / "viral_claim_bank.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=[
                "short_name",
                "viral_headline",
                "evidence",
                "why_it_could_spread",
                "caveat",
                "controversy_score",
                "defensibility_score",
                "chart_file",
            ],
        )
        writer.writeheader()
        for claim in claims:
            writer.writerow(claim.__dict__)


def markdown_table(claims: Iterable[Claim]) -> str:
    lines = [
        "|rank|claim|evidence|caveat|score|",
        "|---:|---|---|---|---:|",
    ]
    ordered = sorted(claims, key=lambda claim: (claim.controversy_score, claim.defensibility_score), reverse=True)
    for idx, claim in enumerate(ordered, start=1):
        lines.append(
            "|{}|{}|{}|{}|{}|".format(
                idx,
                claim.viral_headline.replace("|", "/"),
                claim.evidence.replace("|", "/"),
                claim.caveat.replace("|", "/"),
                claim.controversy_score,
            )
        )
    return "\n".join(lines)


def html_report(claims: list[Claim], summary: dict[str, object]) -> str:
    cards = []
    for claim in sorted(claims, key=lambda item: (item.controversy_score, item.defensibility_score), reverse=True):
        img = f"viral_outputs/{html_text(claim.chart_file)}"
        cards.append(
            f"""
            <section class="claim">
              <div class="claim-copy">
                <p class="score">controversy {claim.controversy_score}/5 · defensibility {claim.defensibility_score}/5</p>
                <h2>{html_text(claim.viral_headline)}</h2>
                <p class="evidence">{html_text(claim.evidence)}</p>
                <p>{html_text(claim.why_it_could_spread)}</p>
                <p class="caveat"><strong>Caveat:</strong> {html_text(claim.caveat)}</p>
              </div>
              <img src="{img}" alt="{html_text(claim.short_name)} chart" />
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VivaTech Viral Pattern Report</title>
  <style>
    :root {{
      --ink: #181614;
      --muted: #5f5750;
      --paper: #fbfaf7;
      --line: #ded8cf;
      --blue: #2454a6;
      --red: #c94343;
      --green: #18805b;
    }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 42px 24px 64px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 28px;
      margin-bottom: 28px;
    }}
    h1 {{
      font-size: clamp(2.3rem, 5vw, 5.2rem);
      line-height: 0.96;
      letter-spacing: 0;
      margin: 0 0 18px;
      max-width: 980px;
    }}
    .dek {{
      font-size: 1.15rem;
      max-width: 860px;
      color: var(--muted);
      margin: 0;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 1px;
      background: var(--line);
      border: 1px solid var(--line);
      margin: 28px 0;
    }}
    .metric {{
      background: var(--paper);
      padding: 18px;
      min-height: 92px;
    }}
    .metric strong {{
      display: block;
      font-size: 2rem;
      line-height: 1;
    }}
    .metric span {{
      display: block;
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.95rem;
    }}
    .claim {{
      display: grid;
      grid-template-columns: minmax(280px, 0.42fr) minmax(0, 0.58fr);
      gap: 28px;
      padding: 28px 0;
      border-top: 1px solid var(--line);
      align-items: start;
    }}
    .claim h2 {{
      font-size: clamp(1.65rem, 3vw, 3.4rem);
      line-height: 1.02;
      letter-spacing: 0;
      margin: 0 0 14px;
    }}
    .claim p {{
      color: var(--muted);
      font-size: 1rem;
      margin: 0 0 12px;
    }}
    .claim .evidence {{
      color: var(--ink);
      font-weight: 700;
    }}
    .score {{
      color: var(--red) !important;
      text-transform: uppercase;
      font-size: 0.78rem !important;
      letter-spacing: 0.08em;
      font-weight: 800;
    }}
    .caveat {{
      border-left: 4px solid var(--line);
      padding-left: 12px;
    }}
    img {{
      display: block;
      width: 100%;
      height: auto;
      border: 1px solid var(--line);
      background: var(--paper);
    }}
    footer {{
      color: var(--muted);
      border-top: 1px solid var(--line);
      padding-top: 20px;
      margin-top: 28px;
      font-size: 0.95rem;
    }}
    @media (max-width: 860px) {{
      .metrics {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .claim {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 520px) {{
      .metrics {{
        grid-template-columns: 1fr;
      }}
      main {{
        padding: 28px 16px 48px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>VivaTech's floor is startup; its microphone is institutional.</h1>
      <p class="dek">A deliberately sharper evidence pack from the VivaTech exhibitor and speaker data. The point is not outrage by vibes: every claim below has a numerator, denominator, caveat, and reusable chart.</p>
    </header>
    <section class="metrics" aria-label="Dataset metrics">
      <div class="metric"><strong>{summary["companies"]:,}</strong><span>exhibitor companies</span></div>
      <div class="metric"><strong>{summary["speakers"]:,}</strong><span>speaker records</span></div>
      <div class="metric"><strong>{summary["matched_speakers"]:,}</strong><span>speakers matched to exhibitors</span></div>
      <div class="metric"><strong>{summary["companies_with_speakers_pct"]:.1f}%</strong><span>exhibitors with a matched speaker</span></div>
    </section>
    {''.join(cards)}
    <footer>
      Source: live VivaTech listing scrape, generated 2026-06-17. Local Documents CSVs were blocked by macOS permissions, so this report uses the freshly validated live scrape. Matching is conservative and likely undercounts true organization links.
    </footer>
  </main>
</body>
</html>
"""


def main() -> None:
    companies = read_csv("companies_normalized.csv")
    speakers = read_csv("speakers_normalized.csv")
    matches = read_csv("speaker_company_matches.csv")
    coverage = read_csv("company_speaker_coverage.csv")
    tag_rows = read_csv("tag_comparison.csv")
    country_rows = read_csv("country_tension.csv")
    fundraising_rows = read_csv("fundraising_distribution.csv")
    role_rows = read_csv("role_buckets.csv")
    leader_rows = read_csv("speaker_company_leaders.csv")
    missing_rows = read_csv("data_quality_missingness.csv")

    company_count = len(companies)
    speaker_count = len(speakers)
    matched_speakers = sum(1 for row in matches if row["matched"] == "True")
    companies_with_speakers = len(coverage)
    assert company_count == 3153, company_count
    assert speaker_count == 1133, speaker_count
    assert len(matches) == speaker_count, len(matches)
    assert matched_speakers == 355, matched_speakers

    type_counts = Counter(row["type"] for row in companies)
    type_speaker_counts: Counter[str] = Counter()
    type_coverage_counts: Counter[str] = Counter(row["type"] for row in coverage)
    for row in matches:
        if row["matched"] == "True":
            type_speaker_counts[row["company_type"]] += 1

    partner_per_company = type_speaker_counts["partner"] / type_counts["partner"]
    startup_per_company = type_speaker_counts["startup"] / type_counts["startup"]
    mic_multiplier = partner_per_company / startup_per_company
    coverage_multiplier = pct(type_coverage_counts["partner"], type_counts["partner"]) / pct(type_coverage_counts["startup"], type_counts["startup"])

    type_share_rows = []
    for kind in ["startup", "partner"]:
        type_share_rows.append(
            {
                "company_type": kind,
                "exhibitor_share_pct": pct(type_counts[kind], company_count),
                "matched_speaker_share_pct": pct(type_speaker_counts[kind], matched_speakers),
                "speakers_per_100_companies": pct(type_speaker_counts[kind], type_counts[kind]),
            }
        )

    chart_agenda_capture = svg_bar_chart(
        "Partner-class exhibitors capture the microphone",
        "Matched speaker share vs exhibitor share by company type",
        type_share_rows,
        "company_type",
        "matched_speaker_share_pct",
        "%",
        "01_partner_agenda_capture.svg",
        color="#2454A6",
        compare_key="exhibitor_share_pct",
        compare_label="exhibitor share",
        compare_color="#C94343",
    )

    country_enriched = []
    country_map = {row["country"]: row for row in country_rows}
    for row in country_rows:
        companies_n = as_int(row, "companies")
        if companies_n < 20:
            continue
        country_enriched.append(
            {
                "country": row["country"],
                "companies": companies_n,
                "matched_speakers": as_int(row, "matched_speakers"),
                "speaker_per_100_companies": as_float(row, "speaker_per_100_companies"),
            }
        )
    country_focus_names = [
        "United States of America",
        "United Kingdom",
        "China",
        "Hong Kong",
        "France",
        "Germany",
        "India",
        "Canada",
        "South Korea",
        "korearepublicof",
    ]
    country_focus = [row for name in country_focus_names for row in country_enriched if row["country"] == name]
    chart_country_leverage = svg_bar_chart(
        "Booths do not equal agenda power",
        "Matched speakers per 100 exhibitor companies, selected countries with >=20 exhibitors",
        sorted(country_focus, key=lambda row: row["speaker_per_100_companies"], reverse=True),
        "country",
        "speaker_per_100_companies",
        "",
        "02_country_mic_leverage.svg",
        color="#18805B",
    )

    korea_combined_companies = as_int(country_map["South Korea"], "companies") + as_int(country_map["korearepublicof"], "companies")
    korea_combined_speakers = as_int(country_map["South Korea"], "matched_speakers") + as_int(country_map["korearepublicof"], "matched_speakers")
    korea_density = pct(korea_combined_speakers, korea_combined_companies)
    usa_density = as_float(country_map["United States of America"], "speaker_per_100_companies")
    india_density = as_float(country_map["India"], "speaker_per_100_companies")
    canada_density = as_float(country_map["Canada"], "speaker_per_100_companies")

    under_index_tags = sorted(
        [
            {
                "tag": row["tag"],
                "speaker_minus_company_share_pp": as_float(row, "speaker_minus_company_share_pp"),
                "company_count": as_int(row, "company_count"),
                "speaker_count": as_int(row, "speaker_count"),
                "speaker_per_100_tagged_companies": as_float(row, "speaker_per_100_tagged_companies"),
            }
            for row in tag_rows
        ],
        key=lambda row: row["speaker_minus_company_share_pp"],
    )[:10]
    chart_tag_silence = svg_diverging_bar_chart(
        "The booth-heavy topics with quieter stages",
        "Speaker share minus exhibitor share, percentage points",
        under_index_tags,
        "tag",
        "speaker_minus_company_share_pp",
        "03_tag_silence.svg",
    )

    leader_focus = [
        {
            "speaker_company": row["speaker_company"],
            "speaker_count": as_int(row, "speaker_count"),
        }
        for row in leader_rows[:12]
    ]
    chart_orgs = svg_bar_chart(
        "Who owns the most speaker slots?",
        "Top speaker organizations by speaker count",
        leader_focus,
        "speaker_company",
        "speaker_count",
        "",
        "04_speaker_org_power.svg",
        color="#2454A6",
    )

    funding_explicit = [
        row for row in fundraising_rows
        if row["fundraising_stage"] not in {"Unspecified"} and as_int(row, "companies") >= 20
    ]
    funding_order = {
        "Bootstrapped - 0": 1,
        "Not yet - 0": 2,
        "Pre-Seed - <$1M": 3,
        "Seed - $1M - $5M": 4,
        "Series A - $5M - $15M": 5,
        "Series B - $15M - $50M": 6,
        "Series C - $50M - $200M": 7,
    }
    funding_rows = sorted(
        [
            {
                "fundraising_stage": row["fundraising_stage"],
                "speaker_per_100_companies": as_float(row, "speaker_per_100_companies"),
                "companies": as_int(row, "companies"),
            }
            for row in funding_explicit
        ],
        key=lambda row: funding_order.get(row["fundraising_stage"], 99),
    )
    chart_funding = svg_bar_chart(
        "Funding maturity buys microphone odds",
        "Matched speakers per 100 companies among explicit fundraising labels",
        funding_rows,
        "fundraising_stage",
        "speaker_per_100_companies",
        "",
        "05_funding_mic_odds.svg",
        color="#C94343",
    )

    role_chart_rows = [
        {
            "role_bucket": row["role_bucket"],
            "speaker_share_pct": as_float(row, "speaker_share_pct"),
            "top_speaker_share_in_bucket_pct": as_float(row, "top_speaker_share_in_bucket_pct"),
            "speakers": as_int(row, "speakers"),
        }
        for row in role_rows
    ]
    chart_roles = svg_bar_chart(
        "VivaTech's stage is a boss layer",
        "Speaker share by role bucket",
        role_chart_rows,
        "role_bucket",
        "speaker_share_pct",
        "%",
        "06_boss_stage.svg",
        color="#18805B",
    )

    ai_company_count = sum(1 for row in companies if "Artificial Intelligence & Robotics" in split_tags(row["tags"]))
    ai_speaker_count = sum(1 for row in speakers if "Artificial Intelligence & Robotics" in split_tags(row["tags"]))
    ai_company_pct = pct(ai_company_count, company_count)
    ai_speaker_pct = pct(ai_speaker_count, speaker_count)

    company_ai_cotags: Counter[str] = Counter()
    speaker_ai_cotags: Counter[str] = Counter()
    for row in companies:
        tags = split_tags(row["tags"])
        if "Artificial Intelligence & Robotics" in tags:
            company_ai_cotags.update(tag for tag in tags if tag != "Artificial Intelligence & Robotics")
    for row in speakers:
        tags = split_tags(row["tags"])
        if "Artificial Intelligence & Robotics" in tags:
            speaker_ai_cotags.update(tag for tag in tags if tag != "Artificial Intelligence & Robotics")
    ai_cotag_rows = []
    for tag, count in company_ai_cotags.most_common(8):
        ai_cotag_rows.append(
            {
                "tag": tag,
                "company_ai_cotag_share_pct": pct(count, ai_company_count),
                "speaker_ai_cotag_share_pct": pct(speaker_ai_cotags.get(tag, 0), ai_speaker_count),
            }
        )
    chart_ai = svg_bar_chart(
        "AI is the grammar, not the headline",
        "Among AI-tagged records, strongest exhibitor co-tags",
        ai_cotag_rows,
        "tag",
        "company_ai_cotag_share_pct",
        "%",
        "07_ai_cotags.svg",
        color="#2454A6",
        compare_key="speaker_ai_cotag_share_pct",
        compare_label="speaker AI co-tag share",
        compare_color="#C94343",
    )

    top_speakers = [row for row in speakers if row["top"] == "True"]
    top_speaker_count = len(top_speakers)
    role_map = {row["role_bucket"]: row for row in role_rows}
    gov_top_rate = as_float(role_map["Government / public sector"], "top_speaker_share_in_bucket_pct")
    overall_top_rate = pct(top_speaker_count, speaker_count)
    gov_multiplier = gov_top_rate / overall_top_rate if overall_top_rate else 0.0
    boss_count = sum(as_int(role_map[name], "speakers") for name in ["CEO / president / GM", "Founder / co-founder", "Other C-suite"])
    boss_share = pct(boss_count, speaker_count)

    description_missing = next(row for row in missing_rows if row["dataset"] == "companies" and row["field"] == "short_desc")
    fundraising_missing = next(row for row in missing_rows if row["dataset"] == "companies" and row["field"] == "fundraising")

    top10_org_speakers = sum(as_int(row, "speaker_count") for row in leader_rows[:10])
    top10_org_share = pct(top10_org_speakers, speaker_count)

    claims = [
        Claim(
            short_name="partner_agenda_capture",
            viral_headline=f"Partners are {one_decimal(mic_multiplier)}x louder per company than startups.",
            evidence=(
                f"Partners are {one_decimal(pct(type_counts['partner'], company_count))}% of exhibitors "
                f"but {one_decimal(pct(type_speaker_counts['partner'], matched_speakers))}% of matched speaker slots; "
                f"startup exhibitors are {one_decimal(pct(type_counts['startup'], company_count))}% of the floor but "
                f"{one_decimal(pct(type_speaker_counts['startup'], matched_speakers))}% of matched speaker slots."
            ),
            why_it_could_spread="It turns a generic startup-event narrative into a power-distribution claim: the floor sells startup energy, while the microphone rewards institutions.",
            caveat="Only speakers whose organizations conservatively match exhibitors are included; unmatched speakers may change some shares but not the exhibitor-side imbalance.",
            controversy_score=5,
            defensibility_score=5,
            chart_file=chart_agenda_capture,
        ),
        Claim(
            short_name="voiceless_floor",
            viral_headline=f"{one_decimal(100 - pct(companies_with_speakers, company_count))}% of exhibitors appear voiceless in the speaker program.",
            evidence=f"Only {companies_with_speakers} of {company_count} exhibitors have at least one matched speaker; for startups the no-matched-speaker rate is {one_decimal(100 - pct(type_coverage_counts['startup'], type_counts['startup']))}%.",
            why_it_could_spread="It gives founders a blunt way to talk about the difference between buying/earning a booth and owning agenda visibility.",
            caveat="This is based on public listing data and conservative organization matching, not internal stage selection data.",
            controversy_score=5,
            defensibility_score=5,
            chart_file=chart_agenda_capture,
        ),
        Claim(
            short_name="country_agenda_leverage",
            viral_headline="The US has fewer booths than India, but roughly 27x the matched-speaker density.",
            evidence=(
                f"US: {as_int(country_map['United States of America'], 'companies')} exhibitors and "
                f"{as_int(country_map['United States of America'], 'matched_speakers')} matched speakers "
                f"({one_decimal(usa_density)} per 100 companies). India: {as_int(country_map['India'], 'companies')} exhibitors and "
                f"{as_int(country_map['India'], 'matched_speakers')} matched speakers ({one_decimal(india_density)} per 100)."
            ),
            why_it_could_spread="It reframes country presence from booth count to agenda leverage, which is much more politically sensitive.",
            caveat="Country values come from exhibitor records after matching; country normalization and unmatched speaker organizations can move this metric.",
            controversy_score=5,
            defensibility_score=4,
            chart_file=chart_country_leverage,
        ),
        Claim(
            short_name="korea_silent_supply",
            viral_headline="Korea has 153 exhibitor records after normalizing the split label, but only 2 matched speakers.",
            evidence=(
                f"`South Korea` has 96 exhibitors and `korearepublicof` has 57. Combined density is "
                f"{one_decimal(korea_density)} matched speakers per 100 companies, versus {one_decimal(usa_density)} for the US."
            ),
            why_it_could_spread="It is both a data-quality gotcha and a market-visibility claim: a large booth presence can still be nearly silent on the matched stage layer.",
            caveat="The raw country split must be normalized before any official country ranking; unmatched Korean speaker organizations may be missing from the conservative match.",
            controversy_score=4,
            defensibility_score=4,
            chart_file=chart_country_leverage,
        ),
        Claim(
            short_name="retail_silence",
            viral_headline="Retail has 337 exhibitors but only 6 speakers: a booth-heavy topic with almost no mic.",
            evidence="Retail & E-commerce is 10.7% of exhibitor tags but 0.5% of speaker tags, a -10.2 percentage point speaker under-index.",
            why_it_could_spread="It challenges the commercial reality of tech events: some market categories pay/show up, but do not get to define the public agenda.",
            caveat="Tag fields are multi-select listing tags, so counts represent tagged records rather than exclusive categories.",
            controversy_score=4,
            defensibility_score=5,
            chart_file=chart_tag_silence,
        ),
        Claim(
            short_name="funding_mic_odds",
            viral_headline="Among explicit funding labels, Series C startups have about 8x the mic density of bootstrapped companies.",
            evidence="Series C: 16.7 matched speakers per 100 companies. Bootstrapped: 2.1 per 100. Pre-seed: 2.3 per 100.",
            why_it_could_spread="It makes the prestige gradient visible: the event may celebrate early startups, but later-stage companies are much more stage-visible.",
            caveat="Series C has only 24 companies, and partner records often have unspecified fundraising; use this as a directional signal, not a causal claim.",
            controversy_score=4,
            defensibility_score=4,
            chart_file=chart_funding,
        ),
        Claim(
            short_name="boss_stage",
            viral_headline=f"The speaker program is a boss layer: {one_decimal(boss_share)}% are CEOs/founders/C-suite.",
            evidence=(
                f"CEO/president/GM, founder/co-founder, and other C-suite buckets total {boss_count} of {speaker_count} speakers. "
                f"Government/public-sector speakers are only 2.6% of speakers but are top-billed at {one_decimal(gov_top_rate)}% inside their bucket, "
                f"{one_decimal(gov_multiplier)}x the overall top-speaker rate."
            ),
            why_it_could_spread="It names the social structure of the stage: not a broad worker/practitioner program, but a leadership and legitimacy program.",
            caveat="Role buckets are keyword-derived from public job titles and should be reviewed manually before publication.",
            controversy_score=4,
            defensibility_score=4,
            chart_file=chart_roles,
        ),
        Claim(
            short_name="ai_saturation",
            viral_headline="AI is so saturated that it has stopped being the interesting label.",
            evidence=(
                f"{ai_company_count} of {company_count} exhibitors ({one_decimal(ai_company_pct)}%) and "
                f"{ai_speaker_count} of {speaker_count} speakers ({one_decimal(ai_speaker_pct)}%) carry the AI/Robotics tag."
            ),
            why_it_could_spread="It punctures the easy AI hype angle: the more interesting story is which categories AI attaches to and which still get ignored.",
            caveat="This is tag-level saturation, not a measure of product depth, revenue, or actual AI capability.",
            controversy_score=4,
            defensibility_score=5,
            chart_file=chart_ai,
        ),
        Claim(
            short_name="directory_opacity",
            viral_headline="The public exhibitor list is a taxonomy machine, not a discovery engine.",
            evidence=(
                f"{as_int(description_missing, 'missing_count')} exhibitor short descriptions are empty "
                f"({one_decimal(as_float(description_missing, 'missing_pct'))}%), and {as_int(fundraising_missing, 'missing_count')} "
                f"fundraising fields are missing ({one_decimal(as_float(fundraising_missing, 'missing_pct'))}%)."
            ),
            why_it_could_spread="It shifts criticism from individual exhibitors to platform design: the listing is better for sorting than understanding.",
            caveat="Detail pages may contain richer text; this claim is scoped to the listing payload used for bulk discovery.",
            controversy_score=3,
            defensibility_score=5,
            chart_file=chart_ai,
        ),
        Claim(
            short_name="speaker_org_concentration",
            viral_headline="A few organizations can bend the agenda more than thousands of booths can.",
            evidence=f"The top 10 speaker organizations account for {top10_org_speakers} speaker records ({one_decimal(top10_org_share)}% of all speakers), led by L'Oreal and PwC.",
            why_it_could_spread="It makes agenda-setting visible without needing private sponsorship data.",
            caveat="The top-organization table uses displayed speaker organization names; some subsidiaries and country suffixes may split or merge imperfectly.",
            controversy_score=3,
            defensibility_score=4,
            chart_file=chart_orgs,
        ),
    ]

    write_claim_bank(claims)

    summary = {
        "companies": company_count,
        "speakers": speaker_count,
        "matched_speakers": matched_speakers,
        "companies_with_speakers": companies_with_speakers,
        "companies_with_speakers_pct": pct(companies_with_speakers, company_count),
        "partner_mic_multiplier": mic_multiplier,
        "partner_coverage_multiplier": coverage_multiplier,
        "ai_company_pct": ai_company_pct,
        "ai_speaker_pct": ai_speaker_pct,
        "usa_vs_india_density_multiplier": usa_density / india_density if india_density else None,
        "usa_vs_canada_density_multiplier": usa_density / canada_density if canada_density else None,
        "korea_combined_companies": korea_combined_companies,
        "korea_combined_matched_speakers": korea_combined_speakers,
        "korea_combined_density": korea_density,
        "boss_share_pct": boss_share,
        "government_top_speaker_multiplier": gov_multiplier,
        "top10_org_speaker_share_pct": top10_org_share,
        "chart_files": sorted({claim.chart_file for claim in claims}),
    }

    (OUT / "viral_metrics_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    report_md = f"""# VivaTech Viral/Polemic Pattern Bank

Generated from the normalized VivaTech company and speaker scrape.

## Sharpest Claims

{markdown_table(claims)}

## How To Use These Claims Without Overclaiming

- Say "matched speaker" when making exhibitor-stage overlap claims.
- Say "speaker density" rather than "influence" unless you have independent influence evidence.
- Treat country results as directional until raw country labels are normalized.
- Avoid fuzzy company matching in viral claims unless a manual review sample is added.
- The strongest defensible polemic is structural: VivaTech's floor is startup-heavy, but its matched microphone layer is partner-heavy.

## Generated Visuals

""" + "\n".join(f"- `{claim.chart_file}` - {claim.short_name}" for claim in claims) + "\n"
    (OUT / "viral_polemic_report.md").write_text(report_md, encoding="utf-8")
    (BASE / "viral_visual_report.html").write_text(html_report(claims, summary), encoding="utf-8")

    print(json.dumps({"ok": True, "out_dir": str(OUT), "html_report": str(BASE / "viral_visual_report.html"), "claims": len(claims), **summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
