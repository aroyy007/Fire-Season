# Remove synthetic values from scientific bundles

Status: ready-for-agent

## Goal

Ensure generated app data never turns deterministic fixtures, guessed denominators, or display offsets into apparent scientific observations.

## Acceptance criteria

- No hash-based value generation is used by the publisher.
- Months without processed evidence are omitted or explicitly unavailable with null measurements.
- Any retained contract fixture is isolated from the generated scientific bundle and labeled as test-only.

## Comments

- Implemented by replacing the app bundle source with the real raster sample builder.
