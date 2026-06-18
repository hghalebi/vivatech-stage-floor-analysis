const { data, downloads } = window.VIVADASH;

const $ = (id) => document.getElementById(id);
const fmt = (n, d = 0) => {
  const value = Number(n);
  if (!Number.isFinite(value)) return "0";
  return value.toLocaleString(undefined, { maximumFractionDigits: d, minimumFractionDigits: d });
};
const num = (v) => {
  const value = Number.parseFloat(String(v ?? "").replace("%", ""));
  return Number.isFinite(value) ? value : 0;
};
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (ch) => ({
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  "\"": "&quot;",
  "'": "&#039;",
}[ch]));

const state = {
  activeClaimRank: data.claims[0]?.rank,
  chartKey: "typeGap",
  chartSort: "desc",
  chartLimit: "12",
  chartMetric: "share",
  chartLabels: true,
  selectedPointKey: null,
};

let activePoints = [];

function claimTopic(claim) {
  const blob = `${claim.headline} ${claim.punchline} ${claim.evidence}`.toLowerCase();
  if (blob.includes("partner") || blob.includes("sponsor")) return "partner power";
  if (blob.includes("startup")) return "startup gap";
  if (blob.includes("country") || blob.includes("france") || blob.includes("united states")) return "country leverage";
  if (blob.includes("funding") || blob.includes("series")) return "funding";
  if (blob.includes("tag") || blob.includes("ai") || blob.includes("tech for change")) return "topics";
  if (blob.includes("gini") || blob.includes("attention")) return "attention inequality";
  return "program governance";
}

function initMetrics() {
  const m = data.metrics;
  const cards = [
    ["Companies", m.companies],
    ["Speakers", m.speakers],
    ["Matched speakers", m.matched_speakers],
    ["Matched companies", m.companies_with_speakers],
    ["Attention Gini", data.moreVisualizationMetrics.attention_gini.toFixed(3)],
  ];
  $("metricGrid").innerHTML = cards.map(([label, value]) => `
    <div class="metric">
      <strong>${typeof value === "number" ? fmt(value, value < 10 ? 3 : 0) : esc(value)}</strong>
      <span>${esc(label)}</span>
    </div>
  `).join("");
  $("centralThesis").textContent = data.recommendation.thesis;
}

function initClaimTopics() {
  const topics = ["all topics", ...Array.from(new Set(data.claims.map(claimTopic))).sort()];
  $("claimTopic").innerHTML = topics.map((topic) => `<option value="${esc(topic)}">${esc(topic)}</option>`).join("");
}

function claimMatches(claim) {
  const minC = Number($("controversyFilter").value);
  const minD = Number($("defensibilityFilter").value);
  const topic = $("claimTopic").value;
  const q = $("claimSearch").value.trim().toLowerCase();
  const blob = `${claim.headline} ${claim.punchline} ${claim.evidence} ${claim.caveat}`.toLowerCase();
  return Number(claim.controversy) >= minC
    && Number(claim.defensibility) >= minD
    && (topic === "all topics" || claimTopic(claim) === topic)
    && (!q || blob.includes(q));
}

function renderClaims(selectedRank = state.activeClaimRank) {
  const claims = data.claims.filter(claimMatches);
  const selected = claims.find((claim) => claim.rank === selectedRank) || claims[0] || null;
  state.activeClaimRank = selected?.rank;
  $("claimList").innerHTML = claims.length
    ? claims.map((claim) => `
      <button class="claim-button ${claim.rank === state.activeClaimRank ? "active" : ""}" data-rank="${esc(claim.rank)}">
        <strong>${esc(claim.headline)}</strong>
        <small>${esc(claimTopic(claim))} / ${esc(claim.metric)} / controversy ${esc(claim.controversy)}/5 / defensibility ${esc(claim.defensibility)}/5</small>
      </button>
    `).join("")
    : `<div class="claim-detail"><p>No claim matches the current filters.</p></div>`;
  renderClaimDetail(selected);
  document.querySelectorAll(".claim-button").forEach((btn) => {
    btn.addEventListener("click", () => renderClaims(btn.dataset.rank));
  });
}

function renderClaimDetail(claim) {
  if (!claim) {
    $("claimDetail").innerHTML = "<p>No claim matches the filters.</p>";
    return;
  }
  $("claimDetail").innerHTML = `
    <p class="score">${esc(claimTopic(claim))} / ${esc(claim.metric)} / controversy ${esc(claim.controversy)}/5 / defensibility ${esc(claim.defensibility)}/5</p>
    <h3>${esc(claim.headline)}</h3>
    <p><strong>${esc(claim.punchline)}</strong></p>
    <p>${esc(claim.evidence)}</p>
    <p><strong>Caveat:</strong> ${esc(claim.caveat)}</p>
    <img src="downloads/polemic_outputs/social_cards/${esc(claim.card_file)}" alt="${esc(claim.headline)}" />
    <a class="primary-link" href="downloads/polemic_outputs/social_cards/${esc(claim.card_file)}" download>Download card</a>
  `;
}

