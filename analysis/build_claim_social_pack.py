#!/usr/bin/env python3
"""Create a social-ready sharp insight pack from VivaTech normalized CSVs."""

from __future__ import annotations

import csv
import html
import itertools
import json
import math
import re
import textwrap
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


BASE = Path(__file__).resolve().parent
OUT = BASE / "claim_outputs"
CARDS = OUT / "social_cards"
OUT.mkdir(exist_ok=True)
CARDS.mkdir(exist_ok=True)


@dataclass(frozen=True)
class EvidenceClaim:
    rank: int
    headline: str
    punchline: str
    evidence: str
    caveat: str
    metric: str
    controversy: int
    defensibility: int
    card_file: str


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def pct(numerator: float, denominator: float) -> float:
    return numerator / denominator * 100.0 if denominator else 0.0


def fmt(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}"


def split_tags(value: str) -> list[str]:
    return [part.strip() for part in value.split(" | ") if part.strip()]


def clean_svg(value: object) -> str:
    return html.escape(str(value), quote=True)


def wrap_lines(value: str, width: int) -> list[str]:
    return textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def svg_text_block(lines: list[str], x: int, y: int, size: int, weight: int, fill: str, line_height: int) -> list[str]:
    nodes = []
    for idx, line in enumerate(lines):
        nodes.append(
            f'<text x="{x}" y="{y + idx * line_height}" font-family="Inter, Arial, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{clean_svg(line)}</text>'
        )
    return nodes


def draw_social_card(claim: EvidenceClaim) -> str:
    width = 1080
    height = 1350
    palette = [
        ("#fbfaf7", "#161411", "#c94343", "#2454a6"),
        ("#11130f", "#fbfaf7", "#f2c94c", "#69d2a7"),
        ("#f7f2e8", "#161411", "#18805b", "#c94343"),
        ("#151515", "#f8f4ec", "#ff6b35", "#7cc6fe"),
    ][(claim.rank - 1) % 4]
    bg, ink, accent, accent2 = palette
    headline = wrap_lines(claim.headline, 21)
    punch = wrap_lines(claim.punchline, 34)
    evidence = wrap_lines(claim.evidence, 46)
    caveat = wrap_lines("Caveat: " + claim.caveat, 52)
    filename = f"card_{claim.rank:02d}.svg"

    nodes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f'<rect width="100%" height="100%" fill="{bg}"/>',
        f'<rect x="54" y="54" width="972" height="1242" rx="0" fill="none" stroke="{accent}" stroke-width="6"/>',
        f'<text x="82" y="120" font-family="Inter, Arial, sans-serif" font-size="30" font-weight="800" fill="{accent}">VivaTech evidence card {claim.rank:02d}</text>',
        f'<text x="82" y="170" font-family="Inter, Arial, sans-serif" font-size="28" font-weight="700" fill="{ink}" opacity="0.78">controversy {claim.controversy}/5 · defensibility {claim.defensibility}/5</text>',
        f'<text x="82" y="272" font-family="Inter, Arial, sans-serif" font-size="86" font-weight="900" fill="{accent2}">{clean_svg(claim.metric)}</text>',
    ]
    nodes.extend(svg_text_block(headline[:5], 82, 390, 72, 900, ink, 82))
    punch_y = 390 + min(len(headline), 5) * 82 + 44
    nodes.extend(svg_text_block(punch[:4], 82, punch_y, 36, 750, accent, 46))
    evidence_y = punch_y + min(len(punch), 4) * 46 + 62
    nodes.append(f'<rect x="82" y="{evidence_y - 36}" width="916" height="{max(150, len(evidence[:5]) * 36 + 52)}" fill="{ink}" opacity="0.07"/>')
    nodes.extend(svg_text_block(evidence[:5], 112, evidence_y, 27, 650, ink, 36))
    caveat_y = 1118
    nodes.extend(svg_text_block(caveat[:4], 82, caveat_y, 24, 500, ink, 32))
    nodes.append(f'<text x="82" y="1250" font-family="Inter, Arial, sans-serif" font-size="25" font-weight="800" fill="{accent}">Source: VivaTech company and speaker listing scrape, 2026-06-17</text>')
    nodes.append("</svg>")
    (CARDS / filename).write_text("\n".join(nodes), encoding="utf-8")
    return filename


