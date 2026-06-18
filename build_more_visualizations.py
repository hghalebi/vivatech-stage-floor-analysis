#!/usr/bin/env python3
"""Generate additional VivaTech visualizations from the normalized CSVs."""

from __future__ import annotations

import csv
import html
import itertools
import json
import math
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
OUT = BASE / "more_visualizations"
SVG_DIR = OUT / "svg"
OUT.mkdir(exist_ok=True)
SVG_DIR.mkdir(exist_ok=True)


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def pct(numerator: float, denominator: float) -> float:
    return numerator / denominator * 100.0 if denominator else 0.0


def f1(value: float) -> str:
    return f"{value:.1f}"


def split_tags(value: str) -> list[str]:
    return [part.strip() for part in value.split(" | ") if part.strip()]


def write_svg(filename: str, content: str) -> str:
    path = SVG_DIR / filename
    path.write_text(content, encoding="utf-8")
    return filename


def svg_shell(title: str, subtitle: str, width: int, height: int, body: list[str]) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            '<rect width="100%" height="100%" fill="#fbfaf7"/>',
            f'<text x="40" y="52" font-family="Inter, Arial, sans-serif" font-size="28" font-weight="900" fill="#171411">{esc(title)}</text>',
            f'<text x="40" y="84" font-family="Inter, Arial, sans-serif" font-size="15" fill="#5f5750">{esc(subtitle)}</text>',
            *body,
            "</svg>",
        ]
    )


def bar_chart(
    filename: str,
    title: str,
    subtitle: str,
    rows: list[dict[str, object]],
    label_key: str,
    value_key: str,
    unit: str = "",
    color: str = "#2454a6",
    width: int = 1180,
    row_height: int = 42,
) -> str:
    left = 360
    top = 120
    height = top + max(1, len(rows)) * row_height + 50
    plot_w = width - left - 80
    max_value = max(float(row[value_key]) for row in rows) if rows else 1.0
    max_value = max(max_value * 1.08, 1.0)
    body: list[str] = []
    for idx, row in enumerate(rows):
        y = top + idx * row_height
        val = float(row[value_key])
        bar_w = max(1, val / max_value * plot_w)
        body.append(f'<text x="40" y="{y + 25}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#171411">{esc(row[label_key])}</text>')
        body.append(f'<rect x="{left}" y="{y + 8}" width="{bar_w:.1f}" height="22" rx="3" fill="{color}" opacity="0.9"/>')
        body.append(f'<text x="{left + bar_w + 8:.1f}" y="{y + 25}" font-family="Inter, Arial, sans-serif" font-size="13" fill="#171411">{f1(val)}{unit}</text>')
    return write_svg(filename, svg_shell(title, subtitle, width, height, body))


def grouped_bar_chart(filename: str, title: str, subtitle: str, rows: list[dict[str, object]], label_key: str, left_key: str, right_key: str, left_label: str, right_label: str) -> str:
    width = 1180
    left = 360
    top = 128
    row_height = 58
    height = top + len(rows) * row_height + 70
    plot_w = width - left - 90
    max_value = max(max(float(row[left_key]), float(row[right_key])) for row in rows) * 1.12
    body = [
        '<rect x="40" y="98" width="14" height="10" fill="#c94343"/><text x="62" y="108" font-family="Inter, Arial, sans-serif" font-size="13" fill="#5f5750">' + esc(left_label) + "</text>",
        '<rect x="250" y="98" width="14" height="10" fill="#2454a6"/><text x="272" y="108" font-family="Inter, Arial, sans-serif" font-size="13" fill="#5f5750">' + esc(right_label) + "</text>",
    ]
    for idx, row in enumerate(rows):
        y = top + idx * row_height
        left_val = float(row[left_key])
        right_val = float(row[right_key])
        left_w = max(1, left_val / max_value * plot_w)
        right_w = max(1, right_val / max_value * plot_w)
        body.append(f'<text x="40" y="{y + 30}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#171411">{esc(row[label_key])}</text>')
        body.append(f'<rect x="{left}" y="{y + 8}" width="{left_w:.1f}" height="16" rx="2" fill="#c94343" opacity="0.82"/>')
        body.append(f'<rect x="{left}" y="{y + 30}" width="{right_w:.1f}" height="16" rx="2" fill="#2454a6" opacity="0.88"/>')
        body.append(f'<text x="{left + max(left_w, right_w) + 8:.1f}" y="{y + 43}" font-family="Inter, Arial, sans-serif" font-size="13" fill="#171411">{f1(left_val)} / {f1(right_val)}</text>')
    return write_svg(filename, svg_shell(title, subtitle, width, height, body))


