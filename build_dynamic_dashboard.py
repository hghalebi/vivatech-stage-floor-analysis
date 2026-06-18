#!/usr/bin/env python3
"""Build a standalone dynamic VivaTech dashboard and downloadable bundle."""

from __future__ import annotations

import csv
import json
import os
import shutil
import textwrap
import zipfile
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
DASH = BASE / "dynamic_dashboard"
DATA_DIR = DASH / "data"
DOWNLOADS = DASH / "downloads"
ASSETS = DASH / "assets"
TEMPLATES = BASE / "dashboard_templates"
BRAND_ASSETS = BASE / "vivatech_brand_assets"


RAW_CSVS = [
    "companies_normalized.csv",
    "speakers_normalized.csv",
    "speaker_company_matches.csv",
]

DERIVED_CSVS = [
    "company_speaker_coverage.csv",
    "country_tension.csv",
    "coverage_by_type.csv",
    "data_quality_missingness.csv",
    "fundraising_distribution.csv",
    "provocative_patterns.csv",
    "role_buckets.csv",
    "speaker_company_leaders.csv",
    "tag_comparison.csv",
    "polemic_outputs/polemic_claims.csv",
    "polemic_outputs/hall_attention.csv",
    "polemic_outputs/label_attention.csv",
    "polemic_outputs/top_tag_pairs.csv",
    "polemic_outputs/duplicate_company_names.csv",
    "more_visualizations/visualization_manifest.csv",
    "publish_media_kit/claim_evidence_map.csv",
]

JSON_FILES = [
    "summary_metrics.json",
    "polemic_outputs/polemic_metrics.json",
    "more_visualizations/more_visualization_metrics.json",
    "publish_media_kit/media_kit_summary.json",
    "web_enrichment/web_search_summary_official.json",
]

