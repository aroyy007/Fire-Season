# Fire Season Competition MVP

Status: ready-for-agent

## Problem Statement

A Monitoring Analyst preparing a seasonal monitoring plan can access historical satellite hot-spot records, but cannot safely interpret a change across the MODIS and VIIRS eras as a change in burning activity. The products differ in sensitivity, sampling, resolution, quality states, and observation support. A naïve merged count can therefore make a sensor transition look like a real environmental change.

Existing fire maps and alert dashboards make detections visible, but visibility alone does not answer the analyst's decision question: **did recorded burning change, or did the observing system change?** They also commonly blur no observation, observed non-fire, and detected activity. The analyst needs a concise way to find typical burning periods, inspect unusual months, judge whether a historical comparison is credible, and identify months or 10 km analysis blocks that merit human review or field coordination.

The project must answer that question with NASA data, transparent methods, explicit uncertainty, and reproducible evidence. It must remain honest when the evidence is insufficient. It also has to fit a four-person hackathon team, work during an unreliable live demonstration, and use only Open Resources. Scientific validity, challenge relevance, and a clear user story take precedence over feature count and fashionable AI behavior.

## Solution

Build **Fire Season**, an offline-capable, sensor-aware burning activity calendar for two Curated Regions. The first region is a data-rich northeast India–Myanmar Science Pilot used to establish scientific viability. The second is a Chattogram Hill Tracts and adjacent Cox's Bazar Local Impact Case, released only if its observation support and calibration scope justify a trustworthy result.

The product preserves each Native Sensor Record and separately presents Comparable Activity only when a Calibration Release has passed declared evaluation and scope gates. The first calibration expresses Suomi-NPP VIIRS VNP14A1 Version 2 activity on the Aqua MODIS MYD14A1 Collection 6.1 Reference Product scale. It does not claim to estimate the true number of fires, burned area, fire danger, or ignition cause.

A Monitoring Analyst opens a Curated Region, explores a year-by-month calendar, switches between Native Sensor Records and eligible Comparable Activity, selects an unusual month, checks Observation Support and uncertainty, inspects an Evidence Receipt, and exports a one-page Monitoring Brief. When the evidence is inadequate, the product displays an Unavailable Comparison with a specific reason while retaining the supported native evidence.

A reproducible Python pipeline creates immutable, versioned Analysis Artifacts. A lightweight React application consumes those artifacts without fitting models or calling required external services during judging. The demonstrated application must run from a static public host and from a verified local build. No paid API, proprietary model, commercial map token, trial credit, account system, database, job queue, or live AI service is required.

The Competition MVP contains no user-facing agent. An Evidence Investigator may be considered only after every core scientific, accessibility, reliability, and presentation gate passes. If added later, it may read released Analysis Artifacts and produce grounded explanations, but it cannot calculate, alter, or release scientific values.

## User Stories