function svg(width, height, body, extra = "") {
  return `<svg viewBox="0 0 ${width} ${height}" role="img" ${extra}>
    <defs>
      <linearGradient id="grad-main" x1="0" x2="1" y1="0" y2="0">
        <stop offset="0%" stop-color="#f7d700" />
        <stop offset="51%" stop-color="#ff5900" />
        <stop offset="100%" stop-color="#f5255d" />
      </linearGradient>
      <linearGradient id="grad-startup" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" stop-color="#812fdb" />
        <stop offset="100%" stop-color="#c51180" />
      </linearGradient>
      <linearGradient id="grad-exhibitor" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" stop-color="#5eb9ca" />
        <stop offset="100%" stop-color="#b6cf20" />
      </linearGradient>
      <linearGradient id="grad-investor" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0%" stop-color="#c5117f" />
        <stop offset="100%" stop-color="#6acce2" />
      </linearGradient>
    </defs>
    ${body}
  </svg>`;
}

function registerPoint(point) {
  const key = `p${activePoints.length}`;
  activePoints.push({ ...point, key });
  return `data-point="${key}" tabindex="0" role="button"`;
}

function metricOption(key, label, unit = "", decimals = 1) {
  return { key, label, unit, decimals };
}

function sortedLimited(rows, valueKey = "value") {
  const sorted = [...rows].sort((a, b) => {
    if (state.chartSort === "name") return String(a.label).localeCompare(String(b.label));
    const diff = num(a[valueKey]) - num(b[valueKey]);
    return state.chartSort === "asc" ? diff : -diff;
  });
  if (state.chartLimit === "all") return sorted;
  return sorted.slice(0, Number(state.chartLimit));
}

function renderBarChart({ title, subtitle, rows, valueKey = "value", unit = "", decimals = 1, source = "Derived CSV" }) {
  const visible = sortedLimited(rows, valueKey);
  const width = 1120;
  const left = 320;
  const top = 102;
  const rowHeight = 46;
  const plotWidth = 690;
  const height = Math.max(430, top + visible.length * rowHeight + 70);
  const max = Math.max(...visible.map((row) => num(row[valueKey])), 1) * 1.08;
  let body = `<rect width="${width}" height="${height}" rx="30" fill="#fff"/>
    <text x="34" y="48" class="chart-title">${esc(title)}</text>
    <text x="34" y="76" class="chart-subtitle">${esc(subtitle)}</text>
    <line x1="${left}" y1="${top - 12}" x2="${left + plotWidth}" y2="${top - 12}" stroke="#e4e4e7"/>`;

  visible.forEach((row, index) => {
    const y = top + index * rowHeight;
    const value = num(row[valueKey]);
    const barWidth = Math.max(2, value / max * plotWidth);
    const fill = row.fill || "url(#grad-main)";
    const pointAttrs = registerPoint({
      label: row.label,
      value,
      valueLabel: `${fmt(value, decimals)}${unit}`,
      meta: row.meta || "",
      source: row.source || source,
      evidence: row.evidence || subtitle,
    });
    const label = String(row.label).slice(0, 38);
    body += `
      <g class="chart-mark" ${pointAttrs}>
        ${state.chartLabels ? `<text x="34" y="${y + 21}" class="bar-label">${esc(label)}</text>` : ""}
        <rect x="${left}" y="${y}" width="${barWidth}" height="26" rx="13" fill="${fill}" opacity=".95">
          <animate attributeName="width" from="0" to="${barWidth}" dur=".45s" fill="freeze" />
        </rect>
        <text x="${Math.min(left + barWidth + 10, width - 92)}" y="${y + 19}" class="bar-label">${fmt(value, decimals)}${esc(unit)}</text>
      </g>`;
  });

  return svg(width, height, body);
}

