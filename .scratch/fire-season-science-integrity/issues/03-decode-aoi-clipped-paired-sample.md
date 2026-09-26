# Decode an AOI-clipped paired sample

Status: ready-for-agent

## Goal

Decode March 2023 MYD14A1 and VNP14A1 masks for both candidate windows, using QA-aware pixel classification and exact spatial/temporal clipping.

## Acceptance criteria

- Use pixel centers on verified tile coordinates and the documented AOI inclusion rule.
- Exclude low-confidence, cloud, unknown, unprocessed, water, and non-land pixels from primary valid/detected counts.
- Preserve per-product valid, eligible, detected, and coverage counts.
- Fail when paired month coverage is incomplete or grid alignment is outside tolerance.

## Comments

- Implemented the March 2023 paired sample from 5 MYD14A1 and 31 VNP14A1 granules. Both candidate windows use pixel-center AOI masks, product QA rules, daily coverage checks, and a verified shared grid; generated receipts record exclusions and source checksums.
- March 2023 chosen because both source archives are present locally with full month coverage.
