# Make the real sample reproducible

Status: ready-for-agent

## Goal

Document and verify the exact command, dependencies, source coverage checks, and artifact-generation workflow for the stored granules.

## Acceptance criteria

- A dependency lock identifies the geospatial/HDF runtime used for analysis.
- A single documented command rebuilds the compact static artifact offline.
- Tests cover classification, clipping, coverage, calibration abstention, schema, and payload checksums.
- Implementation status describes actual rather than planned work.

## Comments

- Implemented with a pinned science-analysis requirements file and offline rebuild command. Release fingerprints bind inputs, region revision, code, schema, lockfile, and runtime; identical rebuilds reuse existing artifacts without rewriting receipts.