function renderTypeGap() {
  if (state.chartMetric === "leverage") {
    const rows = [
      {
        label: "Partner microphone leverage",
        value: data.derived.partnerMatchedSpeakerShare / data.derived.partnerExhibitorShare,
        meta: "Matched speaker share divided by exhibitor share.",
        source: "coverage_by_type.csv",
        evidence: "Partners are 13.8% of exhibitors and 77.2% of matched speaker slots.",
      },
      {
        label: "Startup microphone leverage",
        value: data.derived.startupMatchedSpeakerShare / data.derived.startupExhibitorShare,
        meta: "Matched speaker share divided by exhibitor share.",
        source: "coverage_by_type.csv",
        evidence: "Startups are 86.2% of exhibitors and 22.8% of matched speaker slots.",
        fill: "url(#grad-startup)",
      },
    ];
    return renderBarChart({
      title: "Partner/startup microphone leverage",
      subtitle: "Matched speaker share divided by exhibitor-floor share.",
      rows,
      unit: "x",
      decimals: 1,
      source: "coverage_by_type.csv",
    });
  }

  const rows = [
    {
      label: "Startup exhibitor share",
      value: data.derived.startupExhibitorShare,
      fill: "url(#grad-startup)",
      meta: `${fmt(data.derived.typeCounts.startup)} startup exhibitors.`,
      source: "companies_normalized.csv",
    },
    {
      label: "Startup matched speaker share",
      value: data.derived.startupMatchedSpeakerShare,
      fill: "url(#grad-exhibitor)",
      meta: `${fmt(data.derived.matchedTypeCounts.startup)} matched startup speakers.`,
      source: "speaker_company_matches.csv",
    },
    {
      label: "Partner exhibitor share",
      value: data.derived.partnerExhibitorShare,
      fill: "url(#grad-startup)",
      meta: `${fmt(data.derived.typeCounts.partner)} partner exhibitors.`,
      source: "companies_normalized.csv",
    },
    {
      label: "Partner matched speaker share",
      value: data.derived.partnerMatchedSpeakerShare,
      fill: "url(#grad-main)",
      meta: `${fmt(data.derived.matchedTypeCounts.partner)} matched partner speakers.`,
      source: "speaker_company_matches.csv",
    },
  ];
  return renderBarChart({
    title: "Stage vs floor funnel",
    subtitle: "Company type share on the exhibitor floor compared with matched speaker share.",
    rows,
    unit: "%",
    decimals: 1,
    source: "coverage_by_type.csv",
  });
}

function renderCountryChart() {
  const metric = getMetric();
  const rows = data.tables.countries
    .filter((row) => num(row.companies) >= 20)
    .map((row) => ({
      label: row.country,
      value: num(row[metric.key]),
      meta: `${fmt(row.companies)} companies / ${fmt(row.matched_speakers)} matched speakers / ${fmt(row.coverage_pct, 1)}% coverage.`,
      source: "country_tension.csv",
      evidence: "Countries with at least 20 exhibitors, sorted by selected metric.",
    }));
  return renderBarChart({
    title: "Country microphone leverage",
    subtitle: metric.label,
    rows,
    unit: metric.unit,
    decimals: metric.decimals,
    source: "country_tension.csv",
  });
}

function renderFundingChart() {
  const metric = getMetric();
  const rows = data.tables.funding.map((row) => ({
    label: row.fundraising_stage,
    value: num(row[metric.key]),
    meta: `${fmt(row.companies)} companies / ${fmt(row.matched_speakers)} matched speakers.`,
    source: "fundraising_distribution.csv",
  }));
  return renderBarChart({
    title: "Funding maturity ladder",
    subtitle: metric.label,
    rows,
    unit: metric.unit,
    decimals: metric.decimals,
    source: "fundraising_distribution.csv",
  });
}

function renderRoleChart() {
  const metric = getMetric();
  const rows = data.tables.roles.map((row) => ({
    label: row.role_bucket,
    value: num(row[metric.key]),
    meta: `${fmt(row.speakers)} speakers / ${fmt(row.top_speakers)} top speakers.`,
    source: "role_buckets.csv",
  }));
  return renderBarChart({
    title: "Speaker role mix",
    subtitle: metric.label,
    rows,
    unit: metric.unit,
    decimals: metric.decimals,
    source: "role_buckets.csv",
  });
}

function renderTaglessChart() {
  const rows = [
    {
      label: "Top speakers without tags",
      value: 57.4468,
      meta: "Top speaker taglessness rate from derived visualization metrics.",
      source: "more_visualizations/svg/12_top_speaker_taglessness.svg",
    },
    {
      label: "Non-top speakers without tags",
      value: 27.8084,
      meta: "Non-top speaker taglessness rate from derived visualization metrics.",
      source: "more_visualizations/svg/12_top_speaker_taglessness.svg",
      fill: "url(#grad-exhibitor)",
    },
  ];
  return renderBarChart({
    title: "Top-speaker taglessness",
    subtitle: "Top-billed speakers are more often untagged than other speakers.",
    rows,
    unit: "%",
    decimals: 1,
  });
}

