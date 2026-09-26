# Implemented features and current limits

This document describes what the repository runs today. The larger product scope in the [PRD](01-PRD.md) and [TRD](02-TRD.md) is a target specification. The actual implementation is the stored, QA-filtered March 2023 raster sample and the static browser application described here.

## Current release

| Item | Implemented value |
|---|---|
| Data period | March 1–31, 2023 |
| Science products | Aqua MODIS MYD14A1 Collection 6.1; Suomi-NPP VIIRS VNP14A1 Version 2 |
| Coverage | 31 of 31 calendar days for each product in each candidate window |
| Granules | Five MYD14A1 eight-day granules and 31 VNP14A1 daily granules per sample build |
| Regions | Northeast India–Myanmar Science Pilot candidate; Chattogram Hills and Cox's Bazar Local Impact Case candidate |
| Region state | Both boundaries are candidate windows at revision 2; neither is frozen by the team or local event |
| Artifact state | `native_only`; no Calibration Release |
| Browser delivery | Static HTML, CSS, and JavaScript with bundled, versioned artifacts |
| Runtime services | No database, live API, Earthdata login, hosted model, or map service |

Each regional artifact includes a monthly CSV, a block-month CSV, an `evaluation.json` marked `not_evaluated`, a GeoJSON candidate window, a printable HTML brief, an Analysis Artifact, an Evidence Receipt, and a checksum manifest. `app/data.js` contains the records used by the UI.

## Data processing features

### Real file decoding

The build reads locally stored NASA raster files from `data/timeseries/modis/` and `data/timeseries/viirs/`. It reads MODIS HDF4 and VIIRS HDF5 structures using the product-specific code in `pipeline/fireseason/decoder.py` and `pipeline/fireseason/raster_analysis.py`. The source records identify each product and platform. The sample is derived from raster pixels, not generated fixtures or hash-seeded counts.

This is a local-data build. The repository's current sample builder does not query NASA CMR or download new granules. Local retrieval timestamps were not preserved, so the Evidence Receipt records that provenance gap rather than inventing a retrieval time.

### QA and observation semantics

Each pixel-day is classified under `firemask-qa-land-highnominal-v1`:

| Raster meaning | Eligible land support | Valid observed support | Detected count |
|---|---:|---:|---:|
| QA identifies land and FireMask is clear non-fire (`5`) | yes | yes | no |
| QA identifies land and FireMask is nominal/high-confidence fire (`8` or `9`) | yes | yes | yes |
| Low-confidence fire (`7`) | yes | no | no |
| Cloud, unknown, or unprocessed land | yes | no | no |
| Water or non-land | no | no | no |
| Outside the candidate region | no | no | no |

The primary rate is:

```text
detected activity rate = 1,000 × detected active land-cell-days / valid observed land-cell-days
```

The support fraction is `valid observed land-cell-days / eligible land-cell-days`. When valid support is zero, a rate is null; zero detections with positive valid support are a measured zero. Product-specific values remain separate.

### Spatial clipping and blocks

The pipeline maps native pixel centers into the shared h26v06 sinusoidal grid, clips them against the candidate bounding boxes, and checks that the source grids align. Region bounds are projected with densified edges before the pixel-center point-in-polygon test. The build fails if it sees a missing or duplicate day, a grid mismatch, or an incompatible raster shape.

The app's geographic context uses Aqua MYD14A1 reference-product counts aggregated to 10×10 native cells. At this grid, a block is roughly 9.3 km; it is not an exact equal-area 10 km square. The heatmap color scale is relative within the displayed sample. A separate table exposes each block's coordinates, detected rate, valid and detected counts, and support fraction.

## Browser features

| Feature | Current behavior |
|---|---|
| Candidate region selector | Switches between the two bundled candidate windows and shows their bounds and role. The UI says the boundaries are not frozen. |
| Burning Activity Calendar | Shows the sampled March 2023 rate in a year-by-month grid. Unprocessed months have a distinct missing state and explanatory copy; they do not become zero observations. |
| Native Sensor Records view | Shows MYD14A1 and VNP14A1 records separately, including eligible, valid, and detected cell-days, a per-1,000 rate, observation status, and support meter. |
| Comparable Activity view | Shows the current release state and the specific reason comparison is unavailable. It does not substitute one sensor's rate for another or display an experimental estimate. |
| Selected-month evidence panel | Displays comparison status, anomaly status, reference-product identity, and the native records for the selected month. In this single-month release, the anomaly is indeterminate. |
| Aqua reference heatmap | Shows selectable 10×10 native-grid blocks, a relative-rate legend, and the selected block's value and support. |
| Block detail table | Lists the published Aqua reference blocks with geographic coordinates, rates, valid/detected cell-days, and support. |
| Evidence Receipt | Exposes artifact and receipt IDs, candidate region revision, period, daily coverage, source manifest identity, quality policy, source objects, exclusions, file checksums, environment, and limits. |
| Exports | Downloads the calendar as CSV and the receipt as JSON. The user can open a print-ready Monitoring Brief from the selected evidence. |
| Keyboard and small screens | Calendar cells can be reached and moved through with the keyboard. The small-screen view changes the grid into a selected-year month list. Receipt focus is returned to its opener when closed. |

The app is usable offline once served locally because the artifacts, styles, and scripts are bundled. No remote font, tile server, analytics, API, or LLM is needed.

## Provenance and publication safeguards

The build creates a source manifest identity from the local input objects and binds the artifact identity to the selected sample, code, schemas, dependency lock, runtime, region revision, and geometry. Payload files carry SHA-256 checksums. The Evidence Receipt links scientific interpretation to its inputs and exclusions. The final manifest records the published file inventory and checksums.

Publication uses a temporary release directory and renames it into place only after the bundle passes validation. Rebuilding an identical artifact verifies the existing files and reuses that immutable release. Changing a region's geometry without incrementing its revision fails the build. Contract validation rejects invalid counts, impossible support fractions, unsafe file references, mismatched geometry, or an artifact/receipt/manifest disagreement.

## Not implemented in this release

These items appear in planning documents but are not implemented as functioning analytical results in the current app:

- Multi-year or multi-season raster processing and a historical fire calendar.
- A trained or released MODIS-to-VIIRS calibration model, eligible Comparable Activity estimate, or calibrated uncertainty interval.
- An independent temporal holdout, independent geographic transfer test, or reference-data assessment.
- A seasonal pattern, Activity Anomaly, validated Investigation Priority, field outcome, fire-risk score, alert, prediction, or causality claim.
- Live NASA CMR discovery/download, FIRMS recent-fire overlays, weather, burned-area corroboration, editable polygons, user accounts, hosted APIs, database writes, or live collaboration.
- LLM-generated explanations or autonomous agents. The deterministic Evidence Receipt and fixed brief are the current explanation and provenance tools.

The `calibrator.py` module can calculate exploratory monthly-ratio diagnostics when passed time-series records, but it always marks the output experimental and cannot issue a Calibration Release. Its presence does not mean the app has a working calibration model.

## Build and validation

From the repository root:

```sh
python3 -m venv venv
venv/bin/python -m pip install -r pipeline/requirements-science.lock
venv/bin/python pipeline/build_research_bundle.py
venv/bin/python -m unittest discover -s pipeline/tests -v
node --check app/app.js
python3 scripts/check_package.py
```

See [implementation status](09-IMPLEMENTATION-STATUS.md) for the measured sample details and outstanding research gates, and the [root README](../README.md) for quick app startup.