1. As a Monitoring Analyst, I want to open the product without creating an account, so that I can evaluate it without an onboarding barrier.
2. As a Monitoring Analyst, I want to choose between two named Curated Regions, so that every available comparison stays within an evaluated scope.
3. As a Monitoring Analyst, I want the application to identify the Science Pilot and Local Impact Case clearly, so that I understand the role each region plays in the evidence.
4. As a Monitoring Analyst, I want to see the declared analysis period and Reference Product, so that I know what the calendar represents.
5. As a Monitoring Analyst, I want to see a year-by-month burning activity calendar, so that I can recognize typical seasonal patterns quickly.
6. As a Monitoring Analyst, I want calendar values to use a declared Detected Activity Rate, so that I do not mistake detected cell-days for a count of individual fires.
7. As a Monitoring Analyst, I want the activity unit and denominator visible near the visualization, so that I can interpret values without searching through documentation.
8. As a Monitoring Analyst, I want the MODIS–VIIRS era boundary shown on the calendar, so that a platform transition cannot pass unnoticed.
9. As a Monitoring Analyst, I want to switch between Native Sensor Records and Comparable Activity, so that I can see what the evaluated transfer changes.
10. As a Monitoring Analyst, I want each Native Sensor Record to retain its product, platform, and version identity, so that unlike measurements are never presented as one raw series.
11. As a Monitoring Analyst, I want the application to explain that Comparable Activity is expressed on the Aqua MODIS Reference Product scale, so that I do not interpret it as true fire activity.
12. As a Monitoring Analyst, I want Comparable Activity to appear only from a Calibration Release, so that an experimental fit cannot become an operational-looking result.
13. As a Monitoring Analyst, I want an Unavailable Comparison when calibration evidence is insufficient, so that missing scientific support is not disguised as zero or a model estimate.
14. As a Monitoring Analyst, I want the unavailable state to name its reason, so that I can distinguish poor observation support, inadequate overlap, domain failure, and an unreleased calibration.
15. As a Monitoring Analyst, I want Native Sensor Records to remain visible when a comparison is unavailable, so that supported evidence is not discarded.
16. As a Monitoring Analyst, I want unknown observation, valid observed non-fire, and detected activity to be distinct states, so that empty-looking periods are not automatically interpreted as safe.
17. As a Monitoring Analyst, I want Observation Support visible for every selected month, so that I can judge how much valid land-cell-day evidence underlies a value.
18. As a Monitoring Analyst, I want missing evidence encoded by pattern and text rather than color alone, so that I can distinguish it from low activity and model uncertainty.
19. As a Monitoring Analyst, I want uncertainty bounds around Comparable Activity, so that apparent precision does not exceed the calibration evidence.
20. As a Monitoring Analyst, I want the uncertainty label to state what the interval covers and omits, so that I do not assume it captures every source of sensor or domain error.
21. As a Monitoring Analyst, I want to select a calendar month and inspect its evidence, so that I can investigate an unusual period without leaving the main workflow.
22. As a Monitoring Analyst, I want to compare a selected month with the same calendar month in a fixed historical reference window, so that seasonal differences do not drive the Activity Anomaly.
23. As a Monitoring Analyst, I want the selected year excluded from its own anomaly baseline, so that the comparison does not dilute itself.
24. As a Monitoring Analyst, I want Activity Anomaly language to remain descriptive, so that it is not confused with a forecast, hazard warning, or causal claim.
25. As a Monitoring Analyst, I want a small context map for the selected region and analysis blocks, so that I can connect the calendar to geography without navigating a full GIS platform.
26. As a Monitoring Analyst, I want months and 10 km analysis blocks ranked as Investigation Priorities, so that I can focus human review and monitoring coordination.
27. As a Monitoring Analyst, I want Investigation Priority wording to avoid emergency severity and automatic dispatch implications, so that the tool stays within its evidence and intended decision.
28. As a Monitoring Analyst, I want a one-page Monitoring Brief, so that I can carry the result into a planning conversation.
29. As a Monitoring Analyst, I want the Monitoring Brief to state the region, time period, typical burning months, selected anomaly, and Investigation Priority, so that its practical conclusion is self-contained.
30. As a Monitoring Analyst, I want the Monitoring Brief to include Native Sensor Records, eligible Comparable Activity, Observation Support, and uncertainty, so that its conclusion remains auditable.
31. As a Monitoring Analyst, I want the Monitoring Brief to include calibration status and limitations, so that it does not overstate a result when forwarded without the application.
32. As a Monitoring Analyst, I want the Monitoring Brief to contain an Evidence Receipt identifier, so that another person can trace its result to the exact inputs and method.
33. As a Monitoring Analyst, I want to export compact CSV data, so that I can inspect the displayed values with common analysis tools.
34. As a Monitoring Analyst, I want to export the Evidence Receipt as JSON, so that the analysis can be reproduced and checked programmatically.
35. As a researcher, I want the Evidence Receipt to name source products, versions, granules, checksums, region revision, dates, exclusions, quality policy, calibration release, and software environment, so that the result is reproducible.
36. As a researcher, I want the Evidence Receipt to distinguish observed, modeled, and unavailable values, so that provenance is not lost after export.
37. As a researcher, I want the calibration training and held-out seasons recorded, so that I can detect leakage or post-hoc evaluation.
38. As a researcher, I want evaluation results against transparent baselines, so that model complexity is justified by measurable improvement.
39. As a researcher, I want a geographically separate Transfer Test Region evaluation, so that the limits of geographic transfer are visible.
40. As a researcher, I want Corroborating Evidence labeled separately from active-fire validation targets, so that burned-area imagery or incident records are not treated as perfect ground truth.
41. As a researcher, I want exact product mask classes decoded according to the provider documentation, so that file names and visual appearance do not substitute for data semantics.
42. As a researcher, I want categorical masks reprojected only with mask-preserving methods, so that interpolation cannot create false fire or quality classes.
43. As a researcher, I want valid land-cell-days and detected land-cell-days retained as integer sufficient statistics, so that the Detected Activity Rate has an inspectable denominator.
44. As a researcher, I want the FIRMS recent-detection context kept separate from the daily 1 km science stream, so that 375 m point counts never contaminate the harmonization metric.
45. As a researcher, I want calibration to abstain outside its evaluated product versions, geography, activity range, and support domain, so that a released model is not treated as universal.
46. As a judge, I want the opening view to communicate the question “did burning change, or did the observing system change?”, so that the project's challenge relevance is immediately clear.
47. As a judge, I want to see a real apparent change across the sensor transition, so that the demonstration addresses a concrete interpretive problem.
48. As a judge, I want to compare the native view with the comparable view, so that I can see the specific contribution of harmonization.
49. As a judge, I want the team to demonstrate a deliberate Unavailable Comparison, so that scientific restraint is visible as a product capability.
50. As a judge, I want to open an Evidence Receipt from the demonstrated month, so that the result is more than a polished visualization.
51. As a judge, I want the application and demo links to work without authentication, so that I can evaluate the submission immediately.
52. As a judge, I want the core application to work without network access, so that temporary service failure does not prevent evaluation.
53. As a judge, I want every NASA dataset and external resource attributed, so that the project's use of open data is transparent.
54. As a judge, I want AI assistance disclosed accurately, so that I can assess originality, intent, and execution.
55. As a keyboard user, I want to move through calendar cells, select a month, open evidence, and return focus predictably, so that the primary workflow does not require a pointer.
56. As a screen-reader user, I want each month to announce its period, value type, activity value, support, uncertainty, and comparison status, so that the visualization has an equivalent interpretation.
57. As a user with color-vision differences, I want text, shape, and pattern to reinforce color encodings, so that no scientific state depends on color alone.
58. As a user on a small laptop, I want the calendar, selected-month evidence, and essential controls readable without excessive scrolling, so that the judged experience remains coherent.
59. As a mobile user, I want a selected year's months presented as an accessible vertical list, so that the evidence remains usable on a narrow display.
60. As a user with reduced-motion preferences, I want nonessential animation removed, so that transitions do not impair access or interpretation.
61. As a team member, I want a deterministic build from pinned dependencies, so that another machine can reproduce the approved analysis and application.
62. As a team member, I want source retrieval credentials excluded from artifacts and version control, so that free access keys are not exposed.
63. As a team member, I want failed or partial pipeline runs to leave the last released Analysis Artifact unchanged, so that incomplete work cannot corrupt the demo.
64. As a team member, I want every Analysis Artifact to be immutable and versioned, so that the browser, exports, and presentation all describe the same result.
65. As a team member, I want the frontend to consume only released artifact fields, so that it cannot silently recompute or reinterpret the science.
66. As a team member, I want the application to fall back to a local static build, so that hosting availability is not a competition dependency.
67. As a team member, I want all critical data, code, fonts, boundaries, and map assets to be Open Resources, so that the project requires no payment, trial credit, or proprietary permission.
68. As a team member, I want the Science Pilot to reach a documented go/no-go decision before the event, so that the team can pivot instead of defending an invalid harmonization.
69. As a team member, I want the Local Impact Case withheld or shown as unavailable when it fails evidence checks, so that local relevance does not override scientific validity.
70. As a team member, I want optional features cut before Native Sensor Records, Observation Support, Unavailable Comparison, or Evidence Receipts, so that the core claim survives schedule pressure.
71. As a potential fifth teammate, I want a clearly defined domain-review and user-access role, so that I can contribute expertise beyond generic development.
72. As a Bangladesh Forest Department regional analyst or research proxy, I want the product tested through realistic monitoring tasks, so that usability claims reflect actual interpretation rather than team familiarity.
73. As a tester, I want to identify the typical high-activity season, distinguish no observation from no detected activity, and locate the Evidence Receipt, so that the evaluation covers the product's essential reasoning tasks.
74. As a maintainer, I want withdrawn Calibration Releases preserved in historical Evidence Receipts, so that past results are not silently rewritten.
75. As a maintainer, I want a new product, platform, or collection version to require a separate compatibility evaluation, so that a renamed source cannot inherit an unrelated calibration.
76. As a maintainer, I want the repository to include data-source records, asset licenses, checksums, reproducibility instructions, and AI-use disclosure, so that the public project can be independently inspected.

