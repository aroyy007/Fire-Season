/* global FIRE_SEASON_DATA */

(function () {
  "use strict";

  const DATA = window.FIRE_SEASON_DATA;
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const FULL_MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const state = {
    region: "science",
    view: "native",
    selectedMonth: "2024-03",
    selectedBlock: null,
    receiptOpen: false,
    receiptFocus: null,
  };

  const app = document.getElementById("app");

  function artifact() {
    return DATA.artifacts[state.region];
  }

  function receipt() {
    return DATA.receipts[state.region];
  }

  function monthRecord(monthKey) {
    return artifact().months.find((month) => month.month === monthKey) || artifact().months[0];
  }

  function yearList() {
    return [...new Set(artifact().months.map((month) => month.month.slice(0, 4)))];
  }

  function nativeRecord(month, productId) {
    return month.native_records.find((record) => record.product_id === productId);
  }

  function referenceRecord(month) {
    return nativeRecord(month, artifact().reference_product_id) || month.native_records[0];
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function formatRate(value) {
    return value == null ? "—" : Number(value).toFixed(1);
  }

  function formatPercent(value) {
    return `${Math.round(Number(value) * 100)}%`;
  }

  function formatCount(value) {
    return value == null ? "—" : Number(value).toLocaleString("en-US");
  }

  function typicalMonths() {
    const totals = Array.from({ length: 12 }, () => ({ total: 0, count: 0 }));
    artifact().months.forEach((month) => {
      const record = referenceRecord(month);
      if (record.rate_per_1000 != null) {
        const index = Number(month.month.slice(5, 7)) - 1;
        totals[index].total += Number(record.rate_per_1000);
        totals[index].count += 1;
      }
    });
    return totals
      .map((entry, index) => ({ index, average: entry.count ? entry.total / entry.count : -1 }))
      .sort((left, right) => right.average - left.average)
      .slice(0, 3)
      .filter((entry) => entry.average >= 0)
      .map((entry) => FULL_MONTHS[entry.index]);
  }

  function formatDateLabel(monthKey) {
    const [year, month] = monthKey.split("-");
    return `${FULL_MONTHS[Number(month) - 1]} ${year}`;
  }

  function productLabel(productId) {
    const source = artifact().sources.find((entry) => entry.product_id === productId);
    return source ? `${source.short_name} · ${source.platform}` : productId;
  }

  function cellValue(month) {
    if (state.view === "comparable") {
      return month.comparison.estimate_per_1000;
    }
    return referenceRecord(month).rate_per_1000;
  }

  function cellState(month) {
    if (state.view === "comparable") {
      return month.comparison.status === "available" ? "available" : "unavailable";
    }
    const record = referenceRecord(month);
    if (record.observation_status === "no_observation") return "no-observation";
    if (record.observation_status === "insufficient_support") return "low-support";
    if (record.rate_per_1000 === 0) return "zero";
    return "observed";
  }

  function cellLabel(month) {
    const record = referenceRecord(month);
    if (state.view === "comparable") {
      const comparison = month.comparison;
      if (comparison.status !== "available") {
        return `${formatDateLabel(month.month)}; comparison unavailable; ${comparison.reason}`;
      }
      return `${formatDateLabel(month.month)}; Comparable Activity ${formatRate(comparison.estimate_per_1000)} per 1,000; interval ${formatRate(comparison.lower_90)} to ${formatRate(comparison.upper_90)}.`;
    }
    if (record.observation_status === "no_observation") {
      return `${formatDateLabel(month.month)}; no usable observations in ${productLabel(record.product_id)}.`;
    }
    return `${formatDateLabel(month.month)}; ${productLabel(record.product_id)} Native Sensor Record ${formatRate(record.rate_per_1000)} per 1,000; ${formatPercent(record.support_fraction)} valid support.`;
  }

  function render() {
    const current = artifact();
    app.innerHTML = `
      <div class="shell">
        <header class="topbar">
          <a class="wordmark" href="#" aria-label="Fire Season home">Fire Season<span class="wordmark-dot">.</span></a>
          <div class="topbar-meta"><span>One Last Launch</span><span class="status-dot" aria-hidden="true"></span><span>offline artifact demo</span></div>
          <button class="text-button" data-action="receipt">Evidence receipt</button>
        </header>

        <section class="intro" aria-labelledby="page-title">
          <div>
            <p class="kicker">NASA Space Apps · Harmonization of MODIS and VIIRS Hot Spots</p>
            <h1 id="page-title">Did recorded burning change, or did the observing system change?</h1>
            <p class="intro-copy">A seasonal calendar that keeps each satellite record visible and states when a comparison has not earned release.</p>
          </div>
          <div class="region-picker">
            <label for="region-select">Curated Region</label>
            <select id="region-select" data-action="region">
              ${DATA.index.regions.map((entry) => `<option value="${entry.key}" ${entry.key === state.region ? "selected" : ""}>${escapeHtml(entry.name)}</option>`).join("")}
            </select>
            <span class="region-role">${current.region.role === "science_pilot" ? "Science Pilot" : "Local Impact Case"}</span>
          </div>
        </section>

        <div class="fixture-banner" role="note">
          <span class="banner-mark">i</span>
          <span><strong>Contract fixture.</strong> These bundled values rehearse the product states. No historical raster has been decoded and no Calibration Release is present.</span>
          <a href="../docs/03-MODEL-AND-DATA-PROTOCOL.md">Read the evidence boundary</a>
        </div>

        <section class="instrument" aria-labelledby="calendar-heading">
          <div class="instrument-head">
            <div>
              <p class="section-label">Burning Activity Calendar</p>
              <h2 id="calendar-heading">${escapeHtml(current.region.name)}</h2>
              <p class="measurement">${escapeHtml(current.metric.unit)} · ${current.period.start_date.slice(0, 4)}–${current.period.end_date.slice(0, 4)}</p>
            </div>
            <div class="view-control" role="group" aria-label="Measurement view">
              <button class="view-button ${state.view === "native" ? "is-active" : ""}" data-action="view" data-view="native">Native Sensor Records</button>
              <button class="view-button ${state.view === "comparable" ? "is-active" : ""}" data-action="view" data-view="comparable">Comparable Activity</button>
            </div>
          </div>
          <div class="era-note"><span class="era-line"></span><span>Sensor-era boundary will be asserted only after paired historical masks pass QA. Product identity stays visible in every record.</span></div>
          <div class="calendar-wrap">
            <div class="calendar" role="grid" aria-label="${escapeHtml(current.region.name)} burning activity calendar">
              <div class="calendar-corner" aria-hidden="true">Year</div>
              ${MONTHS.map((month) => `<div class="month-heading" role="columnheader">${month}</div>`).join("")}
              ${yearList().map((year) => renderYearRow(year)).join("")}
            </div>
          </div>
          ${renderMobileCalendar()}
          <div class="legend" aria-label="Calendar legend">
            <span class="legend-item"><span class="legend-swatch activity-low"></span> lower detected rate</span>
            <span class="legend-item"><span class="legend-swatch activity-high"></span> higher detected rate</span>
            <span class="legend-item"><span class="legend-swatch hatch"></span> comparison unavailable / weak support</span>
            <span class="legend-item"><span class="legend-swatch zero-mark">0</span> observed zero</span>
          </div>
        </section>

        <section class="evidence-grid" aria-label="Selected month evidence">
          ${renderEvidencePanel(monthRecord(state.selectedMonth))}
          ${renderContextPanel(monthRecord(state.selectedMonth))}
        </section>

        ${state.receiptOpen ? renderReceiptPanel() : ""}

        <footer class="footer">
          <span>Fire Season · contract fixture ${escapeHtml(current.artifact_id)}</span>
          <span>NASA data sources remain under their own terms.</span>
        </footer>
      </div>
    `;
    bindEvents();
    if (!state.receiptOpen && state.receiptFocus) {
      const returnTarget = state.receiptFocus === "panel"
        ? app.querySelector(".panel-actions [data-action='receipt']")
        : app.querySelector(".topbar [data-action='receipt']");
      returnTarget?.focus();
      state.receiptFocus = null;
    }
  }

  function renderYearRow(year) {
    const cells = MONTHS.map((_, index) => {
      const key = `${year}-${String(index + 1).padStart(2, "0")}`;
      const month = monthRecord(key);
      const value = cellValue(month);
      const intensity = value == null ? 0 : Math.min(100, Math.max(8, (Number(value) / 55) * 100));
      const selected = state.selectedMonth === key;
      return `<button class="calendar-cell ${cellState(month)} ${selected ? "is-selected" : ""}" style="--intensity:${intensity}%" data-action="month" data-month="${key}" role="gridcell" aria-selected="${selected}" aria-label="${escapeHtml(cellLabel(month))}"><span class="cell-bar" aria-hidden="true"></span><span class="cell-value">${escapeHtml(formatRate(value))}</span></button>`;
    }).join("");
    return `<div class="year-label" role="rowheader">${year}</div>${cells}`;
  }

  function renderMobileCalendar() {
    const selectedYear = state.selectedMonth.slice(0, 4);
    const yearOptions = yearList().map((year) => `<option value="${year}" ${year === selectedYear ? "selected" : ""}>${year}</option>`).join("");
    const months = artifact().months.filter((month) => month.month.startsWith(`${selectedYear}-`));
    return `<div class="mobile-calendar" aria-label="${escapeHtml(artifact().region.name)} selected year list"><div class="mobile-year-picker"><label for="mobile-year">Selected year</label><select id="mobile-year" data-action="mobile-year">${yearOptions}</select></div><div class="mobile-month-list" role="list">${months.map((month) => `<button class="mobile-month ${cellState(month)} ${state.selectedMonth === month.month ? "is-selected" : ""}" data-action="month" data-month="${month.month}" role="listitem" aria-label="${escapeHtml(cellLabel(month))}"><span>${formatDateLabel(month.month)}</span><strong>${formatRate(cellValue(month))}</strong><small>${escapeHtml(cellLabel(month).split(";").slice(1).join(";").trim())}</small></button>`).join("")}</div></div>`;
  }

  function renderEvidencePanel(month) {
    const comparison = month.comparison;
    const anomaly = month.anomaly;
    return `<article class="evidence-panel panel" aria-labelledby="evidence-title">
      <div class="panel-heading"><div><p class="section-label">Selected month</p><h2 id="evidence-title" tabindex="-1">${formatDateLabel(month.month)}</h2></div><span class="status-pill ${comparison.status === "available" ? "pill-ok" : "pill-muted"}">${comparison.status === "available" ? "comparison available" : "comparison unavailable"}</span></div>
      <div class="native-list">
        ${month.native_records.map((record) => `<div class="native-row"><div><strong>${escapeHtml(productLabel(record.product_id))}</strong><span>${escapeHtml(record.observation_status.replaceAll("_", " "))}</span><small class="record-counts">eligible ${formatCount(record.eligible_land_cell_days)} · valid ${formatCount(record.valid_cell_days)} · detected ${formatCount(record.detected_cell_days)}</small></div><div class="native-number"><strong>${formatRate(record.rate_per_1000)}</strong><span>per 1,000</span></div><div class="support-meter"><span style="width:${Math.round(record.support_fraction * 100)}%"></span><small>${formatPercent(record.support_fraction)} support</small></div></div>`).join("")}
      </div>
      <div class="comparison-callout ${comparison.status === "available" ? "callout-ok" : "callout-muted"}"><div><span class="callout-label">Comparable Activity</span><strong>${comparison.status === "available" ? `${formatRate(comparison.estimate_per_1000)} per 1,000` : "Unavailable"}</strong></div><p>${escapeHtml(comparison.reason || `90% interval ${formatRate(comparison.lower_90)}–${formatRate(comparison.upper_90)}.`)}</p></div>
      <div class="detail-grid">
        <div><span class="detail-label">Activity Anomaly</span><strong>${anomaly.status === "available" ? `${anomaly.difference_per_1000 > 0 ? "+" : ""}${formatRate(anomaly.difference_per_1000)} vs baseline` : "Indeterminate"}</strong><small>${escapeHtml(anomaly.reason || `${anomaly.usable_baseline_years} same-month baseline years`)}</small></div>
        <div><span class="detail-label">Reference Product</span><strong>${escapeHtml(productLabel(artifact().reference_product_id))}</strong><small>native record remains separate from estimates</small></div>
      </div>
      <div class="panel-actions"><button class="outline-button" data-action="receipt">Open evidence receipt</button><button class="outline-button" data-action="csv">Download CSV</button><button class="outline-button" data-action="brief">Print Monitoring Brief</button></div>
    </article>`;
  }

  function renderContextPanel(month) {
    const blocks = DATA.blocks[state.region].filter((block) => block.month === month.month);
    return `<article class="context-panel panel" aria-labelledby="context-title">
      <div class="panel-heading"><div><p class="section-label">Geographic context</p><h2 id="context-title">10 km review blocks</h2></div><span class="context-tag">${escapeHtml(artifact().region.role.replaceAll("_", " "))}</span></div>
      <div class="map-placeholder" role="img" aria-label="Context map placeholder showing the selected Curated Region. The equivalent block table follows."><svg viewBox="0 0 360 170" aria-hidden="true"><rect x="8" y="8" width="344" height="154" rx="3" fill="#e8efec"/><path d="M64 125 L112 52 L188 36 L292 66 L318 126 L216 146 Z" fill="#c8dcd3" stroke="#2c6674" stroke-width="2"/><path d="M74 115 L132 78 M122 132 L180 49 M176 141 L222 51 M229 133 L265 64" stroke="#eff5f1" stroke-width="5" opacity=".9"/><circle cx="188" cy="86" r="7" fill="#b94a2c"/><text x="18" y="28" fill="#52656b" font-size="11">local geometry fixture</text></svg></div>
      <div class="table-wrap"><table><caption class="sr-only">Review blocks for ${formatDateLabel(month.month)}</caption><thead><tr><th>Block</th><th>Native rate</th><th>Support</th><th>Priority</th></tr></thead><tbody>${blocks.map((block) => `<tr class="${state.selectedBlock === block.block_id ? "row-selected" : ""}"><td><button class="table-link" data-action="block" data-block="${escapeHtml(block.block_id)}">${escapeHtml(block.block_id.split("_").slice(-2).join("·"))}</button></td><td>${formatRate(block.native_rate_per_1000)}</td><td>${formatPercent(block.support_fraction)}</td><td><span class="priority ${block.investigation_priority}">${block.investigation_priority}</span></td></tr>`).join("")}</tbody></table></div>
      <p class="table-note">Investigation Priority is unavailable until a calibration release or a separately declared native rule exists.</p>
    </article>`;
  }

  function renderReceiptPanel() {
    const current = receipt();
    const sourceRows = current.sources.map((source) => `<li><strong>${escapeHtml(source.short_name)} ${escapeHtml(source.version)}</strong> · ${escapeHtml(source.platform)} · ${source.provider_objects.map((object) => `${escapeHtml(object.provider_object_id)} (${escapeHtml(object.sha256)})`).join(", ")}</li>`).join("");
    const fileRows = current.files.map((file) => `<li>${escapeHtml(file.path)} · ${escapeHtml(file.sha256)} · ${formatCount(file.size_bytes)} bytes</li>`).join("");
    const exclusions = current.exclusions.length ? current.exclusions.map((item) => `<li>${escapeHtml(JSON.stringify(item))}</li>`).join("") : "<li>None declared.</li>";
    return `<section class="receipt-panel panel" id="receipt-panel" aria-labelledby="receipt-title"><div class="panel-heading"><div><p class="section-label">Provenance</p><h2 id="receipt-title">Evidence Receipt</h2></div><button class="close-button" data-action="receipt" aria-label="Close evidence receipt">×</button></div><dl class="receipt-grid"><div><dt>Receipt ID</dt><dd>${escapeHtml(current.receipt_id)}</dd></div><div><dt>Artifact ID</dt><dd>${escapeHtml(current.artifact_id)}</dd></div><div><dt>Region revision</dt><dd>${escapeHtml(current.region.region_id)}</dd></div><div><dt>Period</dt><dd>${current.analysis.start_date} → ${current.analysis.end_date}</dd></div><div><dt>Source manifest</dt><dd>${escapeHtml(current.analysis.source_manifest_id)} · ${escapeHtml(current.analysis.source_manifest_sha256)}</dd></div><div><dt>Quality policy</dt><dd>${escapeHtml(current.analysis.quality_policy_version)}</dd></div><div><dt>Calibration</dt><dd>${current.calibration ? "Released" : "None released"}</dd></div><div><dt>Environment</dt><dd>${escapeHtml(current.environment.pipeline_revision)}</dd></div></dl><div class="receipt-limitations"><h3>Source provider objects</h3><ul>${sourceRows}</ul><h3>Exclusions</h3><ul>${exclusions}</ul><h3>Files and checksums</h3><ul>${fileRows}</ul><h3>Limits recorded with this artifact</h3><ul>${current.limitations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div><div class="panel-actions"><button class="outline-button" data-action="receipt-json">Download receipt JSON</button></div></section>`;
  }

  function bindEvents() {
    app.querySelectorAll("[data-action='region']").forEach((element) => element.addEventListener("change", () => {
      state.region = element.value;
      state.selectedMonth = "2024-03";
      state.selectedBlock = null;
      render();
    }));
    app.querySelectorAll("[data-action='mobile-year']").forEach((element) => element.addEventListener("change", () => {
      state.selectedMonth = `${element.value}-01`;
      render();
      app.querySelector(".mobile-month.is-selected")?.focus();
    }));
    app.querySelectorAll("[data-action='view']").forEach((element) => element.addEventListener("click", () => {
      state.view = element.dataset.view;
      render();
    }));
    app.querySelectorAll("[data-action='month']").forEach((element) => {
      element.addEventListener("click", () => {
        state.selectedMonth = element.dataset.month;
        state.mobileYear = element.dataset.month.slice(0, 4);
        state.selectedBlock = null;
        render();
        document.getElementById("evidence-title")?.focus();
      });
      element.addEventListener("keydown", (event) => moveCell(event, element));
    });
    app.querySelectorAll("[data-action='block']").forEach((element) => element.addEventListener("click", () => {
      state.selectedBlock = element.dataset.block;
      render();
    }));
    app.querySelectorAll("[data-action='receipt']").forEach((element) => element.addEventListener("click", () => {
      state.receiptFocus = element.classList.contains("close-button") || element.closest(".panel-actions") ? "panel" : "top";
      state.receiptOpen = !state.receiptOpen;
      render();
      if (state.receiptOpen) document.getElementById("receipt-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }));
    app.querySelectorAll("[data-action='csv']").forEach((element) => element.addEventListener("click", downloadCsv));
    app.querySelectorAll("[data-action='receipt-json']").forEach((element) => element.addEventListener("click", downloadReceipt));
    app.querySelectorAll("[data-action='brief']").forEach((element) => element.addEventListener("click", printBrief));
  }

  function moveCell(event, current) {
    const cells = [...app.querySelectorAll("[data-action='month']")];
    const index = cells.indexOf(current);
    const columns = 12;
    let next = index;
    if (event.key === "ArrowRight") next = Math.min(cells.length - 1, index + 1);
    if (event.key === "ArrowLeft") next = Math.max(0, index - 1);
    if (event.key === "ArrowDown") next = Math.min(cells.length - 1, index + columns);
    if (event.key === "ArrowUp") next = Math.max(0, index - columns);
    if (next !== index) {
      event.preventDefault();
      cells[next].focus();
    }
  }

  function download(name, content, type) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    link.hidden = true;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  function downloadCsv() {
    const rows = ["month,product_id,observation_status,detected_cell_days,valid_cell_days,eligible_land_cell_days,support_fraction,rate_per_1000,comparison_status"];
    artifact().months.forEach((month) => month.native_records.forEach((record) => rows.push([month.month, record.product_id, record.observation_status, record.detected_cell_days ?? "", record.valid_cell_days, record.eligible_land_cell_days, record.support_fraction, record.rate_per_1000 ?? "", month.comparison.status].join(","))));
    download(`${artifact().artifact_id}-calendar.csv`, `${rows.join("\n")}\n`, "text/csv");
  }

  function downloadReceipt() {
    download(`${receipt().receipt_id}.json`, JSON.stringify(receipt(), null, 2), "application/json");
  }

  function printBrief() {
    const month = monthRecord(state.selectedMonth);
    const nativeRows = month.native_records.map((record) => `<tr><td>${escapeHtml(productLabel(record.product_id))}</td><td>${formatRate(record.rate_per_1000)}</td><td>${formatPercent(record.support_fraction)}</td><td>${escapeHtml(record.observation_status.replaceAll("_", " "))}</td></tr>`).join("");
    const blocks = DATA.blocks[state.region].filter((block) => block.month === month.month);
    const blockRows = blocks.map((block) => `<tr><td>${escapeHtml(block.block_id)}</td><td>${formatRate(block.native_rate_per_1000)}</td><td>${formatPercent(block.support_fraction)}</td><td>${escapeHtml(block.investigation_priority)}</td></tr>`).join("");
    const sourceRows = artifact().sources.map((source) => `<li>${escapeHtml(source.short_name)} ${escapeHtml(source.version)} · <a href="${escapeHtml(source.source_url)}">source</a></li>`).join("");
    const win = window.open("", "_blank");
    if (!win) return;
    win.document.write(`<!doctype html><html><head><title>Monitoring Brief · ${formatDateLabel(month.month)}</title><style>@page{size:A4;margin:14mm}body{font:14px system-ui;color:#182a30;max-width:820px;margin:40px auto;line-height:1.5}h1{font:32px Georgia}table{width:100%;border-collapse:collapse;margin:18px 0}td,th{border-bottom:1px solid #cbd5d2;padding:8px;text-align:left}.note{background:#eef4f0;padding:14px;border-left:4px solid #2c6674}</style></head><body><p>FIRE SEASON · MONITORING BRIEF</p><h1>${escapeHtml(formatDateLabel(month.month))}</h1><p>${escapeHtml(artifact().region.name)} · ${escapeHtml(artifact().region.role.replaceAll("_", " "))}</p><p>Analysis period: ${escapeHtml(artifact().period.start_date)} → ${escapeHtml(artifact().period.end_date)}<br>Typical higher-activity months: ${escapeHtml(typicalMonths().join(", ") || "Unavailable")}</p><div class="note"><strong>Comparison status:</strong> ${escapeHtml(month.comparison.status.replaceAll("_", " "))}. ${escapeHtml(month.comparison.reason)}<br><strong>Uncertainty:</strong> no interval is emitted until a calibration release passes evaluation gates.</div><h2>Native Sensor Records</h2><table><thead><tr><th>Product</th><th>Rate per 1,000</th><th>Support</th><th>Eligible</th><th>Valid</th><th>Detected</th><th>State</th></tr></thead><tbody>${month.native_records.map((record) => `<tr><td>${escapeHtml(productLabel(record.product_id))}</td><td>${formatRate(record.rate_per_1000)}</td><td>${formatPercent(record.support_fraction)}</td><td>${formatCount(record.eligible_land_cell_days)}</td><td>${formatCount(record.valid_cell_days)}</td><td>${formatCount(record.detected_cell_days)}</td><td>${escapeHtml(record.observation_status.replaceAll("_", " "))}</td></tr>`).join("")}</tbody></table><h2>Activity Anomaly</h2><p>${escapeHtml(month.anomaly.reason || `${formatRate(month.anomaly.difference_per_1000)} per 1,000 versus the same-month baseline.`)}</p><h2>Investigation Priority</h2><table><thead><tr><th>Block</th><th>Native rate</th><th>Support</th><th>Status</th></tr></thead><tbody>${blockRows}</tbody></table><h2>Limits and sources</h2><ul>${artifact().limitations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}${sourceRows}</ul><p>Evidence Receipt: ${escapeHtml(receipt().receipt_id)}</p><script>window.onload=()=>window.print()</script></body></html>`);
    win.document.close();
  }

  render();
})();