def write_rows(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_generated_text(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.splitlines()) + "\n"


def build_html_deck(claims: list[EvidenceClaim], metrics: dict[str, object]) -> str:
    cards = []
    for claim in claims:
        cards.append(
            f"""
            <section class="card-row">
              <img src="claim_outputs/social_cards/{clean_svg(claim.card_file)}" alt="{clean_svg(claim.headline)}" />
              <div>
                <p class="rank">Card {claim.rank:02d}</p>
                <h2>{clean_svg(claim.headline)}</h2>
                <p class="punch">{clean_svg(claim.punchline)}</p>
                <p><strong>Evidence:</strong> {clean_svg(claim.evidence)}</p>
                <p class="caveat"><strong>Caveat:</strong> {clean_svg(claim.caveat)}</p>
              </div>
            </section>
            """
        )
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VivaTech Claim Card Pack</title>
  <style>
    body {{
      margin: 0;
      background: #fbfaf7;
      color: #171411;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 42px 22px 70px; }}
    h1 {{ font-size: clamp(2.4rem, 5vw, 5.5rem); line-height: 0.96; letter-spacing: 0; margin: 0 0 16px; }}
    .lede {{ color: #5f5750; max-width: 850px; font-size: 1.15rem; margin-bottom: 28px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      border: 1px solid #ddd4c8;
      margin: 28px 0 38px;
    }}
    .metric {{ padding: 18px; border-right: 1px solid #ddd4c8; }}
    .metric:last-child {{ border-right: none; }}
    .metric strong {{ display: block; font-size: 2rem; }}
    .metric span {{ color: #5f5750; }}
    .card-row {{
      display: grid;
      grid-template-columns: minmax(280px, 0.38fr) minmax(0, 0.62fr);
      gap: 30px;
      border-top: 1px solid #ddd4c8;
      padding: 34px 0;
      align-items: start;
    }}
    img {{ width: 100%; height: auto; display: block; border: 1px solid #ddd4c8; }}
    h2 {{ font-size: clamp(1.6rem, 3.5vw, 3.8rem); line-height: 1; letter-spacing: 0; margin: 0 0 14px; }}
    p {{ color: #5f5750; font-size: 1rem; }}
    .punch {{ color: #c94343; font-size: 1.2rem; font-weight: 800; }}
    .rank {{ color: #2454a6; font-weight: 900; text-transform: uppercase; letter-spacing: 0.08em; }}
    .caveat {{ border-left: 4px solid #ddd4c8; padding-left: 14px; }}
    @media (max-width: 820px) {{
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .card-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>VivaTech's viral story is not AI. It is who gets the microphone.</h1>
  <p class="lede">These are social-ready, sharp-but-defensible claim cards. Each claim uses the public company and speaker listing scrape, and each includes the caveat needed to avoid overclaiming.</p>
  <section class="metrics">
    <div class="metric"><strong>{metrics["company_count"]:,}</strong><span>companies</span></div>
    <div class="metric"><strong>{metrics["speaker_count"]:,}</strong><span>speakers</span></div>
    <div class="metric"><strong>{metrics["matched_speakers"]:,}</strong><span>matched speakers</span></div>
    <div class="metric"><strong>{metrics["claim_count"]}</strong><span>social claims</span></div>
  </section>
  {''.join(cards)}
</main>
</body>
</html>
"""
    return clean_generated_text(html_doc)


def main() -> None:
    companies = read_csv("companies_normalized.csv")
    speakers = read_csv("speakers_normalized.csv")
    matches = read_csv("speaker_company_matches.csv")
    coverage = read_csv("company_speaker_coverage.csv")
    tag_rows = read_csv("tag_comparison.csv")
    country_rows = read_csv("country_tension.csv")
    fundraising_rows = read_csv("fundraising_distribution.csv")
    missing_rows = read_csv("data_quality_missingness.csv")

    assert len(companies) == 3153
    assert len(speakers) == 1133
    assert len(matches) == len(speakers)

    company_count = len(companies)
    speaker_count = len(speakers)
    matched_speakers = sum(1 for row in matches if row["matched"] == "True")
    type_counts = Counter(row["type"] for row in companies)
    matched_type_counts = Counter(row["company_type"] for row in matches if row["matched"] == "True")
    matched_top_type_counts = Counter(row["company_type"] for row in matches if row["matched"] == "True" and row["top_speaker"] == "True")

    top_speaker_tags = Counter((row["top"] == "True", bool(row["tags"].strip())) for row in speakers)
    top_total = top_speaker_tags[(True, False)] + top_speaker_tags[(True, True)]
    non_top_total = top_speaker_tags[(False, False)] + top_speaker_tags[(False, True)]
    top_tagless_pct = pct(top_speaker_tags[(True, False)], top_total)
    non_top_tagless_pct = pct(top_speaker_tags[(False, False)], non_top_total)

    company_ids_with_speakers = {row["company_id"] for row in matches if row["matched"] == "True"}
    hall_rows: list[dict[str, object]] = []
    for hall, count in Counter(row["hall"] or "<blank>" for row in companies).most_common():
        companies_with_speakers = sum(1 for row in companies if (row["hall"] or "<blank>") == hall and row["id"] in company_ids_with_speakers)
        hall_matched_speakers = sum(1 for row in matches if row["matched"] == "True" and (row["hall"] or "<blank>") == hall)
        hall_rows.append(
            {
                "hall": hall,
                "companies": count,
                "company_share_pct": round(pct(count, company_count), 1),
                "companies_with_speakers": companies_with_speakers,
                "coverage_pct": round(pct(companies_with_speakers, count), 1),
                "matched_speakers": hall_matched_speakers,
                "matched_speakers_per_100_companies": round(pct(hall_matched_speakers, count), 1),
            }
        )
    write_rows(OUT / "hall_attention.csv", hall_rows, list(hall_rows[0].keys()))

    label_rows: list[dict[str, object]] = []
    company_by_id = {row["id"]: row for row in companies}
    for label, count in Counter(row["label"] or "<blank>" for row in companies).most_common():
        matched_company_ids = {row["company_id"] for row in matches if row["matched"] == "True" and (company_by_id[row["company_id"]]["label"] or "<blank>") == label}
        matched_label_speakers = sum(1 for row in matches if row["matched"] == "True" and (company_by_id[row["company_id"]]["label"] or "<blank>") == label)
        label_rows.append(
            {
                "label": label,
                "companies": count,
                "company_share_pct": round(pct(count, company_count), 1),
                "companies_with_speakers": len(matched_company_ids),
                "coverage_pct": round(pct(len(matched_company_ids), count), 1),
                "matched_speakers": matched_label_speakers,
                "matched_speakers_per_100_companies": round(pct(matched_label_speakers, count), 1),
            }
        )
    write_rows(OUT / "label_attention.csv", label_rows, list(label_rows[0].keys()))

    tag_pair_counter: Counter[tuple[str, str]] = Counter()
    for row in companies:
        tags = sorted(set(split_tags(row["tags"])))
        for left, right in itertools.combinations(tags, 2):
            tag_pair_counter[(left, right)] += 1
    pair_rows = [
        {"left_tag": left, "right_tag": right, "company_count": count}
        for (left, right), count in tag_pair_counter.most_common(30)
    ]
    write_rows(OUT / "top_tag_pairs.csv", pair_rows, ["left_tag", "right_tag", "company_count"])

    duplicate_name_rows = []
    normalized_counts = Counter(row["normalized_name"] for row in companies if row["normalized_name"])
    for normalized_name, count in normalized_counts.most_common(40):
        if count <= 1:
            break
        names = sorted({row["name"].strip() for row in companies if row["normalized_name"] == normalized_name})
        duplicate_name_rows.append({"normalized_name": normalized_name, "company_rows": count, "display_names": " | ".join(names[:8])})
    write_rows(OUT / "duplicate_company_names.csv", duplicate_name_rows, ["normalized_name", "company_rows", "display_names"])

    tag_lookup = {row["tag"]: row for row in tag_rows}
    country_lookup = {row["country"]: row for row in country_rows}
    funding_lookup = {row["fundraising_stage"]: row for row in fundraising_rows}
    missing_lookup = {(row["dataset"], row["field"]): row for row in missing_rows}

    top_matched_total = sum(matched_top_type_counts.values())
    partner_top_density = pct(matched_top_type_counts["partner"], type_counts["partner"])
    startup_top_density = pct(matched_top_type_counts["startup"], type_counts["startup"])
    top_density_multiplier = partner_top_density / startup_top_density if startup_top_density else math.inf
    partner_loudness = (matched_type_counts["partner"] / type_counts["partner"]) / (matched_type_counts["startup"] / type_counts["startup"])

    tech_label = next(row for row in label_rows if row["label"] == "techforchange")
    blank_label = next(row for row in label_rows if row["label"] == "<blank>")
    techforchange_under_amp = blank_label["matched_speakers_per_100_companies"] / tech_label["matched_speakers_per_100_companies"]

    retail = tag_lookup["Retail & E-commerce"]
    ai = tag_lookup["Artificial Intelligence & Robotics"]
    media = tag_lookup["Media & Entertainment & Creators Economy"]
    us = country_lookup["United States of America"]
    india = country_lookup["India"]
    korea_total_companies = int(country_lookup["South Korea"]["companies"]) + int(country_lookup["korearepublicof"]["companies"])
    korea_total_speakers = int(country_lookup["South Korea"]["matched_speakers"]) + int(country_lookup["korearepublicof"]["matched_speakers"])
    korea_density = pct(korea_total_speakers, korea_total_companies)
    us_density = float(us["speaker_per_100_companies"])
    series_c_density = float(funding_lookup["Series C - $50M - $200M"]["speaker_per_100_companies"])
    bootstrap_density = float(funding_lookup["Bootstrapped - 0"]["speaker_per_100_companies"])
    short_desc_missing = missing_lookup[("companies", "short_desc")]

    preliminary_claims = [
        (
            "Partners are 21x louder per company than startups.",
            "The event sells a startup floor, but the matched microphone belongs to institutions.",
            f"Partners are {fmt(pct(type_counts['partner'], company_count))}% of exhibitors and {fmt(pct(matched_type_counts['partner'], matched_speakers))}% of matched speaker slots. Startups are {fmt(pct(type_counts['startup'], company_count))}% of exhibitors and {fmt(pct(matched_type_counts['startup'], matched_speakers))}% of matched speaker slots.",
            "This is based on conservative exhibitor-speaker organization matching; unmatched speakers are excluded.",
            f"{fmt(partner_loudness)}x",
            5,
            5,
        ),
        (
            "Top billing almost erases startups.",
            "Only one top-billed matched speaker maps to a startup exhibitor.",
            f"Among {top_matched_total} top-billed speakers that matched exhibitors, {matched_top_type_counts['partner']} map to partners and {matched_top_type_counts['startup']} maps to a startup. Per exhibitor, partner top-billing density is {fmt(top_density_multiplier)}x startup density.",
            "This only counts top speakers that match exhibitor organizations; celebrity and government speakers often do not match exhibitors.",
            "1 startup",
            5,
            4,
        ),
        (
            "Top speakers are twice as likely to be tagless.",
            "The highest-status speaker layer is less classified by topic than ordinary speakers.",
            f"{fmt(top_tagless_pct)}% of top speakers have no speaker tags, compared with {fmt(non_top_tagless_pct)}% of non-top speakers.",
            "A missing tag is a listing-data signal, not proof that the speaker lacks a topic.",
            f"{fmt(top_tagless_pct)}%",
            4,
            5,
        ),
        (
            "Tech for Change is under-amplified.",
            "The moral label shows up on the floor, but weakly converts into matched speakers.",
            f"Tech for Change has {tech_label['companies']} exhibitors but {tech_label['matched_speakers']} matched speakers: {tech_label['matched_speakers_per_100_companies']} per 100 companies. Unlabeled exhibitors have {blank_label['matched_speakers_per_100_companies']} per 100, about {fmt(techforchange_under_amp)}x higher.",
            "The label may identify a curated floor program rather than a stage program; still, the attention gap is real in the listing data.",
            f"{fmt(techforchange_under_amp)}x gap",
            5,
            4,
        ),
        (
            "The floor is concentrated in one hall, but attention is still scarce.",
            "Booth geography does not explain the microphone gap.",
            f"Pavillon 7 contains {hall_rows[0]['companies']} exhibitors ({hall_rows[0]['company_share_pct']}% of all companies), yet only {hall_rows[0]['companies_with_speakers']} of those companies have a matched speaker ({hall_rows[0]['coverage_pct']}%).",
            "Hall values are listing fields; 636 companies have no hall value in the payload.",
            f"{hall_rows[0]['coverage_pct']}%",
            4,
            5,
        ),
        (
            "Retail is the booth economy with almost no speaker narrative.",
            "A commercially visible category is nearly absent from the speaker tag layer.",
            f"Retail & E-commerce has {retail['company_count']} tagged exhibitors ({retail['company_share_pct']}%) but only {retail['speaker_count']} tagged speakers ({retail['speaker_share_pct']}%), a {retail['speaker_minus_company_share_pp']} point under-index.",
            "Tags are multi-select listing categories, not exclusive sectors.",
            "337 vs 6",
            4,
            5,
        ),
        (
            "AI is not the story. AI is the wallpaper.",
            "When nearly half the event is tagged AI, the sharper story is who gets amplified inside AI.",
            f"AI/Robotics appears on {ai['company_count']} exhibitors ({ai['company_share_pct']}%) and {ai['speaker_count']} speakers ({ai['speaker_share_pct']}%).",
            "The AI tag measures listing taxonomy, not product quality or real AI depth.",
            f"{ai['company_share_pct']}%",
            4,
            5,
        ),
        (
            "The US punches far above its booth count.",
            "Booths and agenda leverage tell different geopolitical stories.",
            f"The US has {us['companies']} exhibitors and {us['matched_speakers']} matched speakers ({us['speaker_per_100_companies']} per 100 companies). India has {india['companies']} exhibitors and {india['matched_speakers']} matched speakers ({india['speaker_per_100_companies']} per 100).",
            "Country labels come from exhibitor records and need normalization before official rankings.",
            f"{fmt(us_density / float(india['speaker_per_100_companies']))}x",
            5,
            4,
        ),
        (
            "Korea has booth mass but almost no matched microphone.",
            "After fixing the split country label, Korea remains almost silent in matched speaker density.",
            f"South Korea plus `korearepublicof` totals {korea_total_companies} exhibitor records but only {korea_total_speakers} matched speakers, or {fmt(korea_density)} per 100 companies.",
            "This claim depends on normalizing the raw country split and may undercount unmatched speaker organizations.",
            f"{fmt(korea_density)}",
            4,
            4,
        ),
        (
            "Funding maturity buys microphone odds.",
            "The event celebrates early startups, but later-stage companies get much better matched speaker density.",
            f"Series C exhibitors show {fmt(series_c_density)} matched speakers per 100 companies, versus {fmt(bootstrap_density)} for bootstrapped companies.",
            "Series C has only 24 companies, so this is a directional signal rather than a causal proof.",
            f"{fmt(series_c_density / bootstrap_density)}x",
            4,
            4,
        ),
        (
            "The public exhibitor list is not built for understanding companies.",
            "It is a sorting layer, not a discovery layer.",
            f"{short_desc_missing['missing_count']} of {company_count} exhibitor short descriptions are empty ({short_desc_missing['missing_pct']}%).",
            "Detail pages may contain richer information; this claim is scoped to the bulk listing payload.",
            "100%",
            3,
            5,
        ),
        (
            "The same normalized company names repeat across the floor.",
            "Even before external enrichment, identity resolution is a real analytical problem.",
            f"{sum(1 for row in duplicate_name_rows if row['company_rows'] > 1)} normalized company names appear more than once; examples include {duplicate_name_rows[0]['normalized_name']} and {duplicate_name_rows[1]['normalized_name']}.",
            "Some repeats are legitimate multi-booth or naming collisions; do not dedupe without manual review.",
            f"{len(duplicate_name_rows)} names",
            3,
            4,
        ),
    ]

    claims: list[EvidenceClaim] = []
    for rank, raw in enumerate(preliminary_claims, start=1):
        claim = EvidenceClaim(rank, *raw, card_file="")
        card = draw_social_card(claim)
        claims.append(EvidenceClaim(rank, claim.headline, claim.punchline, claim.evidence, claim.caveat, claim.metric, claim.controversy, claim.defensibility, card))

    claim_rows = [claim.__dict__ for claim in claims]
    write_rows(OUT / "claim_bank.csv", claim_rows, list(claim_rows[0].keys()))

    metrics = {
        "company_count": company_count,
        "speaker_count": speaker_count,
        "matched_speakers": matched_speakers,
        "claim_count": len(claims),
        "partner_loudness_multiplier": partner_loudness,
        "partner_top_density_per_100_exhibitors": partner_top_density,
        "startup_top_density_per_100_exhibitors": startup_top_density,
        "top_speaker_tagless_pct": top_tagless_pct,
        "non_top_speaker_tagless_pct": non_top_tagless_pct,
        "techforchange_under_amplification_multiplier": techforchange_under_amp,
        "korea_combined_companies": korea_total_companies,
        "korea_combined_matched_speakers": korea_total_speakers,
        "korea_combined_density_per_100": korea_density,
        "outputs": {
            "claims": str(OUT / "claim_bank.csv"),
            "deck": str(BASE / "claim_social_deck.html"),
            "cards_dir": str(CARDS),
        },
    }
    (OUT / "claim_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# VivaTech Claim Outputs\n\n"
        "This folder contains second-stage, social-ready VivaTech claims and visuals generated from the normalized company and speaker CSVs.\n\n"
        "- `claim_bank.csv`: ranked claim bank with evidence and caveats.\n"
        "- `social_cards/`: 1080x1350 SVG cards for sharing or screenshotting.\n"
        "- `hall_attention.csv`, `label_attention.csv`, `top_tag_pairs.csv`, `duplicate_company_names.csv`: supporting derived tables.\n",
        encoding="utf-8",
    )
    (BASE / "claim_social_deck.html").write_text(build_html_deck(claims, metrics), encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
