# Verification record

Completed 19 September 2026. This record describes checks performed on the research/design package, not on a deployed product.

| Check | Result |
|---|---|
| Research report structure | Passed the deep-research validator. Recommended counterevidence/claims-table headings are warnings; limitations and JSONL claim ledgers are present. |
| Core bibliography network check | 21 of 25 URLs passed; 4 were not automatically verified. Full log: `research/citation-verification.txt`. |
| Citation caveats | One DOI parser retained a closing parenthesis and failed DOI resolution while its URL check passed. Other failures include 403/405 and 404 responses. These are not evidence of fabricated sources; retain provider/search/sample evidence and recheck before submission. |
| Package links | 17 local Markdown links checked; none missing. |
| Source registry | 74 unique linked sources. This is not 74 independently validated scientific claims. |
| Winner registry | 30 unique year/award entries across 2023–2025. |
| API contract | Valid JSON, 11 operations, all internal schema references resolve. No external OpenAPI conformance validator or running API test. |
| Backend schema | 13 tables, static checks and manual review. No PostgreSQL/PostGIS migration, role/grant, RLS or query-execution test. |
| HTML report | 11 chapters; headless browser reported no page errors. Search and navigation reset exercised. No document-level overflow at 390 px width. Desktop/mobile screenshots inspected. |
| PDF | Six pages rendered to images and visually reviewed. No clipped text or table overflow observed. |
| Scientific pipeline | Public sample and catalog request logs exist. Historical raster decode, transfer training, held-out scores and field validation have not been performed. |

The default Playwright browser binary was absent; the installed Chrome executable was used in an isolated headless session after a sandbox launch failure. No personal browser profile was used. Generated QA images/logs are in `output/qa/`.

Reproduction: run `python3 scripts/package_research.py`, the bundled Node runtime on `scripts/build_report.mjs`, the bundled Python runtime on `scripts/build_brief.py`, then `python3 scripts/check_package.py`. The rendering scripts currently contain this machine's bundled dependency paths; update those paths on another computer. The science access-check scripts perform network requests and record current results, which may differ from the preserved September samples.

## 20 September 2026 implementation-document revision

The PRD, TRD, application flow, and backend schema were rewritten from the approved Competition MVP specification. The current architecture is artifact-first and offline-capable. The PostgreSQL and OpenAPI files are now marked as post-MVP references.

| Check | Result |
|---|---|
| Required implementation documents | PRD, TRD, app flow, and backend schema are present and internally identify version 2.0. |
| Artifact contracts | Analysis Artifact, Evidence Receipt, and Release Manifest schemas parse as JSON; every local JSON Schema `$ref` resolves. A Draft 2020-12 validation package was not installed, so metaschema validation was not run. |
| Documentation links | Local links from the revised documents, README, and backend README resolve. Markdown code fences are balanced. |
| Checksum design | Analysis, receipt, and final-manifest inventories avoid self-referential and mutual checksum cycles. |
| Palette contrast | Proposed text/focus pairings tested between 5.15:1 and 14.87:1. Calendar scale and final component pairings still require implementation-time checks. |
| Scientific validation | Still pending. No decoded paired daily-mask fixture, Calibration Release, held-out score, or user test is claimed. |

## 24 September 2026 implementation revision

| Check | Result |
|---|---|
| Contract tests | Passed 6 tests with `python3 -m unittest discover -s pipeline/tests -v`. This covers fixture invariants, unavailable-result rejection, release-manifest hashes, and static no-remote-dependency checks. |
| JavaScript syntax | Passed `node --check app/app.js`. |
| Generated bundles | Passed both Science Pilot and Local Impact Case builds; analysis, receipt, payload, and manifest checksums match. |
| Browser smoke test | Passed in Chrome against a local static server: region switch, Comparable Activity unavailable state, Evidence Receipt panel, fixture boundary copy, and no browser console errors. Download controls are wired to Blob exports; browser download-event capture is not available in the smoke harness. |
| Scientific validation | Still pending. The current app is explicitly a contract fixture and makes no historical-data or calibration claim. |