function renderTechForChangeChart() {
  const metric = getMetric();
  const rows = data.tables.labelAttention.map((row) => ({
    label: row.label === "<blank>" ? "No Tech for Change label" : row.label,
    value: num(row[metric.key]),
    meta: `${fmt(row.companies)} companies / ${fmt(row.matched_speakers)} matched speakers.`,
    source: "polemic_outputs/label_attention.csv",
  }));
  return renderBarChart({
    title: "Tech for Change gap",
    subtitle: metric.label,
    rows,
    unit: metric.unit,
    decimals: metric.decimals,
    source: "polemic_outputs/label_attention.csv",
  });
}

function renderMissingChart() {
  const rows = data.tables.missingness
    .filter((row) => num(row.missing_pct) > 0)
    .map((row) => ({
      label: `${row.dataset}.${row.field}`,
      value: num(row.missing_pct),
      meta: `${fmt(row.missing_count)} missing of ${fmt(row.rows)} rows.`,
      source: "data_quality_missingness.csv",
      fill: "url(#grad-investor)",
    }));
  return renderBarChart({
    title: "Data missingness",
    subtitle: "Missing percentage by dataset field.",
    rows,
    unit: "%",
    decimals: 1,
    source: "data_quality_missingness.csv",
  });
}

function renderLeaderChart() {
  const metric = getMetric();
  const rows = data.tables.leaders.map((row) => ({
    label: row.speaker_company,
    value: num(row[metric.key]),
    meta: `${row.exhibitor_match === "True" ? "Matched" : "Unmatched"} / ${row.matched_company_type || "no exhibitor type"} / ${row.matched_country || "no country"}.`,
    source: "speaker_company_leaders.csv",
    evidence: "Top visible speaker organizations by public speaker count.",
  }));
  return renderBarChart({
    title: "Who owns the speaker list?",
    subtitle: metric.label,
    rows,
    unit: metric.unit,
    decimals: metric.decimals,
    source: "speaker_company_leaders.csv",
  });
}

function renderScatterChart() {
  const metric = getMetric();
  const rows = sortedLimited(data.tables.tags.map((row) => {
    if (metric.key === "rate") {
      return {
        label: row.tag,
        x: num(row.company_count),
        y: num(row.speaker_per_100_tagged_companies),
        size: Math.max(6, Math.sqrt(num(row.speaker_count)) * 2.4),
        value: num(row.speaker_per_100_tagged_companies),
        gap: num(row.speaker_minus_company_share_pp),
        meta: `${fmt(row.company_count)} companies / ${fmt(row.speaker_count)} speakers.`,
        source: "tag_comparison.csv",
      };
    }
    if (metric.key === "volume") {
      return {
        label: row.tag,
        x: num(row.company_count),
        y: num(row.speaker_count),
        size: Math.max(6, Math.sqrt(num(row.company_count)) * 1.2),
        value: num(row.speaker_count),
        gap: num(row.speaker_minus_company_share_pp),
        meta: `${fmt(row.company_count)} companies / ${fmt(row.speaker_count)} speakers.`,
        source: "tag_comparison.csv",
      };
    }
    return {
      label: row.tag,
      x: num(row.company_share_pct),
      y: num(row.speaker_share_pct),
      size: Math.max(6, Math.sqrt(num(row.company_count)) * 1.15),
      value: Math.abs(num(row.speaker_minus_company_share_pp)),
      gap: num(row.speaker_minus_company_share_pp),
      meta: `${fmt(row.company_share_pct, 1)}% company share / ${fmt(row.speaker_share_pct, 1)}% speaker share.`,
      source: "tag_comparison.csv",
    };
  }), "value");

  const width = 1120;
  const height = 660;
  const left = 100;
  const top = 96;
  const plotWidth = 860;
  const plotHeight = 470;
  const maxX = Math.max(...rows.map((row) => row.x), 1) * 1.12;
  const maxY = Math.max(...rows.map((row) => row.y), 1) * 1.16;
  const xLabel = metric.key === "gap" ? "exhibitor share %" : "company count";
  const yLabel = metric.key === "gap" ? "speaker share %" : metric.label;
  let body = `<rect width="${width}" height="${height}" rx="30" fill="#fff"/>
    <text x="34" y="48" class="chart-title">Tag over/under-index scatter</text>
    <text x="34" y="76" class="chart-subtitle">${esc(metric.label)}</text>
    <line x1="${left}" y1="${top + plotHeight}" x2="${left + plotWidth}" y2="${top + plotHeight}" stroke="#d4d4d8"/>
    <line x1="${left}" y1="${top}" x2="${left}" y2="${top + plotHeight}" stroke="#d4d4d8"/>
    <text x="${left + plotWidth - 150}" y="${top + plotHeight + 42}" class="axis-label">${esc(xLabel)}</text>
    <text x="34" y="${top + 16}" class="axis-label">${esc(yLabel)}</text>`;

  if (metric.key === "gap") {
    body += `<line x1="${left}" y1="${top + plotHeight}" x2="${left + plotWidth}" y2="${top}" stroke="#222" stroke-dasharray="5 6" opacity=".35"/>`;
  }

  rows.forEach((row) => {
    const x = left + row.x / maxX * plotWidth;
    const y = top + plotHeight - row.y / maxY * plotHeight;
    const fill = row.gap >= 0 ? "url(#grad-main)" : "url(#grad-startup)";
    const pointAttrs = registerPoint({
      label: row.label,
      value: row.value,
      valueLabel: metric.key === "gap" ? `${fmt(row.gap, 1)} pp` : fmt(row.value, 1),
      meta: row.meta,
      source: row.source,
      evidence: "Tags above the diagonal are over-represented in speaker share; below are under-represented.",
    });
    body += `<g class="chart-mark" ${pointAttrs}>
      <circle cx="${x}" cy="${y}" r="${Math.min(24, row.size)}" fill="${fill}" opacity=".82">
        <animate attributeName="r" from="0" to="${Math.min(24, row.size)}" dur=".45s" fill="freeze" />
      </circle>
      ${state.chartLabels && (Math.abs(row.gap) >= 6 || row.value >= 20)
        ? `<text x="${x + 10}" y="${y + 4}" class="point-label">${esc(String(row.label).slice(0, 30))}</text>`
        : ""}
    </g>`;
  });
  return svg(width, height, body);
}