HTML_REPORTS = [
    "vivatech_insights_report.md",
    "viral_visual_report.html",
    "polemic_social_deck.html",
    "more_visualizations/more_visualizations_gallery.html",
    "publish_media_kit/publish_index.html",
    "publish_media_kit/editorial_brief.md",
    "publish_media_kit/x_thread.md",
    "publish_media_kit/linkedin_post.md",
    "web_enrichment_status.md",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def copy_file(src_rel: str, dest_rel: str | None = None) -> str:
    src = BASE / src_rel
    if not src.exists():
        raise FileNotFoundError(src)
    dest = DOWNLOADS / (dest_rel or src_rel)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return str(dest.relative_to(DASH))


def compact_rows(rows: list[dict[str, str]], limit: int, fields: list[str]) -> list[dict[str, str]]:
    return [{field: row.get(field, "") for field in fields} for row in rows[:limit]]


def pct(numerator: float, denominator: float) -> float:
    return numerator / denominator * 100.0 if denominator else 0.0


def dashboard_data() -> dict[str, object]:
    companies = read_csv(BASE / "companies_normalized.csv")
    speakers = read_csv(BASE / "speakers_normalized.csv")
    matches = read_csv(BASE / "speaker_company_matches.csv")
    claims = read_csv(BASE / "polemic_outputs/polemic_claims.csv")
    countries = read_csv(BASE / "country_tension.csv")
    tags = read_csv(BASE / "tag_comparison.csv")
    funding = read_csv(BASE / "fundraising_distribution.csv")
    roles = read_csv(BASE / "role_buckets.csv")
    missingness = read_csv(BASE / "data_quality_missingness.csv")
    coverage = read_csv(BASE / "company_speaker_coverage.csv")
    leaders = read_csv(BASE / "speaker_company_leaders.csv")
    tag_pairs = read_csv(BASE / "polemic_outputs/top_tag_pairs.csv")
    visual_manifest = read_csv(BASE / "more_visualizations/visualization_manifest.csv")
    metrics = json.loads((BASE / "summary_metrics.json").read_text(encoding="utf-8"))
    polemic_metrics = json.loads((BASE / "polemic_outputs/polemic_metrics.json").read_text(encoding="utf-8"))
    more_metrics = json.loads((BASE / "more_visualizations/more_visualization_metrics.json").read_text(encoding="utf-8"))

    type_counts = Counter(row["type"] for row in companies)
    matched_type = Counter(row["company_type"] for row in matches if row["matched"] == "True")
    top_matched_type = Counter(row["company_type"] for row in matches if row["matched"] == "True" and row["top_speaker"] == "True")
    tech_label = read_csv(BASE / "polemic_outputs/label_attention.csv")
    hall_attention = read_csv(BASE / "polemic_outputs/hall_attention.csv")

    conclusion_support = [
        {
            "pattern": "Partner agenda capture",
            "evidence": "Partners are 13.8% of exhibitors but 77.2% of matched speaker slots.",
            "interpretation": "This supports the critique that the speaker layer behaves like a commercial visibility layer rather than a neutral editorial map of the floor.",
            "caveat": "It does not prove that any specific slot was sold.",
        },
        {
            "pattern": "Startup disappearance at top billing",
            "evidence": "Among 20 top-billed speakers matched to exhibitors, 19 map to partners and 1 maps to a startup.",
            "interpretation": "The top stage looks institution-heavy even though startups dominate the exhibitor floor.",
            "caveat": "Unmatched celebrity/government speakers are outside this exhibitor-linked measure.",
        },
        {
            "pattern": "Floor voice gap",
            "evidence": "Only 191 of 3,153 exhibitors have a matched speaker; 93.9% appear voiceless in the matched speaker program.",
            "interpretation": "The event can look like a massive marketplace whose public narrative is shaped by a tiny visible layer.",
            "caveat": "Conservative matching may undercount true links.",
        },
        {
            "pattern": "Tech for Change under-amplification",
            "evidence": "Tech for Change exhibitors have 3.1 matched speakers per 100 companies versus 12.5 for unlabeled exhibitors.",
            "interpretation": "Mission-oriented branding appears weaker at the matched-microphone layer.",
            "caveat": "The label may describe a floor program rather than a stage program.",
        },
        {
            "pattern": "Attention inequality",
            "evidence": f"Attention Gini across exhibitors is {more_metrics['attention_gini']:.3f} when zero-speaker exhibitors are included.",
            "interpretation": "Matched speaker visibility is extremely concentrated.",
            "caveat": "This is about public matched-speaker visibility, not total business value.",
        },
    ]

    recommendation = {
        "title": "Conclusion: treat the stage like editorial, not ad inventory",
        "thesis": (
            "The data does not prove that VivaTech sells stage slots to sponsors. "
            "But it strongly supports a more cautious and provocative critique: the public program behaves like a journal whose reportage is heavily surrounded by advertising logic. "
            "In media terms, the risk is that the stage reads less like independent editorial coverage and more like advertorial programming unless governance changes. "
            "If the stage is selected by partnership-development incentives, the output will naturally over-amplify partners and under-amplify the long-tail floor. "
            "A credible fix would separate stage selection from partnership sales through an independent editorial board, published selection criteria, conflict disclosures, and quotas or explainability for startup, public-interest, and non-sponsor voices."
        ),
        "business_model_change": (
            "The business model should not require selling the microphone as the premium product. "
            "Sell booths, hospitality, private meetings, research products, and sponsor visibility clearly labeled as sponsor visibility. "
            "Keep the main stage governed by editorial criteria so VivaTech can be trusted as a technology forum rather than perceived as advertorial programming."
        ),
        "red_line": "Use this as an evidence-backed governance critique, not an accusation of a specific pay-for-stage transaction.",
        "support": conclusion_support,
    }

    return {
        "generatedAt": "2026-06-17T21:45:00+00:00",
        "metrics": metrics,
        "polemicMetrics": polemic_metrics,
        "moreVisualizationMetrics": more_metrics,
        "recommendation": recommendation,
        "claims": claims,
        "visualizations": visual_manifest,
        "tables": {
            "companies": compact_rows(
                companies,
                3153,
                ["name", "type", "country", "hall", "stand", "label", "tags", "fundraising"],
            ),
            "speakers": compact_rows(
                speakers,
                1133,
                ["full_name", "company", "job_title", "top", "tags", "has_sessions"],
            ),
            "matches": compact_rows(
                matches,
                1133,
                ["speaker_name", "speaker_company", "speaker_job_title", "matched", "company_name", "company_type", "country", "top_speaker"],
            ),
            "countries": countries,
            "tags": tags,
            "funding": funding,
            "roles": roles,
            "missingness": missingness,
            "hallAttention": hall_attention,
            "labelAttention": tech_label,
            "coverage": coverage,
            "leaders": leaders,
            "tagPairs": tag_pairs,
        },
        "derived": {
            "typeCounts": dict(type_counts),
            "matchedTypeCounts": dict(matched_type),
            "topMatchedTypeCounts": dict(top_matched_type),
            "partnerMatchedSpeakerShare": pct(matched_type["partner"], metrics["matched_speakers"]),
            "startupMatchedSpeakerShare": pct(matched_type["startup"], metrics["matched_speakers"]),
            "partnerExhibitorShare": pct(type_counts["partner"], metrics["companies"]),
            "startupExhibitorShare": pct(type_counts["startup"], metrics["companies"]),
        },
    }


def copy_brand_assets() -> None:
    brand_dest = ASSETS / "brand" / "logos"
    brand_dest.mkdir(parents=True, exist_ok=True)
    logo = BRAND_ASSETS / "logos" / "logo-v-black.svg"
    if logo.exists():
        shutil.copy2(logo, brand_dest / logo.name)


def read_template(name: str) -> str:
    path = TEMPLATES / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    if name == "index.html":
        return index_html()
    if name == "dashboard.css":
        return css()
    if name == "dashboard.js":
        return js()
    raise FileNotFoundError(path)


def build_downloads() -> list[dict[str, str]]:
    if DOWNLOADS.exists():
        shutil.rmtree(DOWNLOADS)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, str]] = []

    for rel in RAW_CSVS:
        items.append({"group": "Raw normalized CSV", "label": rel, "href": copy_file(rel)})
    for rel in DERIVED_CSVS:
        items.append({"group": "Derived analysis CSV", "label": rel, "href": copy_file(rel)})
    for rel in JSON_FILES:
        items.append({"group": "JSON summaries", "label": rel, "href": copy_file(rel)})
    for rel in HTML_REPORTS:
        items.append({"group": "Reports and copy", "label": rel, "href": copy_file(rel)})

    for folder in ["viral_outputs", "polemic_outputs", "more_visualizations", "publish_media_kit"]:
        src = BASE / folder
        dest = DOWNLOADS / folder
        if dest.exists():
            shutil.rmtree(dest)
        ignore = shutil.ignore_patterns("__pycache__", ".DS_Store", "previews")
        shutil.copytree(src, dest, ignore=ignore)
        items.append({"group": "Asset folder", "label": folder, "href": str(dest.relative_to(DASH))})

    return items


