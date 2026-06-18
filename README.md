# The Floor Is Startups. The Microphone Is Partners.

An evidence-backed public-data briefing on VivaTech 2026.

## The Story

VivaTech looks like a startup marketplace from the floor. Its public matched-speaker layer tells a more institutional story.

The sharpest founder reading is that startups risk becoming the background cast for big-company marketing campaigns: they supply the event's energy while partner-class organizations dominate the matched microphone. In media terms, VivaTech can read like the conference equivalent of a magazine filled with advertorial reportage.

This repository turns public VivaTech exhibitor and speaker listings into a journalistic briefing, executive dashboard, and publish-ready media kit. The central question is simple:

> If the main stage is the event's front page, who is the editor: an editorial board or partnership development?

## The Main Findings

- **Partners are 21x louder per company than startups.** Partners are 13.8% of exhibitors and 77.2% of matched speaker slots.
- **Top billing almost erases startups.** Among 20 top-billed speakers matched to exhibitor organizations, 19 map to partners and 1 maps to a startup.
- **Most exhibitors are publicly voiceless in the matched program.** Only 191 of 3,153 exhibitors have a matched speaker.
- **Tech for Change is under-amplified.** The label has 424 exhibitors but 13 matched speakers: 3.1 per 100 companies.
- **The sharper VivaTech story is not AI.** AI is everywhere; the more revealing pattern is who gets amplified inside the event.

## The Editorial Thesis

This does **not** prove that VivaTech sells stage slots to sponsors.

It does support a sharper governance critique: the public program can read like a journal whose reportage is surrounded by advertising logic. The fix is not less sponsorship. The fix is clearer separation.

Sponsors can buy booths, hospitality, private meetings, and clearly labeled sponsor visibility. The main stage should be selected through published editorial criteria, conflict disclosure, and an independent editorial board.

## Open The Briefing

Open the static dashboard locally:

```text
docs/index.html
```

GitHub Pages can serve the same site from the `main` branch `/docs` folder:

```text
https://hghalebi.github.io/vivatech-stage-floor-analysis/
```

The dashboard is designed for executives, founders, journalists, and analysts. It includes:

- a one-minute executive read;
- copy-ready post hooks with attached proof and caveats;
- interactive evidence cards;
- dynamic charts;
- searchable source tables;
- downloadable CSVs, SVGs, and media assets.

## Publish Assets

The most useful files for public posting are:

- `docs/index.html` - the full local dashboard and GitHub Pages entry point.
- `docs/vivatech_dashboard_bundle.zip` - the shareable bundle.
- `analysis/publish_media_kit/executive_viral_brief.md` - boardroom-ready thesis, hooks, and evidence scope.
- `analysis/publish_media_kit/editorial_brief.md` - journalistic framing and recommended visual order.
- `analysis/publish_media_kit/x_thread.md` - draft thread.
- `analysis/publish_media_kit/linkedin_post.md` - draft LinkedIn post.
- `analysis/claim_outputs/social_cards/` - SVG claim cards.

## Source And Method

The analysis uses public VivaTech 2026 exhibitor and speaker listings. It normalizes 3,153 company records, 1,133 speaker records, and conservatively matches speaker organizations back to exhibitor organizations.

The matching is intentionally conservative, so it may undercount true organization links. The findings measure public matched-speaker visibility, not private agenda negotiations, internal sponsorship decisions, or official country rankings.

## Rebuild

```bash
cd analysis
python3 build_publish_media_kit.py
python3 build_dynamic_dashboard.py
```

Validation:

```bash
cd analysis
python3 -m py_compile build_dynamic_dashboard.py build_publish_media_kit.py
node --check ../docs/dashboard.js
```

## Repository Layout

The root is intentionally minimal for GitHub readers:

```text
README.md     editorial front door
docs/         GitHub Pages static site
analysis/     reproducible data, scripts, templates, and media kit
```
