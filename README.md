# NASA Space Apps 2026 — challenge decision and product plan

**Recommendation: choose Harmonization of MODIS and VIIRS Hot Spots**, subject to one historical-data feasibility gate. The proposed product, **Fire Season**, helps an environmental analyst answer: “Did burning change, or did the observing system change?” It fits your Python/data-science/remote-sensing strength and preference for practical Earth impact.

Start with [the complete readable report](research-report.html), or the [six-page team decision brief](output/pdf/fire-season-decision-brief.pdf). Research ran 18–19 September 2026. The event homepage currently lists 14–15 November 2026. [Official event](https://www.spaceappschallenge.org/)

## Why this direction

The scientific challenge can become the product's most memorable interaction: compare a region's raw sensor calendar with an evaluated reference-scale estimate, inspect uncertainty, and open the evidence receipt. GROW's current public code already combines a fire map and agent interaction, so a generic “AI wildfire dashboard” is weak differentiation. [GROW](https://github.com/Florianopolis-NASA-Space-Apps/wildfires_chat_dashboard)

| Choice | Fit for your team | Condition |
|---|---|---|
| **Fire harmonization** | Best overall recommendation | Obtain and decode paired historical masks; validate the transfer. |
| **Field Shift** | Strong practical alternative | Recruit an agronomist and a local farming/extension partner. |
| **Earth System Trend Detective** | Best fallback | Focus on one testable regional question and sound time-series statistics. |
| **Dancing with the SARs** | Strong specialist alternative | Verify a compatible NISAR repeat pair and SAR interpretation expertise. |

The [14-challenge comparison](research/challenges/challenge-comparison.md) includes weighted analyst scores, risks and scope. Scores are judgments, not NASA judging scores or winning probabilities. Four Earth-focused options received deeper data review; the remaining ten received brief-level assessment.

## Implementation package

| Document | What it fixes |
|---|---|
| [PRD](docs/01-PRD.md) | User, decision, signature interaction, MVP and acceptance criteria. |
| [TRD](docs/02-TRD.md) | Artifact-first architecture, ingestion, calibration release, offline delivery and test seam. |
| [Model and data protocol](docs/03-MODEL-AND-DATA-PROTOCOL.md) | Exact metric, products, transfer models, splits, uncertainty and abstention. |
| [App flow and design](docs/04-APP-FLOW-AND-DESIGN.md) | Screens, flow diagrams, wireframe, visual direction, mobile and accessible states. |
| [Team and delivery](docs/05-TEAM-AND-DELIVERY.md) | Roles, recruitment draft, feasibility gate, build schedule, demo and risks. |
| [Backend and artifact design](docs/06-BACKEND-SCHEMA.md) | Analysis Artifact, Evidence Receipt, Parquet tables, invariants and atomic publication. |
| [Analysis Artifact schema](backend/schemas/analysis-artifact.schema.json) | Machine-readable browser and export boundary. |
| [Evidence Receipt schema](backend/schemas/evidence-receipt.schema.json) | Machine-readable provenance and evaluation record. |
| [Release Manifest schema](backend/schemas/release-manifest.schema.json) | Final file inventory and checksum authority. |
| [Post-MVP backend references](backend/README.md) | Earlier PostgreSQL and OpenAPI designs, excluded from the competition path. |
| [Repositories and models](docs/07-REPOSITORIES-AND-MODELS.md) | Relevant code, crop/EO model alternatives, licenses and reuse decisions. |
| [Skills audit](docs/08-SKILLS-AUDIT.md) | Every requested skill resource and actual installation/use status. |
| [Implementation status](docs/09-IMPLEMENTATION-STATUS.md) | Real March 2023 raster sample, validation commands, and the remaining science gates. |
| [LLM decision](docs/10-LLM-DECISION.md) | Why the judged MVP has no hosted LLM dependency and how a bounded local explainer could fit later. |
| [Design system](docs/11-DESIGN-SYSTEM.md) | Palette, typography, heatmap encoding, evidence states, and anti-slop component rules. |

## Research and verification

The [winner review](research/winners/winners-and-competition-research.md) and [30-entry winner registry](research/winners/global-winners-2023-2025.csv) distinguish official award identities from project marketing claims. The [source index](research/SOURCES.md) links the collected sources; JSONL files preserve source/evidence/claim records. Raw public samples and endpoint checks are retained under `research/models/` and `research/challenges/`.

The [duplication audit and competition verdict](research/duplication-audit.md) compares the concept with FIRMS, GWIS, scientific harmonization work, public repositories, earlier Space Apps fire projects, and the 2024 global-winning GROW project. Its conclusion is deliberately strict: the concept is promising, but it becomes competitive only after the paired-data validity gate succeeds.

Public FIRMS CSV and NASA POWER requests succeeded. A real March 2023 MYD14A1/VNP14A1 raster sample is now decoded for two candidate windows with QA filtering, pixel-center clipping, complete daily coverage, a native-only artifact and raster-derived blocks. This proves a bounded processing path, not a validated harmonization result.

Three important design findings: FIRMS positive detections alone cannot distinguish no fire from no observation; the daily VIIRS 1 km mask is a different product from 375 m hotspots; and NASA has announced the November 2026 Suomi-NPP delivery transition. The [model protocol](docs/03-MODEL-AND-DATA-PROTOCOL.md) reflects these limits. Field Shift also faces a paused SoilGrids REST service and a documented 2026 SMAP quality notice.

**Still required before the science is considered validated:** confirm and freeze the candidate boundaries, extend the sample across enough years and regions, run independent temporal and geographic evaluation, assess reference data and uncertainty coverage, and conduct user testing. No harmonization score, prevented-fire count or field outcome is claimed.

ECC's `api-design`, `postgres-patterns` and `verification-loop` skills were installed. Other requested repositories were reviewed selectively; no full plugin/hook stack was installed.

## Next action

Have the team and Chattogram organizers confirm whether the two candidate windows fit the challenge and local event rules. Then process additional complete seasonal months and a geographically separate holdout before considering any calibration model. This implementation is a research prototype; verify the local event’s current pre-event-work rules before treating it as submission work.
