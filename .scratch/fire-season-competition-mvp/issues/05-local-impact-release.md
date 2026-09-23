# 05: Test the Local Impact Case and release or withhold Comparable Activity

**What to build:** Evaluate the Chattogram Hill Tracts and adjacent Cox's Bazar candidate as a separate Local Impact Case. The application shows Comparable Activity only when the calibration scope and transfer evidence pass; otherwise it explains the Unavailable Comparison and preserves native evidence.

**Blocked by:** 03: Inspect a month and trace its evidence; 04: Evaluate the transfer candidate against temporal baselines.

**Status:** ready-for-agent

- [ ] The Local Impact Case has its own region revision, support summary, and source manifest.
- [ ] Geographic transfer evaluation is reported separately from temporal held-out evaluation.
- [ ] An eligible released calibration is the only path to a Comparable Activity value.
- [ ] Unsupported local months and regions expose a reasoned Unavailable Comparison.
- [ ] The UI makes the Science Pilot and Local Impact Case roles clear.

**Implementation note:** Both curated regions are published as separate fixture bundles and selectable in the app. Comparable Activity stays withheld for both until a released calibration and local transfer evaluation exist.