def js_data(data: dict[str, object], downloads: list[dict[str, str]]) -> str:
    payload = {"data": data, "downloads": downloads}
    return "window.VIVADASH = " + json.dumps(payload, ensure_ascii=False) + ";\n"


def index_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VivaTech Stage vs Floor Dashboard</title>
  <link rel="stylesheet" href="dashboard.css" />
</head>
<body>
  <header class="topbar">
    <div>
      <p class="eyebrow">VivaTech 2026 public listing analysis</p>
      <h1>Is the stage editorial, or advertorial?</h1>
      <p class="lede">A dynamic evidence dashboard for the provocative claim that VivaTech's floor is startup-heavy while its public matched-speaker layer is partner-heavy.</p>
    </div>
    <nav>
      <a href="#claims">Claims</a>
      <a href="#charts">Charts</a>
      <a href="#data">Data</a>
      <a href="#downloads">Downloads</a>
      <a href="#conclusion">Conclusion</a>
    </nav>
  </header>

  <main>
    <section id="overview" class="band">
      <div class="metric-grid" id="metricGrid"></div>
      <div class="thesis-panel">
        <h2>The central pattern</h2>
        <p id="centralThesis"></p>
      </div>
    </section>

    <section id="claims" class="band">
      <div class="section-head">
        <div>
          <p class="eyebrow">Interactive claim explorer</p>
          <h2>Filter the polemic claims</h2>
        </div>
        <div class="filters">
          <label>Minimum controversy <input id="controversyFilter" type="range" min="1" max="5" value="1" /></label>
          <label>Minimum defensibility <input id="defensibilityFilter" type="range" min="1" max="5" value="1" /></label>
          <input id="claimSearch" type="search" placeholder="Search claims, evidence, caveats" />
        </div>
      </div>
      <div class="claim-layout">
        <div id="claimList" class="claim-list"></div>
        <article id="claimDetail" class="claim-detail"></article>
      </div>
    </section>

    <section id="charts" class="band">
      <div class="section-head">
        <div>
          <p class="eyebrow">Dynamic charts</p>
          <h2>Stage, floor, country, funding, and topic gaps</h2>
        </div>
        <select id="chartSelect"></select>
      </div>
      <div id="chartCanvas" class="chart-canvas"></div>
      <div class="svg-gallery" id="svgGallery"></div>
    </section>

    <section id="data" class="band">
      <div class="section-head">
        <div>
          <p class="eyebrow">Data explorer</p>
          <h2>Search the source rows</h2>
        </div>
        <div class="filters">
          <select id="tableSelect">
            <option value="companies">Companies</option>
            <option value="speakers">Speakers</option>
            <option value="matches">Speaker-company matches</option>
            <option value="countries">Countries</option>
            <option value="tags">Tags</option>
            <option value="funding">Funding</option>
          </select>
          <input id="tableSearch" type="search" placeholder="Search table" />
        </div>
      </div>
      <div id="dataTable" class="table-wrap"></div>
    </section>

    <section id="downloads" class="band">
      <div class="section-head">
        <div>
          <p class="eyebrow">Download center</p>
          <h2>Data, charts, reports, and full bundle</h2>
        </div>
        <a class="primary-link" href="vivatech_dashboard_bundle.zip" download>Download full dashboard zip</a>
      </div>
      <div id="downloadList" class="download-list"></div>
    </section>

    <section id="conclusion" class="band conclusion">
      <p class="eyebrow">Conclusion and proposed fix</p>
      <h2 id="conclusionTitle"></h2>
      <p id="conclusionThesis"></p>
      <div id="supportGrid" class="support-grid"></div>
      <div class="business-model">
        <h3>Business-model recommendation</h3>
        <p id="businessModel"></p>
        <p class="redline" id="redLine"></p>
      </div>
    </section>

    <section id="methodology" class="band">
      <p class="eyebrow">Methodology and caveats</p>
      <h2>What this proves, and what it does not</h2>
      <ul>
        <li>Uses a live scrape of public VivaTech speakers and exhibitors.</li>
        <li>Uses conservative organization matching; true links may be undercounted.</li>
        <li>Country labels need normalization before official country rankings.</li>
        <li>Web-search enrichment is partial because available search credentials were unauthorized and public search challenged sustained batches.</li>
        <li>No claim here proves specific sponsorship causality or a specific pay-for-stage transaction.</li>
      </ul>
    </section>
  </main>

  <script src="data/dashboard_data.js"></script>
  <script src="dashboard.js"></script>
