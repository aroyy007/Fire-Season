# Fire Season design system

Fire Season is a trust-first monitoring instrument, not a marketing landing page. Its visual language comes from field notebooks, satellite operator consoles, and printed scientific briefs: deliberate alignment, visible evidence boundaries, and one memorable heatmap.

## Tokens

| Token | Value | Use |
|---|---|---|
| Paper | `#f2f5f3` | page substrate |
| Surface | `#ffffff` | evidence panels and controls |
| Basalt | `#182a30` | primary text and structural rules |
| Slate | `#52656b` | secondary text and metadata |
| Ember | `#b94a2c` | activity intensity and the single action accent |
| Signal blue | `#2c6674` | links, focus context, and non-activity status |

The app uses system sans-serif text for reliable offline rendering and a monospace face only for telemetry values. It avoids gradients, remote fonts, decorative AI chat surfaces, and cards that do not communicate hierarchy.

## Component rules

- The calendar is the opening instrument. It keeps the 12-month matrix on wide screens and switches to a selected-year vertical list on narrow screens.
- The seasonal pulse is a compact context strip, not a dashboard KPI wall. It reports mean rate, typical months, support, and release status.
- The 10 km heatmap is the visual signature. Ember opacity encodes native-rate rank within the selected month; hatching means no usable observation; a blue outline marks the selected block. The equivalent table remains visible for exact reading.
- Evidence panels show counts before interpretation: eligible, valid, detected, rate, and support. Comparable Activity remains a plain unavailable state until release gates pass.
- Receipt details expose provider objects, checksums, exclusions, files, calibration state, and limitations in one place.
- Motion answers actions only: pressed controls, selected cells, and focus return. Reduced-motion users receive the same information without animation.

The design deliberately spends visual emphasis on the heatmap and evidence receipt. Everything else stays quiet so a judge can understand what the artifact proves and what it does not.
