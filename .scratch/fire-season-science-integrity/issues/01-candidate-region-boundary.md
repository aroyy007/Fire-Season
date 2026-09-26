# Candidate analysis-window boundary

Status: ready-for-human

## Goal

Record the two current bounding boxes as candidate raster-analysis windows without describing them as final curated or organizer-approved regions.

## Acceptance criteria

- GeoJSON and receipts identify each geometry as a candidate analysis window.
- The app states the exact bounds and that local organizers/team have not frozen them.
- A later human decision can replace the bounds by a new region revision without rewriting old receipts.

## Implementation note

Use the existing Science Pilot search box and Chattogram local-case box only to prove the raster workflow; do not infer that either is the final challenge AOI.

## Comments

- Implemented as revision 2 candidate geometries; final organizer/team confirmation remains open. Region IDs derive from the explicit revision, and each region/source/code fingerprint publishes to an immutable versioned path. A geometry change within the same revision fails closed.