## Implementation Decisions

- The primary product claim is that Fire Season helps a Monitoring Analyst determine whether a change in recorded burning persists after accounting for a satellite-product transition. It does not claim to reveal true fire counts.
- The Competition MVP serves a regional land- or forest-management Monitoring Analyst. A remote-sensing or environmental researcher is the principal accessible proxy for early user testing.
- The first released experience contains two predefined Curated Regions: a bounded northeast India–Myanmar Science Pilot and a Chattogram Hill Tracts plus adjacent Cox's Bazar Local Impact Case. The local region is displayed only after its evidence checks pass; otherwise it becomes an explicit unavailable case.
- Arbitrary user polygons are excluded. This prevents a user from requesting Comparable Activity outside the calibration's evaluated geography and keeps the interface within the team's validation capacity.
- The science stream uses compatible daily 1 km active-fire mask products: Aqua MODIS MYD14A1 Collection 6.1 and Suomi-NPP VIIRS VNP14A1 Version 2. FIRMS 375 m detections may appear as separately labeled recent context and never share the daily-mask denominator.
- The primary metric is detected active land-cell-days per valid observed land-cell-days for a declared product, region or 10 km block, and month. The UI must always identify the unit, product scale, and support denominator.
- The initial transfer direction is VIIRS to the Aqua MODIS Reference Product scale. Comparable Activity means the expected Reference Product record under the released transfer; it is not an estimate of physical truth.
- Source discovery and retrieval use free NASA services such as CMR, Earthdata, FIRMS, and GIBS where appropriate. Credentials may be required for preparation but are never required by the judged browser application or stored in the repository.
- The pipeline records source identifiers, provider metadata, retrieval time, offered checksums when present, local SHA-256 checksums, temporal coverage, product version, region revision, and quality-policy version.
- Product mask and quality classes are decoded from official product documentation. No-observation, observed non-fire, and detected states remain distinct throughout ingestion, aggregation, artifacts, and display.
- Categorical reprojection uses nearest-neighbor or an equivalent mask-preserving operation. Alignment, coordinate reference system, affine transform, array shape, fill values, and daily planes are validated before aggregation.
- Membership in a Curated Region uses a declared centroid rule for integer land-cell-day statistics. Fractional area weighting requires a future metric and likelihood redesign and cannot be inserted into the first release silently.
- Monthly sufficient statistics are computed for the region and 10 km analysis blocks. These statistics include eligible, valid, and detected cell-days, source identity, comparison status, and quality exclusions.
- The model ladder begins with Native Sensor Records, then an identity baseline, a simple seasonal constant or monotone baseline, and a grouped binomial generalized linear model. A beta-binomial model is allowed only when dispersion diagnostics justify it. Tree ensembles, foundation models, and deep learning are excluded from the first harmonization engine.
- Training and evaluation use temporal blocking. The minimum support target is five training seasons and two untouched held-out seasons, with sufficient positive block-months and coverage inside the declared calibration domain. Fifty positive block-months is an initial diagnostic threshold rather than proof of adequacy.
- A month must have at least 50 percent valid land-cell-days to support its primary comparison unless the science protocol records and justifies a revised threshold before evaluation.
- A Calibration Release must lower held-out mean absolute error by at least 10 percent relative to the best simple baseline, avoid materially worse bias in either pilot geography, keep peak-season timing error within one month, and achieve 85–95 percent empirical coverage for a nominal 90 percent interval. It must also have adequate independent test support and pass its product, geography, support, and domain checks.
- Held-out MODIS–VIIRS overlap is the primary quantitative evaluation. A geographically separate Transfer Test Region assesses transfer credibility. Burned-area products, imagery, and incident records are Corroborating Evidence rather than perfect ground truth for active-fire detections.
- If the calibration fails a release gate, the product keeps Native Sensor Records and displays an Unavailable Comparison. It must not rename raw aggregation or an experimental fit as harmonization.
- The application reads immutable Analysis Artifacts generated ahead of the judged session. It performs no model fitting, raw satellite decoding, or required remote API call in the browser.
- The Analysis Artifact bundle is the central interface between the scientific pipeline and the product. It contains versioned calendar data, block summaries, evaluation linkage, calibration metadata, uncertainty bounds, status and reason codes, export data, and an Evidence Receipt.
- Internal analytical tables use Parquet. The static frontend consumes versioned JSON. User exports use CSV and JSON. Every distributable artifact has a checksum and a stable receipt identifier.
- The first implementation is artifact-first and static. It uses no authentication, production database, job queue, or live analysis service. A minimal static-file server may be used in development; an API is added only if later deployment requirements make it necessary.
- The frontend uses React, TypeScript, and Vite. SVG or Observable Plot renders the calendar and comparison charts. MapLibre may render a small context map from locally packaged open or public-domain geography. The core workflow remains usable when the map is unavailable.
- GitHub Pages is the primary public deployment target, with the generated static distribution verified locally as a fallback. The application has no critical dependency on paid hosting, commercial map tiles, analytics, trackers, or third-party accounts.
- The opening screen places the year-by-month calendar, region selector, period, view switch, and sensor-era boundary above secondary explanation. It avoids a marketing hero, spinning globe, dense KPI wall, and generic chat entry point.
- The primary interaction is: select Curated Region, inspect calendar, select month, switch between Native Sensor Records and Comparable Activity, inspect Observation Support and uncertainty, open the Evidence Receipt, and export a Monitoring Brief.
- Missing evidence uses text and a hatch or pattern. Model uncertainty uses bounds or a band. Low activity uses a separate quantitative encoding. These states cannot rely on color alone or share an ambiguous visual treatment.
- The context map supports geographic orientation and 10 km Investigation Priority inspection. It is not the analytical database or the dominant interface.
- The one-page Monitoring Brief includes region and period, typical months, selected Activity Anomaly, Native Sensor Records, eligible Comparable Activity, Observation Support, uncertainty, Investigation Priority, calibration status, limitations, and Evidence Receipt identifier.
- All user-facing language avoids emergency, safety, causality, and forecast claims. Preferred phrases include “No usable observations,” “Estimated on the Aqua reference scale,” “Higher than this region's baseline for March,” and “Comparison unavailable.”
- The Competition MVP contains no chatbot, voice interface, or required agentic behavior. A future Evidence Investigator may use a local open-source model to query released evidence through bounded tools, but only after all core gates pass and with a deterministic explanation fallback.
- The judged demonstration works offline and begins with a real apparent change, identifies the sensor transition, compares native and reference-scale views, opens the evidence, and ends with an Unavailable Comparison. It never depends on a live model or provider response.
- The target submission materials are an English project page, a public repository, a public static application, a concise visual demo compatible with the final 2026 guide, and a seven-slide backup. A Bengali interview or brief summary is optional only after the English core is complete.
- The repository licenses original code under MIT and records the attribution and applicable terms of every source dataset, boundary, font, icon, and other asset. It includes an exact AI-assistance disclosure and never exposes credentials.
- The four core owners are remote-sensing/statistics, Python data and reproducibility, frontend and data visualization, and product/testing/story/submission. A fifth teammate should contribute fire ecology, forestry, or direct user access.
- The build order freezes the artifact contract first, then runs science and frontend work in parallel. Optional AI, bilingual UI, live refresh, arbitrary polygons, extra overlays, extra exports, and broader region support are cut before any core evidence feature.
- The pre-event go/no-go gate requires at least one real paired product sample to be retrieved, decoded, aligned, aggregated, and timed. If paired-mask processing or overlap support remains untenable by the declared October 18 checkpoint, the team pivots instead of making an unsupported harmonization claim.

