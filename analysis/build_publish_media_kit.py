#!/usr/bin/env python3
"""Build a publish-ready media kit from the VivaTech claim bank."""

from __future__ import annotations

import csv
import json
import textwrap
from pathlib import Path


BASE = Path(__file__).resolve().parent
OUT = BASE / "publish_media_kit"
OUT.mkdir(exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def short_post(claim: dict[str, str]) -> str:
    headline = claim["headline"].rstrip(".")
    evidence = claim["evidence"].rstrip(".")
    caveat = claim["caveat"].rstrip(".")
    return f"{headline}.\n\n{evidence}.\n\nImportant caveat: {caveat}."


def punchy_caption(claim: dict[str, str]) -> str:
    return f"{claim['metric']} | {claim['headline']} {claim['punchline']}"


def thread(posts: list[str]) -> str:
    lines = [
        "# X Thread Draft",
        "",
        "1/ VivaTech's viral story is not just AI. It is who gets the microphone.",
        "",
        "I scraped 3,153 exhibitor companies and 1,133 speaker records, then matched speaker organizations back to exhibitors with conservative alias rules.",
        "",
    ]
    for idx, post in enumerate(posts, start=2):
        body = post.replace("\n\n", " ")
        lines.append(f"{idx}/ {body}")
        lines.append("")
    lines.append("Final caveat: these are public-listing signals, not internal sponsorship or curation data. The strongest claim is structural: the floor is startup-heavy, but the matched microphone layer is partner-heavy.")
    return "\n".join(lines)


def linkedin_post(top_claims: list[dict[str, str]]) -> str:
    bullets = "\n".join(
        f"- {claim['headline']} {claim['evidence']}" for claim in top_claims[:6]
    )
    return f"""# LinkedIn Draft

VivaTech looks like a startup marketplace from the floor.

The speaker data tells a more uncomfortable story.

I scraped the public VivaTech listings: 3,153 exhibitor companies and 1,133 speaker records. Then I conservatively matched speaker organizations back to exhibitors.

The sharpest patterns:

{bullets}

The claim I would lead with:

**VivaTech's floor is startup-heavy, but its matched microphone layer is partner-heavy.**

The sharper founder version:

**Startups risk becoming the background cast for big-company marketing campaigns: they supply the event's energy while partner-class organizations dominate the matched microphone.**

The media version:

**VivaTech risks reading like the conference equivalent of a magazine filled with advertorial reportage.**

Important caveat: this is public listing analysis, not internal sponsorship data. It measures visibility in the public speaker/exhibitor data, not causality.
"""


def editorial_brief(claims: list[dict[str, str]]) -> str:
    strongest = claims[0]
    return f"""# Editorial Brief

## Thesis

{strongest['headline']}

The viral framing is simple: VivaTech sells the energy of a startup marketplace, but the public speaker/exhibitor overlap shows a much more institutional microphone layer.

The harder story is that startups can become the background cast for big-company marketing campaigns: they create the floor's energy, while partner-class organizations receive disproportionate agenda visibility.

## Best Lead

{strongest['punchline']}

Evidence: {strongest['evidence']}

## Why This Hits

The claim cuts against the default conference narrative. Instead of asking which AI startups are hot, it asks who actually gets agenda visibility. That is more politically charged because it touches status, sponsorship-adjacent dynamics, geography, and founder access.

In media terms, the edge is that VivaTech can read like the conference equivalent of a magazine filled with advertorial reportage: the editorial surface is hard to separate from the commercial visibility machine.

## Safe Language

- Use "matched speaker slots", not "all speaker influence".
- Use "public listing data", not "internal agenda decisions".
- Use "speaker density" or "matched microphone layer", not "power" unless clearly framed as metaphor.
- Say "conservative matching likely undercounts true links".
- Treat country rankings as directional until country labels are normalized.

## Claims To Avoid

- Do not say partners bought the stage; sponsorship causality is not proven.
- Do not say startups were excluded; only public matched-speaker visibility is measured.
- Do not say AI is fake; the data only shows AI-tag saturation.
- Do not use the web-search enrichment as evidence for all entities; it is partial and blocked.

## Recommended Visual Order

1. `card_01.svg`: partners are 21x louder per company.
2. `card_02.svg`: top billing almost erases startups.
3. `card_03.svg`: top speakers are more tagless.
4. `card_04.svg`: Tech for Change is under-amplified.
5. `card_08.svg`: US booth count vs agenda leverage.
"""


def executive_viral_brief(claims: list[dict[str, str]]) -> str:
    primary = claims[0]
    top_billing = claims[1]
    tech_for_change = claims[3]
    return f"""# Executive Viral Brief

## One-Line Thesis

The floor is startups. The microphone is partners.

## Boardroom Version

VivaTech can credibly say it has a startup-heavy marketplace. The public listing data also shows a sharper governance problem: the matched speaker layer is partner-heavy, attention is concentrated, and the public narrative can look closer to advertorial programming than independent editorial selection.

The blunt founder critique is that startups risk becoming the background cast for big-company marketing campaigns: they supply the event's energy while partner-class organizations dominate the matched microphone.

## Lead With This

{primary['headline']}

Evidence: {primary['evidence']}

Caveat: {primary['caveat']}

## Three Posts That Can Travel

1. VivaTech's startup floor is real. Its microphone layer tells a partner story.
2. Startups risk becoming the background cast for big-company marketing campaigns.
3. VivaTech risks reading like the conference version of a magazine filled with advertorial reportage.
4. The fix is not less sponsorship. It is clearer separation: sponsors buy visibility; an editorial board chooses the stage.

## Executive Talking Points

- The issue is governance, not scandal: the data does not prove pay-for-stage.
- The public risk is perception: a forum can look like a journal full of advertorial reportage.
- The reform is simple to understand: publish selection criteria, disclose conflicts, and separate stage curation from partnership-development incentives.
- The founder angle is access: startups dominate the floor but weakly convert into matched speaker visibility.
- The marketing-campaign angle is defensible when framed as visibility structure: startups supply the event texture while partners capture disproportionate agenda presence.
- The public-interest angle is mission drift: {tech_for_change['headline']} {tech_for_change['evidence']}

## Strongest Evidence Pair

- {primary['metric']}: {primary['headline']} {primary['evidence']}
- {top_billing['metric']}: {top_billing['headline']} {top_billing['evidence']}

## Safe Language

- Say "matched speaker layer", "public listings", and "governance risk".
- Say "advertorial feel" or "advertising logic" as interpretation, not proven intent.
- Say "conservative matching may undercount true links".

## Red Lines

- Do not claim a specific stage slot was sold.
- Do not claim sponsorship causality.
- Do not claim startups were banned or excluded.
- Do not use country rankings as official rankings without normalization.
"""


def html_index(claims: list[dict[str, str]]) -> str:
    rows = []
    for claim in claims:
        rows.append(
            f"""
            <section>
              <img src="../claim_outputs/social_cards/{claim['card_file']}" alt="{claim['headline']}" />
              <div>
                <h2>{claim['headline']}</h2>
                <p class="metric">{claim['metric']}</p>
                <p>{claim['evidence']}</p>
                <p class="caveat">Caveat: {claim['caveat']}</p>
                <pre>{short_post(claim)}</pre>
              </div>
            </section>
            """
        )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VivaTech Publish Media Kit</title>
  <style>
    body {{ margin: 0; background: #fbfaf7; color: #171411; font-family: Inter, system-ui, sans-serif; }}
    main {{ max-width: 1160px; margin: 0 auto; padding: 40px 22px 70px; }}
    h1 {{ font-size: clamp(2.4rem, 5vw, 5.5rem); line-height: .96; letter-spacing: 0; margin: 0 0 14px; }}
    .lede {{ color: #5f5750; max-width: 850px; font-size: 1.1rem; }}
    section {{ display: grid; grid-template-columns: minmax(240px, .36fr) minmax(0, .64fr); gap: 28px; padding: 30px 0; border-top: 1px solid #ddd4c8; }}
    img {{ width: 100%; border: 1px solid #ddd4c8; }}
    h2 {{ font-size: clamp(1.5rem, 3vw, 3.4rem); line-height: 1; margin: 0 0 8px; }}
    p {{ color: #5f5750; }}
    .metric {{ color: #2454a6; font-weight: 900; font-size: 1.4rem; }}
    .caveat {{ border-left: 4px solid #ddd4c8; padding-left: 12px; }}
    pre {{ white-space: pre-wrap; background: #eee9e1; padding: 14px; overflow-wrap: anywhere; }}
    @media (max-width: 800px) {{ section {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
<main>
  <h1>VivaTech publish kit</h1>
  <p class="lede">Copy-ready hooks, caveated captions, and the matching SVG evidence cards.</p>
  {''.join(rows)}
</main>
</body>
</html>
"""
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def main() -> None:
    claim_path = BASE / "claim_outputs" / "claim_bank.csv"
    metrics_path = BASE / "claim_outputs" / "claim_metrics.json"
    claims = read_csv(claim_path)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert len(claims) == 12, len(claims)

    evidence_rows = []
    for claim in claims:
        card_path = BASE / "claim_outputs" / "social_cards" / claim["card_file"]
        assert card_path.exists(), card_path
        evidence_rows.append(
            {
                "rank": claim["rank"],
                "headline": claim["headline"],
                "metric": claim["metric"],
                "evidence": claim["evidence"],
                "caveat": claim["caveat"],
                "card_file": str(card_path),
                "primary_source_file": str(claim_path),
                "metrics_source_file": str(metrics_path),
                "caption": punchy_caption(claim),
                "short_post": short_post(claim),
            }
        )

    write_csv(
        OUT / "claim_evidence_map.csv",
        evidence_rows,
        [
            "rank",
            "headline",
            "metric",
            "evidence",
            "caveat",
            "card_file",
            "primary_source_file",
            "metrics_source_file",
            "caption",
            "short_post",
        ],
    )

    posts = [short_post(claim) for claim in claims[:8]]
    (OUT / "x_thread.md").write_text(thread(posts), encoding="utf-8")
    (OUT / "linkedin_post.md").write_text(linkedin_post(claims), encoding="utf-8")
    (OUT / "editorial_brief.md").write_text(editorial_brief(claims), encoding="utf-8")
    (OUT / "executive_viral_brief.md").write_text(executive_viral_brief(claims), encoding="utf-8")
    (OUT / "publish_index.html").write_text(html_index(claims), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# VivaTech Publish Media Kit\n\n"
        "This folder turns the validated claim bank into copy-ready publishing assets.\n\n"
        "- `claim_evidence_map.csv`: every hook mapped to evidence, caveat, and card file.\n"
        "- `x_thread.md`: thread draft.\n"
        "- `linkedin_post.md`: longer post draft.\n"
        "- `editorial_brief.md`: thesis, red lines, and recommended visual order.\n"
        "- `executive_viral_brief.md`: boardroom-ready thesis, post hooks, and red lines.\n"
        "- `publish_index.html`: browsable kit with cards and copy blocks.\n\n"
        f"Source counts: {metrics['company_count']} companies, {metrics['speaker_count']} speakers, {metrics['matched_speakers']} matched speakers.\n",
        encoding="utf-8",
    )

    summary = {
        "claims": len(claims),
        "company_count": metrics["company_count"],
        "speaker_count": metrics["speaker_count"],
        "matched_speakers": metrics["matched_speakers"],
        "outputs": {
            "directory": str(OUT),
            "evidence_map": str(OUT / "claim_evidence_map.csv"),
            "x_thread": str(OUT / "x_thread.md"),
            "linkedin_post": str(OUT / "linkedin_post.md"),
            "editorial_brief": str(OUT / "editorial_brief.md"),
            "executive_viral_brief": str(OUT / "executive_viral_brief.md"),
            "publish_index": str(OUT / "publish_index.html"),
        },
    }
    (OUT / "media_kit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
