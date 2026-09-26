# Align app language with the available sample

Status: ready-for-agent

## Goal

Make the product interface accurately communicate its one-month, native-only, candidate-window evidence.

## Acceptance criteria

- The interface identifies the March 2023 research sample and boundary status.
- Unprocessed months show no data instead of reusing a nearby record.
- Comparable Activity, anomaly, and priority remain unavailable without passing gates.
- Heatmap, CSV, JSON, and receipt values come from the same artifact.

## Comments

- Implemented as an explicit sample banner, sparse-month states, and real block values.