function renderLorenzChart() {
  const coverageByCompany = new Map(data.tables.coverage.map((row) => [row.company_name, num(row.speaker_count)]));
  const counts = data.tables.companies.map((row) => coverageByCompany.get(row.name) || 0).sort((a, b) => a - b);
  const total = counts.reduce((sum, value) => sum + value, 0) || 1;
  const width = 1120;
  const height = 620;
  const left = 95;
  const top = 92;
  const plot = 460;
  let cumulative = 0;
  const points = [[left, top + plot]];
  counts.forEach((value, index) => {
    cumulative += value;
    points.push([
      left + ((index + 1) / counts.length) * plot,
      top + plot - (cumulative / total) * plot,
    ]);
  });
  const path = points.map(([x, y], index) => `${index ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`).join(" ");
  const zeroSpeaker = counts.filter((value) => value === 0).length;
  const pointAttrs = registerPoint({
    label: "Attention inequality",
    value: data.moreVisualizationMetrics.attention_gini,
    valueLabel: `Gini ${data.moreVisualizationMetrics.attention_gini.toFixed(3)}`,
    meta: `${fmt(zeroSpeaker)} of ${fmt(counts.length)} exhibitors have zero matched speakers.`,
    source: "company_speaker_coverage.csv",
    evidence: "Lorenz curve includes zero-speaker exhibitors.",
  });
  const body = `<rect width="${width}" height="${height}" rx="30" fill="#fff"/>
    <text x="34" y="48" class="chart-title">Attention inequality Lorenz curve</text>
    <text x="34" y="76" class="chart-subtitle">Cumulative matched-speaker attention across all exhibitors.</text>
    <line x1="${left}" y1="${top + plot}" x2="${left + plot}" y2="${top + plot}" stroke="#d4d4d8"/>
    <line x1="${left}" y1="${top}" x2="${left}" y2="${top + plot}" stroke="#d4d4d8"/>
    <line x1="${left}" y1="${top + plot}" x2="${left + plot}" y2="${top}" stroke="#111" stroke-dasharray="6 6" opacity=".35"/>
    <g class="chart-mark" ${pointAttrs}>
      <path d="${path}" fill="none" stroke="url(#grad-main)" stroke-width="6" stroke-linecap="round"/>
      <circle cx="${left + plot}" cy="${top}" r="7" fill="#fd0a71"/>
    </g>
    <text x="${left}" y="${top + plot + 42}" class="axis-label">cumulative exhibitors</text>
    <text x="${left + plot + 42}" y="${top + 18}" class="bar-label">Gini ${data.moreVisualizationMetrics.attention_gini.toFixed(3)}</text>
    <text x="${left + plot + 42}" y="${top + 48}" class="axis-label">${fmt(zeroSpeaker)} zero-speaker exhibitors</text>`;
  return svg(width, height, body);
}

