# VivaTech 2026 Company/Speaker Cross-Analysis

Generated: 2026-06-17T20:54:32+00:00

## Executive Summary

- **The event is AI-saturated, so AI alone is not a differentiator.** 1513 of 3153 exhibitors (48.0%) and 528 of 1133 speakers (46.6%) carry the `Artificial Intelligence & Robotics` tag.
- **The speaker program is not just the exhibitor list with microphones.** 355 of 1133 speakers (31.3%) match an exhibitor by normalized company/alias, and only 191 exhibitors (6.1%) have a matched speaker.
- **The expo floor is startup-heavy, but speaker mindshare is partner-heavy.** 2719 exhibitors are startups (86.2%), while partner exhibitors hold 274 of 355 matched speaker slots.
- **The listing data itself is a strategy signal and a limitation.** 3153 exhibitors (100.0%) have no short description in the payload, so taxonomy, booth geography, and speaker-company matching are more reliable than description mining.

## Data Scope And Trust

- Companies/exhibitors scraped from `https://vivatech.com/exhibitors`, complete cumulative page 158 payload, 3153 unique IDs.
- Speakers scraped from `https://vivatech.com/speakers`, 1133 unique IDs.
- Local CSVs in `/Users/hamzeghalebi/Documents/vivatech` were present by `stat`, but reads failed with `Operation not permitted`, so this report uses a fresh live scrape.
- Company/speaker matching uses exact normalized names plus safe unambiguous aliases from parentheticals, acronyms, `by` tails, and partner prefixes. It is still conservative and may undercount.

## Provocative Patterns

|pattern|evidence|why_it_matters|severity|
|---|---|---|---|
|AI is the event grammar, not a niche track|1513 exhibitors (48.0%) and 528 speakers (46.6%) carry the AI/Robotics tag.|AI is broad enough that simply being AI-tagged is not differentiated; the sharper signal is which adjacent tags it combi|5|
|The stage is less exhibitor-backed than the expo floor|Only 355 of 1133 speakers (31.3%) match an exhibitor by normalized company/alias; 191 of 3153 exhibitors (6.1%) have at |The program is not just a booth amplification layer; it is heavily curated around institutions, media, investors, and co|5|
|Startups dominate supply, but speaker attention is much scarcer|2719 of 3153 exhibitors are startups (86.2%), yet only 81 matched speakers attach to startup exhibitors.|The expo floor is a startup marketplace, while the speaker layer behaves more like a reputation and agenda-setting marke|4|
|Partners are the agenda shortcut|Partner exhibitors are 434 of 3153 companies (13.8%) but hold 274 matched speaker slots (77.2% of matched speakers).|Agenda presence is structurally easier for partner-class organizations than for the long-tail startup floor.|4|
|The public exhibitor list is thin on narrative data|3153 exhibitors (100.0%) have an empty short description in the listing payload; 1349 (42.8%) have no fundraising field.|Discovery from the listing itself is mostly taxonomy/location-driven, not proposition-driven; text mining descriptions w|4|
|Speaker mindshare is concentrated at the top|The top 10 speaker organizations account for 74 speakers (6.5%). Top listed orgs include L'Oréal, PwC, OVHcloud, Le Jame|A few institutions can shape the perceived agenda more than their booth footprint would suggest.|4|
|Korea is split into two country values|South Korea has 96 exhibitors while raw value `korearepublicof` has 57 exhibitors.|Country comparisons need normalization before official ranking or market-priority claims.|3|

## Tag Over- and Under-Representation

|tag|company_count|company_share_pct|speaker_count|speaker_share_pct|speaker_minus_company_share_pp|speaker_per_100_tagged_companies|
|---|---|---|---|---|---|---|
|Growth & Startup & Investment|809|25.7|153|13.5|-12.2|18.9|
|Industry & Supply Chain|565|17.9|66|5.8|-12.1|11.7|
|Energy & Greentech|590|18.7|97|8.6|-10.2|16.4|
|Retail & E-commerce|337|10.7|6|0.5|-10.2|1.8|
|Consulting & B2B services|480|15.2|75|6.6|-8.6|15.6|
|DeepTech|789|25.0|193|17.0|-8.0|24.5|
|Mobility & Smart Cities|368|11.7|46|4.1|-7.6|12.5|
|Healthcare & Wellness|503|16.0|112|9.9|-6.1|22.3|
|Fintech & Banking & Compliance|354|11.2|63|5.6|-5.7|17.8|
|Luxury & Fashion & Cosmetics|211|6.7|29|2.6|-4.1|13.7|
|Media & Entertainment & Creators Economy|175|5.6|95|8.4|2.8|54.3|
|Food & Agriculture|177|5.6|33|2.9|-2.7|18.6|
|HR & EdTech & Future of Work|284|9.0|74|6.5|-2.5|26.1|
|Sovereignty & GovTech|387|12.3|118|10.4|-1.9|30.5|
|Space & Aeronautics|153|4.9|33|2.9|-1.9|21.6|
|Cloud & Infrastructure & Connectivity|305|9.7|93|8.2|-1.5|30.5|
|Artificial Intelligence & Robotics|1513|48.0|528|46.6|-1.4|34.9|
|Marketing & Advertising|224|7.1|67|5.9|-1.2|29.9|
|Gaming & Sports & Esports|71|2.3|35|3.1|0.8|49.3|
|Diversity & Inclusion|146|4.6|59|5.2|0.6|40.4|
|Cybersecurity & Defense|312|9.9|114|10.1|0.2|36.5|

## Country Tension

