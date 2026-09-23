# 01: Show Native Sensor Records from one paired sample

**What to build:** Create a small, real-data-shaped Analysis Artifact from one paired Aqua MODIS and Suomi-NPP VIIRS sample and show both Native Sensor Records in a minimal static view. The result must expose detected and valid land-cell-days, Observation Support, product identity, and source provenance without implying Comparable Activity.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] A reproducible fixture or downloaded paired sample identifies both products, dates, region revision, and checksums.
- [ ] Product-specific values are decoded into semantic observation states without collapsing no observation and observed non-fire.
- [ ] The published Analysis Artifact validates against the artifact contract and contains native monthly records.
- [ ] A minimal browser view loads the artifact and displays the two Native Sensor Records with units and support.
- [ ] A contract check catches missing provenance and invalid count/rate relationships.

**Implementation note:** The dependency-free contract validator and deterministic paired-record fixture are in `pipeline/fireseason/contract.py` and `pipeline/fireseason/demo.py`. A real decoded NASA sample remains the science gate.