function renderHeatmap() {
  const visiblePairs = sortedLimited(data.tables.tagPairs.map((row) => ({
    label: `${row.left_tag} / ${row.right_tag}`,
    value: num(row.company_count),
    left: row.left_tag,
    right: row.right_tag,
    meta: `${fmt(row.company_count)} companies share both tags.`,
    source: "polemic_outputs/top_tag_pairs.csv",
  })), "value");
  const tags = Array.from(new Set(visiblePairs.flatMap((row) => [row.left, row.right]))).slice(0, 12);
  const valueByPair = new Map();
  visiblePairs.forEach((row) => {
    valueByPair.set(`${row.left}|||${row.right}`, row);
    valueByPair.set(`${row.right}|||${row.left}`, row);
  });
  const max = Math.max(...visiblePairs.map((row) => row.value), 1);
  const cell = 48;
  const width = 1120;
  const top = 140;
  const left = 320;
  const height = top + tags.length * cell + 90;
  let body = `<rect width="${width}" height="${height}" rx="30" fill="#fff"/>
    <text x="34" y="48" class="chart-title">Tag co-occurrence heatmap</text>
    <text x="34" y="76" class="chart-subtitle">Top tag pairs by exhibitor co-occurrence.</text>`;
  tags.forEach((tag, index) => {
    body += `<text x="${left + index * cell + 22}" y="${top - 12}" class="axis-label" transform="rotate(-45 ${left + index * cell + 22} ${top - 12})">${esc(tag.slice(0, 16))}</text>`;
    body += `<text x="34" y="${top + index * cell + 30}" class="axis-label">${esc(tag.slice(0, 32))}</text>`;
  });
  tags.forEach((leftTag, yIndex) => {
    tags.forEach((rightTag, xIndex) => {
      const pair = valueByPair.get(`${leftTag}|||${rightTag}`);
      const value = pair?.value || 0;
      const opacity = value ? 0.18 + (value / max) * 0.82 : 0.04;
      const pointAttrs = pair ? registerPoint({
        label: pair.label,
        value: pair.value,
        valueLabel: fmt(pair.value),
        meta: pair.meta,
        source: pair.source,
        evidence: "Co-occurrence count among exhibitor tags.",
      }) : "";
      body += `<rect class="chart-mark" ${pointAttrs} x="${left + xIndex * cell}" y="${top + yIndex * cell}" width="${cell - 4}" height="${cell - 4}" rx="10" fill="#fd0a71" opacity="${opacity}"/>`;
    });
  });
  return svg(width, height, body);
}

const chartSpecs = {
  typeGap: {
    label: "Stage/floor funnel",
    summary: "Compare exhibitor-floor share with matched speaker share by company type.",
    metrics: [metricOption("share", "Share comparison", "%"), metricOption("leverage", "Microphone leverage", "x")],
    render: renderTypeGap,
  },
  country: {
    label: "Country leverage",
    summary: "Rank countries by microphone leverage, coverage, or speaker volume.",
    metrics: [
      metricOption("speaker_per_100_companies", "Matched speakers per 100 companies", "", 1),
      metricOption("coverage_pct", "Companies with matched speakers %", "%", 1),
      metricOption("matched_speakers", "Matched speakers", "", 0),
      metricOption("no_speaker_companies", "No-speaker companies", "", 0),
    ],
    render: renderCountryChart,
  },
  tags: {
    label: "Topic scatter",
    summary: "Find tags that are over or under represented in the public matched-speaker layer.",
    metrics: [
      metricOption("gap", "Speaker share vs exhibitor share", " pp", 1),
      metricOption("rate", "Speakers per 100 tagged companies", "", 1),
      metricOption("volume", "Speaker count vs company count", "", 0),
    ],
    render: renderScatterChart,
  },
  funding: {
    label: "Funding ladder",
    summary: "Compare matched microphone odds across funding maturity labels.",
    metrics: [
      metricOption("speaker_per_100_companies", "Matched speakers per 100 companies", "", 1),
      metricOption("company_share_pct", "Company share", "%", 1),
      metricOption("matched_speakers", "Matched speakers", "", 0),
    ],
    render: renderFundingChart,
  },
  roles: {
    label: "Role mix",
    summary: "Measure which job-role buckets dominate the speaker list.",
    metrics: [
      metricOption("speaker_share_pct", "Speaker share", "%", 1),
      metricOption("top_speaker_share_in_bucket_pct", "Top-speaker share inside role", "%", 1),
      metricOption("speakers", "Speakers", "", 0),
    ],
    render: renderRoleChart,
  },
  leaders: {
    label: "Speaker orgs",
    summary: "Rank organizations by raw public speaker count.",
    metrics: [metricOption("speaker_count", "Speaker count", "", 0), metricOption("speaker_share", "Speaker share", "", 3)],
    render: renderLeaderChart,
  },
  tagless: {
    label: "Taglessness",
    summary: "Compare tag coverage for top-billed versus non-top speakers.",
    metrics: [metricOption("value", "Tagless speaker share", "%", 1)],
    render: renderTaglessChart,
  },
  inequality: {
    label: "Lorenz curve",
    summary: "Show how concentrated matched-speaker attention is across exhibitors.",
    metrics: [metricOption("gini", "Attention Gini", "", 3)],
    render: renderLorenzChart,
  },
  tech: {
    label: "Tech for Change",
    summary: "Compare mission-label coverage with the rest of the floor.",
    metrics: [
      metricOption("matched_speakers_per_100_companies", "Matched speakers per 100 companies", "", 1),
      metricOption("coverage_pct", "Coverage", "%", 1),
      metricOption("matched_speakers", "Matched speakers", "", 0),
    ],
    render: renderTechForChangeChart,
  },
  heatmap: {
    label: "Tag heatmap",
    summary: "Explore co-occurring exhibitor tags.",
    metrics: [metricOption("company_count", "Company count", "", 0)],
    render: renderHeatmap,
  },
  missing: {
    label: "Missingness",
    summary: "Audit source fields with missing values.",
    metrics: [metricOption("missing_pct", "Missing percentage", "%", 1), metricOption("missing_count", "Missing rows", "", 0)],
    render: renderMissingChart,
  },
};

