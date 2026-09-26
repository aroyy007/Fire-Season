# Keep unsupported calibration experimental

Status: ready-for-agent

## Goal

Prevent a fitted monthly ratio or a fixed-width interval from being published as Comparable Activity.

## Acceptance criteria

- Candidate fitting and evaluation are separate from release authorization.
- Release requires the documented temporal holdout, geographic transfer test, paired support, baseline skill, and interval coverage checks.
- With current evidence, calibration and all comparison estimates remain null with an explicit reason.

## Comments

- Removed the automatic ratio release. The artifact contract now requires linked evaluation evidence, all named sub-gates, minimum season/block/support counts, 10% improvement over the best simple baseline, interval coverage, a distinct transfer-region ID in the declared domain, matching artifact/receipt calibration provenance, matching evaluation payload checksums, and checksummed model/training/split files before any available comparison can validate.
- Transfer release evidence now includes a separate GeoJSON reference, SHA-256, region ID, and bounds. The contract reads the actual target and transfer GeoJSON payloads, checks feature IDs and coordinate bounds, and rejects geographic overlap. Existing-release reuse also requires artifact, receipt, manifest, and on-disk file metadata to agree.