## Testing Decisions

- The primary and deliberately shared test seam is the **released Analysis Artifact bundle**. The scientific pipeline publishes this bundle, the frontend consumes it, the exports reproduce it, and the demo presents it. Testing this boundary gives the highest useful coverage with one stable interface.
- Good tests assert externally observable scientific and user behavior rather than internal function calls, library choices, coefficient layout, component structure, or chart implementation details.
- One small, pinned, legally distributable real paired-granule fixture will exercise mask decoding, quality-state preservation, alignment checks, sufficient-statistic aggregation, calibration eligibility, and Analysis Artifact publication. Synthetic micro-fixtures may supplement edge cases but cannot be the only integration evidence.
- Contract validation will reject an Analysis Artifact that lacks source identity, product version, unit, valid support, comparison status, status reason, calibration reference, uncertainty semantics, receipt identifier, or checksum.
- Contract validation will verify that observed, modeled, and unavailable values are mutually distinguishable and that an unavailable numeric estimate is null rather than zero.
- A pipeline integration test will confirm that no-observation, observed non-fire, and detected activity in the pinned fixture survive into the published artifact without semantic collapse.
- A pipeline integration test will confirm that the daily-mask science stream and FIRMS point context cannot be combined under one numerator, denominator, or product identity.
- A release-gate test will verify that Comparable Activity is published only when the calibration version, reference direction, product versions, region scope, support threshold, and evaluation gates all match the analysis request.
- Failure-path tests will independently trigger insufficient Observation Support, inadequate overlap, out-of-domain input, incompatible product version, and unreleased calibration. Each must yield a successful artifact with an Unavailable Comparison and a specific reason rather than a fabricated estimate.
- Evaluation tests will compare the candidate model with the identity and simple seasonal baselines on untouched blocks. They will assert the declared mean absolute error, regional bias, peak-timing, and interval-coverage gates from the published evaluation record.
- A reproducibility test will run the pinned input and locked environment twice and compare normalized artifact content and checksums, allowing only explicitly documented nondeterministic metadata such as build time.
- A snapshot immutability test will verify that a failed or partial rebuild cannot overwrite the last Calibration Release or published Analysis Artifact.
- Browser tests will load the same Analysis Artifact bundle used by the pipeline contract tests and complete the full primary workflow: choose region, inspect calendar, select month, switch views, read Observation Support and uncertainty, open the Evidence Receipt, and export the Monitoring Brief.
- Browser tests will verify the explicit Unavailable Comparison workflow and ensure Native Sensor Records remain available while comparable numeric output is suppressed.
- Browser tests will assert that the sensor-era boundary, unit, Reference Product, source identity, and modeled-versus-observed distinction are visible without relying on a tooltip.
- Export tests will compare the displayed month, CSV row, JSON Evidence Receipt, and Monitoring Brief fields against the same artifact values so that no presentation layer silently changes the science.
- Offline smoke testing will serve the built static application with network access disabled and complete the core workflow, including local map fallback, evidence inspection, and exports.
- Accessibility testing will cover keyboard calendar navigation, focus return, visible focus, accessible month names, table alternatives for map and chart information, non-color state encoding, text contrast, reduced motion, and the narrow-screen month list.
- Usability evaluation will recruit five representative testers, including at least one environmental or remote-sensing researcher. Each tester will identify the typical high-activity season, distinguish no observation from no detected activity, and locate the Evidence Receipt. The working target is successful completion by at least four of five testers, with time and interpretation errors recorded.
- The demo rehearsal will be tested on the actual presentation laptop from the local static build, with external network disabled, and timed against the final official submission limit.
- There is no implemented application test suite in the repository yet. The closest prior art consists of saved endpoint evidence, source manifests and checksums, data-access verification scripts, schema and OpenAPI invariants, and report/package verification scripts. New tests should preserve that evidence-oriented style while centering the Analysis Artifact boundary.