</body>
</html>
"""


def css() -> str:
    return """*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fbfaf7;color:#171411;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.45}a{color:inherit}.topbar{padding:28px clamp(18px,4vw,52px);border-bottom:1px solid #ded8cf;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:end;position:sticky;top:0;background:rgba(251,250,247,.94);backdrop-filter:blur(10px);z-index:10}.topbar h1{font-size:clamp(2.4rem,5vw,5.8rem);line-height:.95;letter-spacing:0;margin:0 0 12px;max-width:980px}.lede{font-size:1.1rem;color:#5f5750;max-width:880px;margin:0}.eyebrow{text-transform:uppercase;letter-spacing:.08em;font-weight:900;color:#c94343;font-size:.78rem;margin:0 0 8px}.topbar nav{display:flex;gap:12px;flex-wrap:wrap}.topbar nav a,.primary-link{border:1px solid #171411;padding:8px 12px;text-decoration:none;font-weight:800;background:#fbfaf7}.primary-link{display:inline-block}.band{padding:34px clamp(18px,4vw,52px);border-bottom:1px solid #ded8cf}.metric-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));border:1px solid #ded8cf}.metric{padding:18px;border-right:1px solid #ded8cf}.metric:last-child{border-right:0}.metric strong{font-size:2rem;display:block;line-height:1}.metric span{color:#5f5750}.thesis-panel{margin-top:26px;max-width:980px}.thesis-panel h2,.section-head h2,.conclusion h2,#methodology h2{font-size:clamp(1.8rem,3.5vw,4rem);line-height:1;letter-spacing:0;margin:0 0 12px}.section-head{display:flex;justify-content:space-between;gap:22px;align-items:end;margin-bottom:22px}.filters{display:flex;gap:12px;flex-wrap:wrap;align-items:center}.filters input,.filters select,#chartSelect,#tableSelect{border:1px solid #9f978d;background:#fffdf9;padding:9px 10px;font:inherit;min-height:40px}.claim-layout{display:grid;grid-template-columns:minmax(280px,.36fr) minmax(0,.64fr);gap:22px}.claim-list{display:grid;gap:8px;max-height:720px;overflow:auto;padding-right:4px}.claim-button{text-align:left;border:1px solid #ded8cf;background:#fffdf9;padding:12px;cursor:pointer}.claim-button.active{border-color:#c94343;box-shadow:inset 4px 0 0 #c94343}.claim-button strong{display:block}.claim-button small{color:#5f5750}.claim-detail{border:1px solid #ded8cf;background:#fffdf9;padding:20px;min-height:420px}.claim-detail img{width:min(420px,100%);border:1px solid #ded8cf;display:block;margin:16px 0}.score{color:#2454a6;font-weight:900}.chart-canvas{border:1px solid #ded8cf;background:#fffdf9;padding:16px;min-height:480px;overflow:auto}.chart-canvas svg{width:100%;height:auto}.svg-gallery{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:18px}.svg-card{border:1px solid #ded8cf;background:#fffdf9;padding:10px}.svg-card img{width:100%;display:block}.svg-card a{font-weight:800;text-decoration:none}.table-wrap{border:1px solid #ded8cf;overflow:auto;max-height:650px;background:#fffdf9}.table-wrap table{width:100%;border-collapse:collapse;font-size:.9rem}.table-wrap th,.table-wrap td{border-bottom:1px solid #eee8de;padding:8px 10px;text-align:left;vertical-align:top}.table-wrap th{position:sticky;top:0;background:#ede7dc;z-index:1}.download-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.download-group{border:1px solid #ded8cf;background:#fffdf9;padding:14px}.download-group h3{margin:0 0 10px}.download-group a{display:block;padding:5px 0;color:#2454a6;overflow-wrap:anywhere}.support-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:20px}.support-card,.business-model{border:1px solid #ded8cf;background:#fffdf9;padding:16px}.support-card h3{margin:0 0 8px}.support-card p,.business-model p,#methodology li{color:#5f5750}.redline{border-left:4px solid #c94343;padding-left:12px;color:#171411!important;font-weight:800}.bar-label{font-size:12px;fill:#171411}.axis-label{font-size:12px;fill:#5f5750}@media(max-width:980px){.topbar{position:static;grid-template-columns:1fr}.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.claim-layout{grid-template-columns:1fr}.download-list,.svg-gallery,.support-grid{grid-template-columns:1fr}.section-head{display:block}.filters{margin-top:14px}.metric{border-bottom:1px solid #ded8cf}.metric:nth-child(even){border-right:0}}@media(max-width:560px){.metric-grid{grid-template-columns:1fr}.metric{border-right:0}.band{padding:28px 16px}.topbar{padding:24px 16px}}"""