def scatter_chart(filename: str, title: str, subtitle: str, rows: list[dict[str, object]], x_key: str, y_key: str, label_key: str) -> str:
    width, height = 1180, 760
    left, top, right, bottom = 120, 120, 80, 100
    plot_w, plot_h = width - left - right, height - top - bottom
    max_x = max(float(row[x_key]) for row in rows) * 1.08
    max_y = max(float(row[y_key]) for row in rows) * 1.08
    body = [
        f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#7f766e"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#7f766e"/>',
        f'<text x="{left + plot_w - 160}" y="{top + plot_h + 48}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#5f5750">exhibitor share %</text>',
        f'<text x="30" y="{top + 20}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#5f5750">speaker share %</text>',
    ]
    for row in rows:
        x = left + float(row[x_key]) / max_x * plot_w
        y = top + plot_h - float(row[y_key]) / max_y * plot_h
        gap = float(row.get("gap", 0))
        color = "#2454a6" if gap >= 0 else "#c94343"
        radius = 6 + min(18, math.sqrt(float(row.get("company_count", 1))) / 2)
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{color}" opacity="0.72"/>')
        if abs(gap) >= 4 or row[label_key] in {"Artificial Intelligence & Robotics", "Retail & E-commerce", "Media & Entertainment & Creators Economy"}:
            body.append(f'<text x="{x + radius + 4:.1f}" y="{y + 4:.1f}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#171411">{esc(row[label_key])}</text>')
    return write_svg(filename, svg_shell(title, subtitle, width, height, body))


def lorenz_chart(filename: str, title: str, subtitle: str, speaker_counts: list[int]) -> tuple[str, float]:
    values = sorted(speaker_counts)
    total = sum(values)
    n = len(values)
    cum_pop = [0.0]
    cum_val = [0.0]
    running = 0
    for idx, value in enumerate(values, start=1):
        running += value
        cum_pop.append(idx / n)
        cum_val.append(running / total if total else 0.0)
    gini = 1.0 - sum((cum_val[i] + cum_val[i - 1]) * (cum_pop[i] - cum_pop[i - 1]) for i in range(1, len(cum_pop)))

    width, height = 900, 720
    left, top, size = 100, 120, 500
    points = []
    for x, y in zip(cum_pop, cum_val):
        px = left + x * size
        py = top + size - y * size
        points.append(f"{px:.1f},{py:.1f}")
    body = [
        f'<rect x="{left}" y="{top}" width="{size}" height="{size}" fill="#ffffff" stroke="#ddd4c8"/>',
        f'<line x1="{left}" y1="{top + size}" x2="{left + size}" y2="{top}" stroke="#7f766e" stroke-dasharray="5 5"/>',
        f'<polyline points="{" ".join(points)}" fill="none" stroke="#c94343" stroke-width="5"/>',
        f'<text x="{left}" y="{top + size + 45}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#5f5750">share of exhibitor companies, sorted by matched speakers</text>',
        f'<text x="{left + 18}" y="{top + 28}" font-family="Inter, Arial, sans-serif" font-size="14" fill="#5f5750">share of matched speakers</text>',
        f'<text x="{left + 300}" y="{top + 430}" font-family="Inter, Arial, sans-serif" font-size="46" font-weight="900" fill="#c94343">Gini {gini:.2f}</text>',
        f'<text x="{left + 300}" y="{top + 466}" font-family="Inter, Arial, sans-serif" font-size="15" fill="#5f5750">Includes zero-speaker exhibitors.</text>',
    ]
    return write_svg(filename, svg_shell(title, subtitle, width, height, body)), gini


