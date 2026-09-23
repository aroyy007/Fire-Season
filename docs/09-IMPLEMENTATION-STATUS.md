# Implementation status

This is the first executable pass of the Fire Season Competition MVP. It deliberately implements the public artifact contract and the product states before claiming any scientific result.

## What is executable now

- `pipeline/fireseason/contract.py` validates Analysis Artifacts and Evidence Receipts, including native-rate arithmetic and unavailable-comparison invariants.
- `pipeline/fireseason/demo.py` creates deterministic contract fixtures for the Science Pilot and Local Impact Case. The values are illustrative and are marked as such in the UI.
- `pipeline/build_demo_artifact.py` publishes both regions as portable release bundles with CSV, GeoJSON, HTML, JSON, and checksum manifests.
- `app/` is a zero-dependency static browser shell. It supports native/comparable view states, selected-month evidence, receipt inspection, CSV/JSON export, printable Monitoring Brief output, keyboard calendar movement, a narrow-screen month list, a seasonal pulse summary, and a selectable 10 km activity heatmap with a table alternative. This prototype intentionally avoids a React/Vite build step until a real paired sample justifies freezing the production frontend stack; the TRD remains the target implementation architecture.

Run the fixture build and checks from the repository root:

```sh
python3 pipeline/build_demo_artifact.py
python3 -m unittest discover -s pipeline/tests -v
node --check app/app.js
python3 scripts/check_package.py
```

Serve `app/` with any static server to inspect the browser flow. The generated `app/data.js` bundle contains all data needed after the initial page load; the app does not fetch a runtime API or remote font.

## What remains behind the science gate

The fixture does not decode NASA granules, fit a MODIS–VIIRS transfer, or claim a released Calibration Release. Tickets 01–03 and 07–08 have executable contract-level coverage. Tickets 04–06 remain ready for the real-data work: paired historical masks, QA/overlap/transfer evaluation, held-out uncertainty, a declared local transfer test, and defensible block-level priority rules.

The first real bundle must preserve the same public schemas and replace `fixture_status` with a release status backed by an Evidence Receipt. A numeric Comparable Activity estimate must never appear without a released calibration and passing evaluation gates.