def js() -> str:
    return r"""const {data, downloads} = window.VIVADASH;
const $ = (id) => document.getElementById(id);
const fmt = (n, d=0) => Number(n).toLocaleString(undefined,{maximumFractionDigits:d, minimumFractionDigits:d});
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[ch]));

function initMetrics(){
  const m = data.metrics;
  const cards = [
    ['Companies', m.companies],
    ['Speakers', m.speakers],
    ['Matched speakers', m.matched_speakers],
    ['Companies with matched speaker', m.companies_with_speakers],
    ['Attention Gini', data.moreVisualizationMetrics.attention_gini.toFixed(3)]
  ];
  $('metricGrid').innerHTML = cards.map(([label,value]) => `<div class="metric"><strong>${typeof value==='number'?fmt(value, value<10?3:0):esc(value)}</strong><span>${esc(label)}</span></div>`).join('');
  $('centralThesis').textContent = data.recommendation.thesis;
}

function claimMatches(claim){
  const minC = Number($('controversyFilter').value);
  const minD = Number($('defensibilityFilter').value);
  const q = $('claimSearch').value.trim().toLowerCase();
  const blob = `${claim.headline} ${claim.punchline} ${claim.evidence} ${claim.caveat}`.toLowerCase();
  return Number(claim.controversy) >= minC && Number(claim.defensibility) >= minD && (!q || blob.includes(q));
}

function renderClaims(selectedRank){
  const claims = data.claims.filter(claimMatches);
  $('claimList').innerHTML = claims.map(c => `<button class="claim-button ${c.rank===selectedRank?'active':''}" data-rank="${esc(c.rank)}"><strong>${esc(c.headline)}</strong><small>${esc(c.metric)} · controversy ${esc(c.controversy)}/5 · defensibility ${esc(c.defensibility)}/5</small></button>`).join('');
  const selected = claims.find(c => c.rank===selectedRank) || claims[0] || data.claims[0];
  renderClaimDetail(selected);
  document.querySelectorAll('.claim-button').forEach(btn => btn.addEventListener('click', () => renderClaims(btn.dataset.rank)));
}

function renderClaimDetail(c){
  if(!c){ $('claimDetail').innerHTML = '<p>No claim matches the filters.</p>'; return; }
  $('claimDetail').innerHTML = `<p class="score">${esc(c.metric)} · controversy ${esc(c.controversy)}/5 · defensibility ${esc(c.defensibility)}/5</p>
    <h3>${esc(c.headline)}</h3>
    <p><strong>${esc(c.punchline)}</strong></p>
    <p>${esc(c.evidence)}</p>
    <p><strong>Caveat:</strong> ${esc(c.caveat)}</p>
    <img src="downloads/polemic_outputs/social_cards/${esc(c.card_file)}" alt="${esc(c.headline)}" />
    <a class="primary-link" href="downloads/polemic_outputs/social_cards/${esc(c.card_file)}" download>Download card</a>`;
}

function svg(width, height, body){ return `<svg viewBox="0 0 ${width} ${height}" role="img">${body}</svg>`; }
function barChart(rows, label, value, color='#2454a6', unit=''){
  const w=1100,h=Math.max(420, rows.length*40+100), left=330, top=40, plot=w-left-80;
  const max=Math.max(...rows.map(r=>Number(r[value]))) * 1.1 || 1;
  let body=`<rect width="${w}" height="${h}" fill="#fffdf9"/>`;
  rows.forEach((r,i)=>{ const y=top+i*38; const v=Number(r[value]); const bw=Math.max(1, v/max*plot);
    body+=`<text x="20" y="${y+22}" class="bar-label">${esc(String(r[label]).slice(0,42))}</text><rect x="${left}" y="${y+7}" width="${bw}" height="20" fill="${color}" opacity=".88"/><text x="${left+bw+8}" y="${y+22}" class="bar-label">${fmt(v,1)}${unit}</text>`;
  });
  return svg(w,h,body);
}

function scatterChart(){
  const rows=data.tables.tags.map(r=>({tag:r.tag,x:Number(r.company_share_pct),y:Number(r.speaker_share_pct),gap:Number(r.speaker_minus_company_share_pp),size:Math.sqrt(Number(r.company_count))*1.3}));
  const w=1100,h=650,left=90,top=50,pw=890,ph=500,maxX=Math.max(...rows.map(r=>r.x))*1.1,maxY=Math.max(...rows.map(r=>r.y))*1.15;
  let body=`<rect width="${w}" height="${h}" fill="#fffdf9"/><line x1="${left}" y1="${top+ph}" x2="${left+pw}" y2="${top+ph}" stroke="#7f766e"/><line x1="${left}" y1="${top}" x2="${left}" y2="${top+ph}" stroke="#7f766e"/><text x="${left+pw-160}" y="${top+ph+42}" class="axis-label">exhibitor share %</text><text x="18" y="${top+18}" class="axis-label">speaker share %</text>`;
  rows.forEach(r=>{ const x=left+r.x/maxX*pw, y=top+ph-r.y/maxY*ph, color=r.gap>=0?'#2454a6':'#c94343'; body+=`<circle cx="${x}" cy="${y}" r="${Math.max(5,Math.min(20,r.size))}" fill="${color}" opacity=".72"/>`; if(Math.abs(r.gap)>=4 || r.tag.includes('Artificial') || r.tag.includes('Retail')) body+=`<text x="${x+10}" y="${y+4}" class="bar-label">${esc(r.tag.slice(0,30))}</text>`; });
  return svg(w,h,body);
}

function lorenzChart(){
  return `<div class="inline-note"><strong>Attention Gini ${data.moreVisualizationMetrics.attention_gini.toFixed(3)}</strong>: this uses the generated Lorenz SVG because it is already validated.</div><img src="downloads/more_visualizations/svg/09_attention_lorenz_curve.svg" alt="Attention Lorenz curve" style="width:100%;max-width:900px">`;
}

const charts = {
  typeGap: {label:'Stage-floor funnel by company type', render:()=>barChart([
    {type:'Startup exhibitor share', value:data.derived.startupExhibitorShare},
    {type:'Startup matched speaker share', value:data.derived.startupMatchedSpeakerShare},
    {type:'Partner exhibitor share', value:data.derived.partnerExhibitorShare},
    {type:'Partner matched speaker share', value:data.derived.partnerMatchedSpeakerShare},
  ], 'type', 'value', '#c94343', '%')},
  country: {label:'Country microphone leverage', render:()=>barChart(data.tables.countries.filter(r=>Number(r.companies)>=20).sort((a,b)=>Number(b.speaker_per_100_companies)-Number(a.speaker_per_100_companies)).slice(0,16), 'country', 'speaker_per_100_companies', '#18805b')},
  tags: {label:'Tag over/under-index scatter', render:scatterChart},
  funding: {label:'Funding maturity ladder', render:()=>barChart(data.tables.funding, 'fundraising_stage', 'speaker_per_100_companies', '#2454a6')},
  roles: {label:'Role mix', render:()=>barChart(data.tables.roles, 'role_bucket', 'speaker_share_pct', '#18805b', '%')},
  tagless: {label:'Top speaker taglessness', render:()=>barChart([{bucket:'Top speakers',value:57.4468},{bucket:'Non-top speakers',value:27.8084}], 'bucket', 'value', '#2454a6', '%')},
  inequality: {label:'Attention inequality Lorenz curve', render:lorenzChart},
  tech: {label:'Tech for Change gap', render:()=>barChart(data.tables.labelAttention, 'label', 'matched_speakers_per_100_companies', '#c94343')},
  heatmap: {label:'Tag co-occurrence heatmap', render:()=>`<img src="downloads/more_visualizations/svg/11_tag_pair_heatmap.svg" alt="Tag co-occurrence heatmap" style="width:100%">`},
  missing: {label:'Missingness dashboard', render:()=>barChart(data.tables.missingness.filter(r=>Number(r.missing_pct)>0).sort((a,b)=>Number(b.missing_pct)-Number(a.missing_pct)).slice(0,12).map(r=>({field:`${r.dataset}.${r.field}`,missing_pct:r.missing_pct})), 'field', 'missing_pct', '#7f766e', '%')}
};

function initCharts(){
  $('chartSelect').innerHTML = Object.entries(charts).map(([key,c])=>`<option value="${key}">${esc(c.label)}</option>`).join('');
  $('chartSelect').addEventListener('change', renderSelectedChart);
  renderSelectedChart();
  const svgs = data.visualizations.map(v=>`<div class="svg-card"><img src="downloads/more_visualizations/svg/${esc(v.file)}" alt="${esc(v.title)}"><a href="downloads/more_visualizations/svg/${esc(v.file)}" download>${esc(v.title)}</a></div>`).join('');
  $('svgGallery').innerHTML = svgs;
}
function renderSelectedChart(){ const key=$('chartSelect').value; $('chartCanvas').innerHTML = charts[key].render(); }

function renderTable(){
  const tableName=$('tableSelect').value;
  const q=$('tableSearch').value.trim().toLowerCase();
  const rows=(data.tables[tableName]||[]).filter(row=>!q || Object.values(row).join(' ').toLowerCase().includes(q)).slice(0,400);
  if(!rows.length){ $('dataTable').innerHTML='<p style="padding:16px">No rows match.</p>'; return; }
  const fields=Object.keys(rows[0]);
  $('dataTable').innerHTML=`<table><thead><tr>${fields.map(f=>`<th>${esc(f)}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${fields.map(f=>`<td>${esc(row[f])}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}

function initDownloads(){
  const groups = {};
  downloads.forEach(d=>{ (groups[d.group] ||= []).push(d); });
  $('downloadList').innerHTML = Object.entries(groups).map(([group,items])=>`<div class="download-group"><h3>${esc(group)}</h3>${items.map(i=>`<a href="${esc(i.href)}" download>${esc(i.label)}</a>`).join('')}</div>`).join('');
}

function initConclusion(){
  const r=data.recommendation;
  $('conclusionTitle').textContent=r.title;
  $('conclusionThesis').textContent=r.thesis;
  $('businessModel').textContent=r.business_model_change;
  $('redLine').textContent=r.red_line;
  $('supportGrid').innerHTML=r.support.map(s=>`<article class="support-card"><h3>${esc(s.pattern)}</h3><p><strong>Evidence:</strong> ${esc(s.evidence)}</p><p><strong>Interpretation:</strong> ${esc(s.interpretation)}</p><p><strong>Caveat:</strong> ${esc(s.caveat)}</p></article>`).join('');
}

function boot(){
  initMetrics();
  renderClaims(data.claims[0]?.rank);
  ['controversyFilter','defensibilityFilter','claimSearch'].forEach(id=>$(id).addEventListener('input',()=>renderClaims(data.claims[0]?.rank)));
  initCharts();
  $('tableSelect').addEventListener('change', renderTable);
  $('tableSearch').addEventListener('input', renderTable);
  renderTable();
  initDownloads();
  initConclusion();
}
boot();"""


