# Replace the display heatmap with raster-derived blocks

Status: ready-for-agent

## Goal

Build spatial values by grouping the reference product's actual aligned native pixels into 10×10-cell blocks.

## Acceptance criteria

- Every block numerator, denominator, support fraction, and rate derives from decoded AOI pixels.
- Block row/column IDs use stable native tile coordinates.
- No synthetic rate offsets or made-up 3×4 block grid remain in the bundle.
- No investigation-priority score appears without a separately declared, evaluated rule.

## Comments

- Implemented for the 2023-03 sample; priority remains unavailable.