def heatmap(filename: str, title: str, subtitle: str, rows: list[dict[str, object]], row_key: str, col_key: str, value_key: str) -> str:
    row_labels = list(dict.fromkeys(str(row[row_key]) for row in rows))
    col_labels = list(dict.fromkeys(str(row[col_key]) for row in rows))
    matrix = {(str(row[row_key]), str(row[col_key])): float(row[value_key]) for row in rows}
    cell = 58
    left, top = 310, 145
    width = left + len(col_labels) * cell + 80
    height = top + len(row_labels) * cell + 80
    max_value = max(matrix.values()) if matrix else 1.0
    body: list[str] = []
    for c, label in enumerate(col_labels):
        body.append(f'<text x="{left + c * cell + 30}" y="{top - 14}" transform="rotate(-45 {left + c * cell + 30},{top - 14})" font-family="Inter, Arial, sans-serif" font-size="12" fill="#171411">{esc(label[:24])}</text>')
    for r, label in enumerate(row_labels):
        body.append(f'<text x="40" y="{top + r * cell + 36}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#171411">{esc(label[:34])}</text>')
        for c, col in enumerate(col_labels):
            val = matrix.get((label, col), 0.0)
            alpha = 0.08 + 0.85 * (val / max_value if max_value else 0)
            x = left + c * cell
            y = top + r * cell
            body.append(f'<rect x="{x}" y="{y}" width="{cell - 4}" height="{cell - 4}" fill="#2454a6" opacity="{alpha:.2f}"/>')
            if val:
                body.append(f'<text x="{x + 8}" y="{y + 34}" font-family="Inter, Arial, sans-serif" font-size="12" fill="#171411">{int(val)}</text>')
    return write_svg(filename, svg_shell(title, subtitle, width, height, body))


