# 06: Inspect 10 km blocks and Investigation Priorities

**What to build:** Add a compact geographic view and equivalent table for the 10 km analysis blocks. A Monitoring Analyst can inspect block support, activity, comparison status, and a declared Investigation Priority for human review.

**Blocked by:** 05: Test the Local Impact Case and release or withhold Comparable Activity.

**Status:** ready-for-agent

- [ ] Block-month records are present in the Analysis Artifact or its verified payload.
- [ ] The context map and block table identify the same selected block and values.
- [ ] Investigation Priority is computed from released artifact rules and has a reason.
- [ ] Unavailable support cannot receive a misleading review priority.
- [ ] The table remains usable when the map is unavailable.

**Implementation note:** The fixture app ships a map placeholder plus equivalent 10 km block table and explicitly marks priority unavailable. A released rule is still required before assigning a real priority.
