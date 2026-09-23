# Team, feasibility gates and delivery plan

## Recommended recruitment

Recruit around **Fire Season: a sensor-aware burning calendar**, not “an AI disaster platform.” Four owners cover remote-sensing/statistics, Python data and reproducibility, frontend/data visualization, and product/testing/submission. A fifth person should bring fire ecology, forestry, or direct user access.

| Owner | Concrete deliverable | Secondary reviewer |
|---|---|---|
| Remote-sensing/statistics owner | Metric, model ladder, frozen splits, evaluation and Calibration Release | Python data owner |
| Python data/reproducibility owner | Paired masks, QA, provenance, Analysis Artifact and exports | Science owner |
| Frontend/data-visualization owner | Calendar, evidence panel, accessible map/table and offline build | Product owner |
| Product/testing/submission owner | User tasks, Monitoring Brief, demo, attribution and submission | Science owner |
| Optional domain/user-access owner | Forestry review, realistic tasks and participant recruitment | Product owner |

Suggested recruitment text: “We are forming a NASA Space Apps team for MODIS–VIIRS hotspot harmonization. Our focus is a reproducible burning calendar that distinguishes changes in fire activity from changes in satellite observations. We need Python/geospatial processing, statistical validation, an excellent data-visualization frontend, and someone who understands environmental monitoring. The goal is one convincing regional demo with open evidence.” This is a draft; it has not been posted.

## Before committing to the challenge

Run a bounded feasibility exercise: obtain one real matching historical tile/date from both science products; decode masks; calculate fire and valid-support counts; inspect a small overlap series; then time the pipeline. Confirm an Earthdata account and the permitted data-access route. The current research established catalog discovery and public CSV access, not this gate.

Pass conditions: readable masks, verified alignment, sufficient overlap, explainable product differences, and a practical CPU runtime for the intended pilot. If access fails, ask a data mentor or use an approved existing extraction route. If science support remains inadequate, choose **Be An Earth System Trend Detective!** with a narrow dry-season heat/rainfall investigation. If an agronomist and extension partner join, reconsider **Field Shift** with constrained rotation scenarios. If a SAR expert produces a usable repeat pair, NISAR becomes a serious alternative.

## Preparation versus competition work

The event homepage currently states 14–15 November 2026. The legal page provides 2026 terms, while the discoverable detailed submission guide still says 2025. Confirm current rules on pre-event code/models, team limits, AI disclosure and demo duration with the event before treating prepared assets as a submission. Keep this research and design package dated and distinguish any permitted starter material from event-created work. [Homepage](https://www.spaceappschallenge.org/) · [Terms](https://www.spaceappschallenge.org/legal/) · [Submission guide](https://www.spaceappschallenge.org/resources/project-submission-guide/)

Preparation can establish user needs, scientific reading, data-access requirements, team roles and a plan. The schedule below is an implementation sequence to use when permitted; it does not assert permission to prebuild a competition entry.

## Proposed 48-hour build sequence

| Window | Work | Exit evidence |
|---|---|---|
| 0–4 h | Freeze AOI, metric, QA policy and splits; obtain first paired masks | Printed counts and source receipt reviewed by two people. |
| 4–12 h | Extract limited history; build native calendars and artifact contracts | Real calendar from immutable data, no modeled claims. |
| 12–20 h | Fit simple baselines and GLM; implement comparison view | Training diagnostics plus untouched test ready. |
| 20–28 h | Evaluate; implement abstention; integrate model receipt | Published pass/fail report; failed model stays experimental. |
| 28–34 h | Complete inspect/export flow and deterministic Monitoring Brief | Reproducible JSON/CSV export and readable brief. |
| 34–40 h | Test with users; check failure cases, accessibility and offline cache | Recorded task results; no unexplained critical defects. |
| 40–48 h | Freeze features, rehearse, credit sources, submit | Public demo/repository, reproducibility instructions and disclosure. |

Actual available work hours vary by local event. Reserve sleep and handoffs; “48-hour event” does not mean every member should work continuously. Assign the science and interface tracks independently but agree on the result schema first. At hour 20, cut optional AI, extra regions and notifications before cutting data validity or a reliable demo.

## Demo and submission package

Prepare a concise narrative usable at different official length limits: user problem, sensor mismatch, real calendar, evidence/uncertainty, and practical use. A longer rehearsal can be three minutes; do not assume that is the submission video allowance. The historical 2025 guide mentioned a much shorter video or a slide option, so verify the 2026 format.

The repository should contain installation instructions, pinned dependencies, a small distributable fixture, data acquisition instructions, artifact schemas, a model card, an evaluation report, licence notices, and an AI-assistance disclosure. The Evidence Receipt lists public source URLs and provider identifiers. No private API credentials or unlicensed reference imagery should be included. Credit open-source work even when its licence does not require prominent UI credit, because Space Apps terms separately require resource attribution.

## Risks and explicit decisions

| Risk | Trigger | Response |
|---|---|---|
| Historical raster access blocked | Cannot download/decode first pair | Resolve before selecting; pivot if unresolved. |
| Transfer does not beat baseline | Held-out gate fails | Keep native calendars; label harmonization experimental; do not invent improvement. |
| Coverage selection dominates | Many months below support threshold | Change pilot or coarsen time/space transparently. |
| Platform transition | NPP delivery ends before event | Retrospective demo works; add NOAA transfer only after validation. |
| No user relevance | Testers cannot name a useful decision | Reframe around monitoring brief, not a generic risk score. |
| Too many features | Core flow incomplete by midpoint | Cut assistant/alerts/extra overlays. |
| Competition rules change | Updated 2026 guide published | Update preparation boundary, credits and submission format. |

## After the event

First, reproduce the analysis in a clean environment and publish known failure cases. Then seek a domain partner to review calibration transfer across regions and a prospective monitoring workflow. Add L2 overpass matching before stronger observation-effort claims. Measure adoption through actual completed briefs and interpretation accuracy. Do not claim prevented fires or financial savings without an appropriate study.