def main() -> None:
    companies = read_csv("companies_normalized.csv")
    speakers = read_csv("speakers_normalized.csv")
    matches = read_csv("speaker_company_matches.csv")
    coverage = read_csv("company_speaker_coverage.csv")
    tag_rows = read_csv("tag_comparison.csv")
    country_rows = read_csv("country_tension.csv")
    funding_rows = read_csv("fundraising_distribution.csv")
    role_rows = read_csv("role_buckets.csv")
    missing_rows = read_csv("data_quality_missingness.csv")

    company_count = len(companies)
    speaker_count = len(speakers)
    matched_speakers = sum(1 for row in matches if row["matched"] == "True")
    assert company_count == 3153
    assert speaker_count == 1133
    assert matched_speakers == 355

    outputs: list[dict[str, str]] = []

    # 1. Attention funnel by company type.
    type_counts = Counter(row["type"] for row in companies)
    matched_type = Counter(row["company_type"] for row in matches if row["matched"] == "True")
    top_matched_type = Counter(row["company_type"] for row in matches if row["matched"] == "True" and row["top_speaker"] == "True")
    funnel_rows = [
        {"type": "startup", "exhibitors": type_counts["startup"], "matched_speakers": matched_type["startup"], "top_matched_speakers": top_matched_type["startup"]},
        {"type": "partner", "exhibitors": type_counts["partner"], "matched_speakers": matched_type["partner"], "top_matched_speakers": top_matched_type["partner"]},
    ]
    outputs.append({"file": grouped_bar_chart("01_stage_floor_funnel.svg", "Stage-floor funnel by company type", "Exhibitor share and matched-speaker share point in opposite directions.", [
        {"type": "startup", "exhibitor_share": pct(type_counts["startup"], company_count), "speaker_share": pct(matched_type["startup"], matched_speakers)},
        {"type": "partner", "exhibitor_share": pct(type_counts["partner"], company_count), "speaker_share": pct(matched_type["partner"], matched_speakers)},
    ], "type", "exhibitor_share", "speaker_share", "exhibitor share %", "matched speaker share %"), "title": "Stage-floor funnel by company type"})

    # 2. Top billing density.
    outputs.append({"file": bar_chart("02_top_billing_density.svg", "Top billing density per 100 exhibitors", "Partner top-billing density dwarfs startup top-billing density.", [
        {"type": "partner", "density": pct(top_matched_type["partner"], type_counts["partner"])},
        {"type": "startup", "density": pct(top_matched_type["startup"], type_counts["startup"])},
    ], "type", "density", "", "#c94343"), "title": "Top billing density"})

    # 3. Tag scatter.
    scatter_rows = []
    for row in tag_rows:
        scatter_rows.append({
            "tag": row["tag"],
            "company_share": float(row["company_share_pct"]),
            "speaker_share": float(row["speaker_share_pct"]),
            "gap": float(row["speaker_minus_company_share_pp"]),
            "company_count": float(row["company_count"]),
        })
    outputs.append({"file": scatter_chart("03_tag_stage_floor_scatter.svg", "Which topics get stage share?", "Red dots under-index on stage; blue dots over-index.", scatter_rows, "company_share", "speaker_share", "tag"), "title": "Tag stage-floor scatter"})

    # 4. Tag under-index leaderboard.
    under = sorted(scatter_rows, key=lambda row: row["gap"])[:12]
    outputs.append({"file": bar_chart("04_topic_underindex_leaderboard.svg", "Topics most under-amplified on stage", "Negative value means speaker share is lower than exhibitor share.", under, "tag", "gap", " pp", "#c94343"), "title": "Topic under-index leaderboard"})

    # 5. Country leverage.
    country_focus = []
    for row in country_rows:
        companies_n = int(row["companies"])
        if companies_n >= 20:
            country_focus.append({"country": row["country"], "density": float(row["speaker_per_100_companies"]), "companies": companies_n})
    country_focus = sorted(country_focus, key=lambda row: row["density"], reverse=True)[:16]
    outputs.append({"file": bar_chart("05_country_mic_leverage_ranked.svg", "Matched-speaker density by country", "Countries with at least 20 exhibitors, ranked by matched speakers per 100 exhibitors.", country_focus, "country", "density", "", "#18805b"), "title": "Country microphone leverage"})

    # 6. Funding ladder.
    funding_order = {
        "Bootstrapped - 0": 1,
        "Not yet - 0": 2,
        "Pre-Seed - <$1M": 3,
        "Seed - $1M - $5M": 4,
        "Series A - $5M - $15M": 5,
        "Series B - $15M - $50M": 6,
        "Series C - $50M - $200M": 7,
        "Unspecified": 8,
    }
    funding_chart = sorted(
        [{"stage": row["fundraising_stage"], "density": float(row["speaker_per_100_companies"]), "companies": int(row["companies"])} for row in funding_rows],
        key=lambda row: funding_order.get(row["stage"], 99),
    )
    outputs.append({"file": bar_chart("06_funding_maturity_ladder.svg", "Funding maturity ladder", "Matched speakers per 100 companies by funding label.", funding_chart, "stage", "density", "", "#2454a6"), "title": "Funding maturity ladder"})

    # 7. Speaker-role map.
    role_chart = [{"role": row["role_bucket"], "share": float(row["speaker_share_pct"]), "top_rate": float(row["top_speaker_share_in_bucket_pct"])} for row in role_rows]
    outputs.append({"file": grouped_bar_chart("07_role_share_vs_top_rate.svg", "Role mix vs top-billing rate", "Government is small by count but high in top-billing share.", role_chart, "role", "share", "top_rate", "speaker share %", "top share in bucket %"), "title": "Role share vs top billing"})

    # 8. Data quality missingness.
    missing_chart = [{"field": f"{row['dataset']}.{row['field']}", "missing": float(row["missing_pct"])} for row in missing_rows if float(row["missing_pct"]) > 0]
    missing_chart = sorted(missing_chart, key=lambda row: row["missing"], reverse=True)[:12]
    outputs.append({"file": bar_chart("08_missingness_dashboard.svg", "What the public listing hides", "Missing field rates in the company and speaker listing payloads.", missing_chart, "field", "missing", "%", "#7f766e"), "title": "Missingness dashboard"})

    # 9. Attention inequality / Lorenz.
    speaker_count_by_company_id = Counter(row["company_id"] for row in matches if row["matched"] == "True")
    all_company_speaker_counts = [speaker_count_by_company_id.get(row["id"], 0) for row in companies]
    lorenz_file, gini = lorenz_chart("09_attention_lorenz_curve.svg", "Attention inequality across exhibitors", "Most exhibitors have zero matched speakers; a small set absorbs the visible matched-speaker layer.", all_company_speaker_counts)
    outputs.append({"file": lorenz_file, "title": "Attention inequality curve"})

    # 10. Tech for Change vs unlabeled.
    label_counts = Counter(row["label"] or "<blank>" for row in companies)
    company_by_id = {row["id"]: row for row in companies}
    label_speakers = Counter()
    for row in matches:
        if row["matched"] == "True":
            label_speakers[company_by_id[row["company_id"]]["label"] or "<blank>"] += 1
    label_chart = [
        {"label": "<blank>", "density": pct(label_speakers["<blank>"], label_counts["<blank>"])},
        {"label": "techforchange", "density": pct(label_speakers["techforchange"], label_counts["techforchange"])},
    ]
    outputs.append({"file": bar_chart("10_tech_for_change_attention_gap.svg", "Tech for Change attention gap", "Matched speakers per 100 companies by listing label.", label_chart, "label", "density", "", "#c94343"), "title": "Tech for Change attention gap"})

    # 11. Tag pair heatmap.
    top_tags = [row["tag"] for row in sorted(tag_rows, key=lambda row: int(row["company_count"]), reverse=True)[:10]]
    pair_counts = Counter()
    for row in companies:
        tags = set(split_tags(row["tags"]))
        for left, right in itertools.product(top_tags, top_tags):
            if left == right:
                continue
            if left in tags and right in tags:
                pair_counts[(left, right)] += 1
    heat_rows = [{"left": left, "right": right, "count": pair_counts[(left, right)]} for left in top_tags for right in top_tags if left != right]
    outputs.append({"file": heatmap("11_tag_pair_heatmap.svg", "Top tag co-occurrence heatmap", "How often the biggest exhibitor tags appear together.", heat_rows, "left", "right", "count"), "title": "Tag pair heatmap"})

    # 12. Top speaker taglessness.
    top_tagless = Counter((row["top"] == "True", bool(row["tags"].strip())) for row in speakers)
    top_total = top_tagless[(True, False)] + top_tagless[(True, True)]
    non_top_total = top_tagless[(False, False)] + top_tagless[(False, True)]
    tagless_rows = [
        {"bucket": "top speakers", "tagless_pct": pct(top_tagless[(True, False)], top_total)},
        {"bucket": "non-top speakers", "tagless_pct": pct(top_tagless[(False, False)], non_top_total)},
    ]
    outputs.append({"file": bar_chart("12_top_speaker_taglessness.svg", "Top speakers are less classified", "Share of speakers with no public speaker tags.", tagless_rows, "bucket", "tagless_pct", "%", "#2454a6"), "title": "Top speaker taglessness"})

    write_csv_fields = ["file", "title"]
    with (OUT / "visualization_manifest.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=write_csv_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(outputs)

    metrics = {
        "company_count": company_count,
        "speaker_count": speaker_count,
        "matched_speakers": matched_speakers,
        "visualization_count": len(outputs),
        "attention_gini": gini,
        "top_matched_speaker_counts_by_type": dict(top_matched_type),
        "chart_files": [row["file"] for row in outputs],
    }
    (OUT / "more_visualization_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    cards = []
    for row in outputs:
        cards.append(
            f"""
            <section>
              <h2>{esc(row['title'])}</h2>
              <img src="svg/{esc(row['file'])}" alt="{esc(row['title'])}" />
            </section>
            """
        )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>More VivaTech Visualizations</title>
  <style>
    body {{ margin: 0; background: #fbfaf7; color: #171411; font-family: Inter, system-ui, sans-serif; }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    h1 {{ font-size: clamp(2.4rem, 5vw, 5.4rem); line-height: .96; letter-spacing: 0; margin: 0 0 12px; }}
    p {{ color: #5f5750; font-size: 1.08rem; max-width: 900px; }}
    section {{ border-top: 1px solid #ddd4c8; padding: 30px 0; }}
    h2 {{ font-size: clamp(1.5rem, 3vw, 3rem); line-height: 1; letter-spacing: 0; }}
    img {{ width: 100%; height: auto; border: 1px solid #ddd4c8; background: #fbfaf7; }}
  </style>
</head>
<body>
<main>
  <h1>More VivaTech visualizations</h1>
  <p>Additional chart forms from the same validated scrape: 3,153 companies, 1,133 speakers, and 355 matched speakers.</p>
  {''.join(cards)}
</main>
</body>
</html>
"""
    (OUT / "more_visualizations_gallery.html").write_text(html, encoding="utf-8")
    (OUT / "README.md").write_text(
        "# More VivaTech Visualizations\n\n"
        "Generated from the normalized company/speaker CSVs.\n\n"
        "- `more_visualizations_gallery.html`: gallery view.\n"
        "- `svg/`: standalone SVG charts.\n"
        "- `visualization_manifest.csv`: chart index.\n"
        "- `more_visualization_metrics.json`: key validation metrics.\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
