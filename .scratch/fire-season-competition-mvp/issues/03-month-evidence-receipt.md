# 03: Inspect a month and trace its evidence

**What to build:** Let a Monitoring Analyst select a calendar month and inspect its Native Sensor Records, Observation Support, descriptive Activity Anomaly, Evidence Receipt, and matching CSV export. The selected values must come from the same Analysis Artifact shown in the calendar.

**Blocked by:** 02: Browse the Science Pilot native seasonal calendar.

**Status:** ready-for-agent

- [ ] Selecting a month opens an evidence panel with product values, support counts, exclusions, and units.
- [ ] The anomaly compares the selected month with the same calendar month while excluding the selected year.
- [ ] The Evidence Receipt identifies sources, checksums, policy, region, period, and limitations.
- [ ] CSV export values match the selected artifact month exactly.
- [ ] The selected month remains keyboard reachable and focus returns after the evidence panel closes.

**Implementation note:** The fixture app includes selected-month evidence, receipt JSON, CSV export, keyboard calendar movement, and return focus. Values are generated from the same bundled Analysis Artifact.