function getMetric() {
  const spec = chartSpecs[state.chartKey];
  return spec.metrics.find((metric) => metric.key === state.chartMetric) || spec.metrics[0];
}

function initChartTabs() {
  $("chartTabs").innerHTML = Object.entries(chartSpecs).map(([key, spec]) => `
    <button class="chart-tab ${key === state.chartKey ? "active" : ""}" type="button" role="tab" aria-selected="${key === state.chartKey}" data-chart="${key}">
      ${esc(spec.label)}
    </button>
  `).join("");
  document.querySelectorAll(".chart-tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.chartKey = button.dataset.chart;
      state.chartMetric = chartSpecs[state.chartKey].metrics[0].key;
      state.chartSort = "desc";
      state.chartLimit = "12";
      state.selectedPointKey = null;
      renderCharts();
    });
  });
}

function initMetricSelect() {
  const spec = chartSpecs[state.chartKey];
  $("chartMetric").innerHTML = spec.metrics.map((metric) => `<option value="${esc(metric.key)}">${esc(metric.label)}</option>`).join("");
  $("chartMetric").value = state.chartMetric;
}

function renderCharts() {
  activePoints = [];
  initChartTabs();
  initMetricSelect();
  $("chartSort").value = state.chartSort;
  $("chartLimit").value = state.chartLimit;
  $("chartLabels").checked = state.chartLabels;
  $("chartCanvas").innerHTML = chartSpecs[state.chartKey].render();
  bindChartEvents();
  renderChartInsight();
}

function renderChartInsight(point = null) {
  const spec = chartSpecs[state.chartKey];
  const selected = point || activePoints.find((item) => item.key === state.selectedPointKey) || activePoints[0];
  $("chartInsight").innerHTML = `
    <h3>${esc(selected?.label || spec.label)}</h3>
    <p>${esc(selected?.evidence || spec.summary)}</p>
    <div class="statline">
      <span>${esc(selected?.valueLabel || getMetric().label)}</span>
      <span>${esc(selected?.meta || "Click or hover a mark to inspect its evidence.")}</span>
      <span>Source: ${esc(selected?.source || "dashboard_data.js")}</span>
    </div>
  `;
}

function bindChartEvents() {
  const tooltip = $("chartTooltip");
  $("chartCanvas").querySelectorAll("[data-point]").forEach((node) => {
    const getPoint = () => activePoints.find((item) => item.key === node.dataset.point);
    node.addEventListener("mousemove", (event) => {
      const point = getPoint();
      if (!point) return;
      tooltip.hidden = false;
      tooltip.style.left = `${event.offsetX + 18}px`;
      tooltip.style.top = `${event.offsetY + 18}px`;
      tooltip.innerHTML = `<strong>${esc(point.label)}</strong><br>${esc(point.valueLabel)}<br>${esc(point.meta)}`;
    });
    node.addEventListener("mouseleave", () => {
      tooltip.hidden = true;
    });
    node.addEventListener("click", () => {
      const point = getPoint();
      state.selectedPointKey = point?.key || null;
      renderChartInsight(point);
    });
    node.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      const point = getPoint();
      state.selectedPointKey = point?.key || null;
      renderChartInsight(point);
    });
  });
}

