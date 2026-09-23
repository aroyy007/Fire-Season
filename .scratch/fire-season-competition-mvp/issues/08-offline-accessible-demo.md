# 08: Release an offline, accessible demo and validate the main tasks

**What to build:** Package the complete Fire Season flow as a public static build and local fallback. A judge can use the calendar, evidence panel, comparison status, block table, receipt, exports, and Monitoring Brief without network access. The team records accessibility and task-based usability results.

**Blocked by:** 07: Create a Monitoring Brief from selected evidence.

**Status:** ready-for-agent

- [ ] The built application completes the primary flow with network access disabled.
- [ ] Keyboard navigation, focus return, text alternatives, contrast, narrow layout, and reduced motion are verified.
- [ ] Browser and export values match the released Analysis Artifact.
- [ ] Five representative testers attempt the three defined tasks and results are recorded.
- [ ] Public static deployment and local fallback links work without login or paid service.

**Implementation note:** The zero-dependency `app/` shell and generated `data.js` bundle run from a static server without runtime network calls or paid services. Five-person usability and public deployment checks remain open.
