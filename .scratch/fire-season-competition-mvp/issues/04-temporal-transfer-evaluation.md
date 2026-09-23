# 04: Evaluate the transfer candidate against temporal baselines

**What to build:** Add the transparent model ladder and frozen temporal evaluation to the science artifact. The analyst can inspect identity, seasonal baseline, and grouped-binomial-GLM results, including held-out error, bias, peak timing, interval coverage, and release-gate status. Results stay experimental until geographic transfer is tested.

**Blocked by:** 02: Browse the Science Pilot native seasonal calendar.

**Status:** ready-for-agent

- [ ] Identity and seasonal baselines are scored on a declared temporal split.
- [ ] The grouped binomial GLM is fitted only when paired support and positive-example gates are met.
- [ ] Held-out metrics and interval diagnostics are stored in an evaluation artifact.
- [ ] The artifact marks the candidate experimental unless every required release gate is evaluated.
- [ ] A failing gate produces an explicit Unavailable Comparison rather than a modeled value.

**Implementation note:** No model is fitted in the fixture pass. The UI and contract preserve the Unavailable Comparison state until paired-mask and held-out evaluation gates are implemented.