|country|companies|companies_with_speakers|matched_speakers|speaker_per_100_companies|coverage_pct|no_speaker_companies|
|---|---|---|---|---|---|---|
|France|1579|101|180|11.4|6.4|1478|
|Germany|232|12|26|11.2|5.2|220|
|Canada|124|2|2|1.6|1.6|122|
|South Korea|96|1|2|2.1|1.0|95|
|India|88|2|3|3.4|2.3|86|
|United States of America|73|23|68|93.2|31.5|50|
|Italy|71|2|2|2.8|2.8|69|
|Belgium|70|1|2|2.9|1.4|69|
|korearepublicof|57|0|0|0.0|0.0|57|
|Spain|54|2|2|3.7|3.7|52|
|Japan|52|2|3|5.8|3.8|50|
|Switzerland|45|0|0|0.0|0.0|45|
|Cote d’Ivoire|36|0|0|0.0|0.0|36|
|Taiwan|34|1|1|2.9|2.9|33|
|United Kingdom|33|6|20|60.6|18.2|27|
|Netherlands|32|3|4|12.5|9.4|29|
|Portugal|32|1|1|3.1|3.1|31|
|Hong Kong|29|5|6|20.7|17.2|24|
|China|28|7|10|35.7|25.0|21|
|Senegal|27|0|0|0.0|0.0|27|
|Turkey|26|0|0|0.0|0.0|26|
|Sweden|22|3|5|22.7|13.6|19|
|Israel|21|0|0|0.0|0.0|21|
|Poland|21|0|0|0.0|0.0|21|
|Luxembourg|19|1|1|5.3|5.3|18|

## Speaker Organization Concentration

|rank|speaker_company|speaker_count|exhibitor_match|matched_company_name|matched_company_type|matched_country|
|---|---|---|---|---|---|---|
|1|L'Oréal|14|True|L'Oreal Groupe|partner|France|
|2|PwC|12|True|PwC|partner|United Kingdom|
|3|OVHcloud|6|True|OVHcloud|partner|France|
|4|Le Jamel Comedy Club|6|False||||
|5|EssilorLuxottica|6|True|Essilorluxottica|partner|France|
|6|NVIDIA|6|True|Nvidia|partner|United States of America|
|7|McKinsey & Company|6|True|Quantumblack, AI by Mckinsey|partner|United States of America|
|8|EY|6|False||||
|9|Roland Berger|6|True|Roland Berger|partner|Germany|
|10|Capgemini|6|True|Capgemini Technology Services|partner|France|
|11|AWS|6|True|Amazon Web Services (AWS)|partner|United States of America|
|12|ENGIE|5|True|Engie|partner|France|
|13|Eurazeo|5|False||||
|14|Adobe|4|True|Adobe|partner|United States of America|
|15|Salesforce|4|True|Salesforce|partner|France|
|16|Bpifrance|4|True|Bpifrance|partner|France|
|17|BNP Paribas|4|True|BNP Paribas|partner|France|
|18|IBM|4|True|IBM|partner|United States of America|
|19|Airbus|4|True|Airbus|partner|France|
|20|France|3|False||||
|21|Siemens|3|True|Siemens|partner|Germany|
|22|Orange|3|False||||
|23|CNN|3|False||||
|24|Microsoft France|3|False||||
|25|AXA|3|False||||

## Coverage By Company Type

|company_type|companies|companies_with_speakers|coverage_pct|matched_speakers|
|---|---|---|---|---|
|startup|2719|70|2.6|81|
|partner|434|121|27.9|274|

## Fundraising And Maturity

|fundraising_stage|companies|company_share_pct|matched_speakers|speaker_per_100_companies|
|---|---|---|---|---|
|Unspecified|1349|42.8|306|22.7|
|Pre-Seed - <$1M|469|14.9|11|2.3|
|Not yet - 0|468|14.8|10|2.1|
|Seed - $1M - $5M|393|12.5|12|3.1|
|Bootstrapped - 0|387|12.3|8|2.1|
|Series A - $5M - $15M|140|4.4|6|4.3|
|Series B - $15M - $50M|36|1.1|3|8.3|
|Series C - $50M - $200M|24|0.8|4|16.7|

## Speaker Role Mix

|role_bucket|speakers|speaker_share_pct|top_speakers|top_speaker_share_in_bucket_pct|
|---|---|---|---|---|
|CEO / president / GM|263|23.2|19|7.2|
|Other leadership / specialist|215|19.0|2|0.9|
|Founder / co-founder|202|17.8|12|5.9|
|Other C-suite|197|17.4|6|3.0|
|Investor / VC|91|8.0|0|0.0|
|Product / tech / innovation|76|6.7|1|1.3|
|Media / journalist|36|3.2|0|0.0|
|Government / public sector|30|2.6|7|23.3|
|Academic / research|23|2.0|0|0.0|

## Data Quality Notes

|dataset|field|missing_count|missing_pct|
|---|---|---|---|
|companies|name|0|0.0|
|companies|type|0|0.0|
|companies|country|3|0.1|
|companies|hall|636|20.2|
|companies|stand|159|5.0|
|companies|presence|2|0.1|
|companies|sectors|13|0.4|
|companies|tags|15|0.5|
|companies|fundraising|1349|42.8|
|companies|short_desc|3153|100.0|
|companies|image_url|0|0.0|
|speakers|full_name|0|0.0|
|speakers|company|3|0.3|
|speakers|job_title|11|1.0|
|speakers|tags|329|29.0|
|speakers|image_url|3|0.3|

## Recommended Next Analysis

1. Normalize country names before using country rankings externally, especially `South Korea` and `korearepublicof`.
2. Add fuzzy matching only after a manual review sample; the current alias match is conservative.
3. Enrich exhibitor detail pages if narrative positioning matters; the listing payload has weak descriptions.
4. Compare against prior years to separate stable VivaTech structure from 2026-specific agenda choices.