## Out of Scope

- Arbitrary polygon drawing or upload and claims of globally supported analysis.
- Real-time fire detection, operational alerts, emergency dispatch, evacuation advice, or public-safety recommendations.
- Wildfire spread or ignition forecasting, fire-danger scoring, and weather-driven prediction.
- Attribution of a thermal detection to wildfire, agricultural burning, industrial activity, or illegal behavior.
- Estimating burned hectares, carbon emissions, lives saved, or financial losses from hot-spot counts.
- A universal correction factor across every MODIS, VIIRS, platform, collection, geography, resolution, or processing stream.
- Harmonizing FIRMS 375 m point counts with the daily 1 km mask products in the initial science metric.
- New transfers for NOAA-20, NOAA-21, future product versions, or Level-2 matched overpasses without separate evaluation.
- Production accounts, authentication, row-level security, PostgreSQL/PostGIS, a job queue, object-storage infrastructure, or live user-submitted analyses.
- A required backend API, live Earthdata download, live calibration fit, or live external call during the judged experience.
- Chatbots, voice agents, autonomous internet research, automatic model selection, or an AI-generated executive summary in the Competition MVP.
- Paid APIs, proprietary inference endpoints, free trials, promotional credits, commercial map tokens, paid hosting, and nonredistributable critical assets.
- Hardware, drones, Internet-of-Things sensors, virtual reality, blockchain, social feeds, marketplaces, or notification subscriptions.
- Full Bengali localization. A concise Bengali summary may be added only after every core requirement is complete.
- More than one Monitoring Brief format, extensive report customization, or an enterprise GIS workspace.
- Claims of institutional adoption, population-level usability, prevented fires, or measured field impact without a later appropriate study.

## Further Notes

- The canonical product sentence is: **“Fire Season helps monitoring analysts tell whether recorded burning changed or the satellite changed.”**
- The project is positioned primarily for Best Use of Science and Best Use of Data, with Local Impact supported by a qualified Bangladesh case rather than by unsupported localization.
- Scientific abstention is part of the product, not an error condition. A polished but unsupported Comparable Activity result fails the product standard.
- Earlier planning material that describes arbitrary polygons, a production database/API stack, or a committed explanation assistant is superseded for the Competition MVP by the accepted architecture decisions summarized here.
- The final 2026 submission guide must be checked when published. Demo duration, permitted preparation, team rules, and disclosure wording may change, but a rule update must not weaken the scientific or provenance gates.
- NASA and other provider data remain under their own terms. The MIT license applies only to the team's original code and documentation.
- The event build should preserve a dated distinction between pre-event research/preparation and work created during the official hackathon, according to the final rules.
- If the Science Pilot cannot support a defensible Calibration Release, the team should pivot to the previously identified trend-analysis alternative rather than relabeling native comparisons as completed harmonization.
