# Fire Season science-integrity implementation

## Problem

The current generated bundle contains hash-seeded month counts and spatial offsets, while a weak full-tile ratio fit is marked as a released calibration. The app therefore displays values that do not describe the selected region and overstates what has been evaluated.

## Outcome

The browser bundle contains only measurements derived from stored NASA MYD14A1 and VNP14A1 granules, or explicit unavailable states. A March 2023 sample is clipped to the existing candidate analysis windows, uses the documented product QA policy, and carries source-file checksums. Native records remain visible; Comparable Activity stays unavailable until the pre-registered temporal, spatial, overlap, and uncertainty gates pass. Spatial cells come from actual raster pixels grouped on the native tile grid.

## Boundaries

- Candidate Science Pilot bounds: 93.0–96.0°E, 23.0–26.5°N, inherited from `build_timeseries.py`.
- Candidate Chattogram bounds: 91.4–92.7°E, 20.6–23.2°N, inherited from the current local-region artifact.
- These are working windows for a raster-processing proof, not organizer-approved or final Curated Regions.
- Initial sample: March 2023 only. Other months and years are omitted/visibly unavailable, never filled from a fixture.
- Low-confidence fire, cloud, unknown, unprocessed, water, and non-land pixels do not contribute to the primary valid/detected counts. QA land state defines eligible land support; clear non-fire land and nominal/high fire define valid support; nominal/high fire define detections.
- The artifact is native-only. No calibration estimate, anomaly, forecast, or priority score is released.

## Acceptance

1. A regression test proves no monthly values are generated from a hash or extrapolated denominator.
2. Decoder tests cover mask/QA policy, AOI clipping, exact month trimming, complete daily coverage, and 10×10 native-grid aggregation.
3. The checked-in March 2023 bundle contains real decoded counts and real source checksums for both sensors and both candidate windows.
4. Missing dates fail closed; incomplete months are not represented as complete samples.
5. Calibration output cannot reach `released` without independently supplied evaluation-gate evidence; current data remain experimental.
6. The UI labels the sample and candidate boundaries plainly, and its map/export values resolve to the same raster-derived data.
7. Contract, package, UI syntax, and test checks pass.