def create_zip() -> Path:
    zip_path = DASH / "vivatech_dashboard_bundle.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in DASH.rglob("*"):
            if path == zip_path:
                continue
            if path.is_file():
                zf.write(path, path.relative_to(DASH))
    return zip_path


def main() -> None:
    if DASH.exists():
        shutil.rmtree(DASH)
    DATA_DIR.mkdir(parents=True)
    ASSETS.mkdir(parents=True)
    copy_brand_assets()

    downloads = build_downloads()
    data = dashboard_data()
    write_text(DATA_DIR / "dashboard_data.js", js_data(data, downloads))
    write_text(DASH / "index.html", read_template("index.html"))
    write_text(DASH / "dashboard.css", read_template("dashboard.css"))
    write_text(DASH / "dashboard.js", read_template("dashboard.js"))
    write_text(
        DASH / "README.md",
        textwrap.dedent(
            """\
            # VivaTech Dynamic Dashboard

            Open `index.html` in a browser. The dashboard is static and uses embedded JSON data in `data/dashboard_data.js`.

            Sections:
            - Overview metrics
            - Interactive polemic claim explorer
            - Dynamic charts
            - Searchable data tables
            - Download center
            - Editorial-board conclusion and caveats
            """
        ),
    )
    zip_path = create_zip()
    summary = {
        "dashboard_dir": str(DASH),
        "index": str(DASH / "index.html"),
        "zip": str(zip_path),
        "downloads": len(downloads),
        "claims": len(data["claims"]),
        "visualizations": len(data["visualizations"]),
        "companies": data["metrics"]["companies"],
        "speakers": data["metrics"]["speakers"],
        "matched_speakers": data["metrics"]["matched_speakers"],
        "zip_size_bytes": zip_path.stat().st_size,
    }
    write_text(DASH / "dashboard_build_summary.json", json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