function exportCurrentSvg() {
  const svgNode = $("chartCanvas").querySelector("svg");
  if (!svgNode) return;
  const source = `<?xml version="1.0" encoding="UTF-8"?>\n${new XMLSerializer().serializeToString(svgNode)}`;
  const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `vivatech_${state.chartKey}_${state.chartMetric}.svg`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function initCharts() {
  $("chartSort").addEventListener("change", (event) => {
    state.chartSort = event.target.value;
    state.selectedPointKey = null;
    renderCharts();
  });
  $("chartLimit").addEventListener("change", (event) => {
    state.chartLimit = event.target.value;
    state.selectedPointKey = null;
    renderCharts();
  });
  $("chartMetric").addEventListener("change", (event) => {
    state.chartMetric = event.target.value;
    state.selectedPointKey = null;
    renderCharts();
  });
  $("chartLabels").addEventListener("change", (event) => {
    state.chartLabels = event.target.checked;
    renderCharts();
  });
  $("exportChart").addEventListener("click", exportCurrentSvg);
  renderCharts();
  $("svgGallery").innerHTML = data.visualizations.map((viz) => `
    <div class="svg-card">
      <img src="downloads/more_visualizations/svg/${esc(viz.file)}" alt="${esc(viz.title)}">
      <a href="downloads/more_visualizations/svg/${esc(viz.file)}" download>${esc(viz.title)}</a>
    </div>
  `).join("");
}

function renderTable() {
  const tableName = $("tableSelect").value;
  const q = $("tableSearch").value.trim().toLowerCase();
  const allRows = data.tables[tableName] || [];
  const matchedRows = allRows.filter((row) => !q || Object.values(row).join(" ").toLowerCase().includes(q));
  const rows = matchedRows.slice(0, 400);
  $("dataTableMeta").textContent = `${fmt(matchedRows.length)} matching rows / ${fmt(allRows.length)} total. Showing up to 400 rows.`;
  if (!rows.length) {
    $("dataTable").innerHTML = "<p style=\"padding:16px\">No rows match.</p>";
    return;
  }
  const fields = Object.keys(rows[0]);
  $("dataTable").innerHTML = `
    <table>
      <thead><tr>${fields.map((field) => `<th>${esc(field)}</th>`).join("")}</tr></thead>
      <tbody>${rows.map((row) => `<tr>${fields.map((field) => `<td>${esc(row[field])}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  `;
}

function initDownloads() {
  const groups = {};
  downloads.forEach((item) => {
    (groups[item.group] ||= []).push(item);
  });
  $("downloadList").innerHTML = Object.entries(groups).map(([group, items]) => `
    <div class="download-group">
      <h3>${esc(group)}</h3>
      ${items.map((item) => `<a href="${esc(item.href)}" download>${esc(item.label)}</a>`).join("")}
    </div>
  `).join("");
}

function initConclusion() {
  const recommendation = data.recommendation;
  $("conclusionTitle").textContent = recommendation.title;
  $("conclusionThesis").textContent = recommendation.thesis;
  $("businessModel").textContent = recommendation.business_model_change;
  $("redLine").textContent = recommendation.red_line;
  $("supportGrid").innerHTML = recommendation.support.map((support) => `
    <article class="support-card">
      <h3>${esc(support.pattern)}</h3>
      <p><strong>Evidence:</strong> ${esc(support.evidence)}</p>
      <p><strong>Interpretation:</strong> ${esc(support.interpretation)}</p>
      <p><strong>Caveat:</strong> ${esc(support.caveat)}</p>
    </article>
  `).join("");
}

function restoreHashScroll() {
  if (!window.location.hash) return;
  const target = document.querySelector(window.location.hash);
  if (!target) return;
  requestAnimationFrame(() => {
    const header = document.querySelector(".vt-header");
    const headerOffset = window.matchMedia("(max-width: 820px)").matches ? 0 : (header?.offsetHeight || 0);
    const top = target.getBoundingClientRect().top + window.scrollY - headerOffset;
    window.scrollTo({ top, behavior: "auto" });
  });
}

function boot() {
  initMetrics();
  initClaimTopics();
  renderClaims();
  ["controversyFilter", "defensibilityFilter", "claimSearch", "claimTopic"].forEach((id) => {
    $(id).addEventListener("input", () => {
      state.activeClaimRank = null;
      renderClaims();
    });
  });
  initCharts();
  $("tableSelect").addEventListener("change", renderTable);
  $("tableSearch").addEventListener("input", renderTable);
  renderTable();
  initDownloads();
  initConclusion();
  restoreHashScroll();
  window.addEventListener("load", restoreHashScroll, { once: true });
  window.setTimeout(restoreHashScroll, 350);
}

boot();
