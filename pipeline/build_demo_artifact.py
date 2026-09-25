#!/usr/bin/env python3
"""Build the portable Fire Season contract fixture and static data bundle."""

from __future__ import annotations

import csv
import calendar
import hashlib
import html
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.contract import validate_analysis_artifact, validate_evidence_receipt, validate_release_manifest
from fireseason.demo import build_demo_release


OUT = ROOT / "app" / "data"
RELEASES = OUT / "releases"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> bytes:
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data


def payload_record(path: Path, media_type: str) -> dict[str, object]:
    data = path.read_bytes()
    return {"path": path.name, "media_type": media_type, "size_bytes": len(data), "sha256": sha256_bytes(data)}


def region_geojson(region_key: str) -> dict[str, object]:
    if region_key == "science":
        # A display fixture bounding box; final boundaries require the data gate.
        ring = [[90.0, 21.0], [98.0, 21.0], [98.0, 28.0], [90.0, 28.0], [90.0, 21.0]]
    else:
        ring = [[91.4, 20.6], [92.7, 20.6], [92.7, 23.2], [91.4, 23.2], [91.4, 20.6]]
    return {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {"fixture": True, "region_key": region_key}, "geometry": {"type": "Polygon", "coordinates": [ring]}}],
    }


def calendar_rows(artifact: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for month in artifact["months"]:
        for record in month["native_records"]:
            rows.append({
                "artifact_id": artifact["artifact_id"],
                "region_id": artifact["region"]["region_id"],
                "month": month["month"],
                "product_id": record["product_id"],
                "observation_status": record["observation_status"],
                "detected_cell_days": record["detected_cell_days"],
                "valid_cell_days": record["valid_cell_days"],
                "eligible_land_cell_days": record["eligible_land_cell_days"],
                "support_fraction": record["support_fraction"],
                "rate_per_1000": record["rate_per_1000"],
                "comparison_status": month["comparison"]["status"],
            })
    return rows


def block_rows(artifact: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for month in artifact["months"]:
        record = month["native_records"][0]
        for row in range(1, 4):
            for column in range(1, 5):
                # A spatial display fixture: the final block values must come from
                # aligned rasters and a declared rule, never from this offset.
                offset = ((row * 7 + column * 11 + int(month["month"][5:7])) % 9) - 4
                native_rate = None if record["rate_per_1000"] is None else round(max(0, record["rate_per_1000"] + offset * 0.7), 4)
                support = round(max(0, min(1, record["support_fraction"] - (abs(offset) * 0.006))), 6)
                rows.append({
                    "artifact_id": artifact["artifact_id"],
                    "region_id": artifact["region"]["region_id"],
                    "block_id": f"{artifact['region']['region_id']}_b{row:02d}_{column:02d}",
                    "month": month["month"],
                    "product_id": record["product_id"],
                    "native_rate_per_1000": native_rate,
                    "support_fraction": support,
                    "comparison_status": month["comparison"]["status"],
                    "investigation_priority": month["investigation_priority"]["status"],
                })
    return rows


def monitoring_brief_html(artifact: dict[str, object], receipt: dict[str, object]) -> str:
    """Render the portable one-page brief from the same artifact fields as the app."""
    month = next(item for item in artifact["months"] if item["month"] == "2024-03")
    monthly_totals = [{"total": 0.0, "count": 0} for _ in range(12)]
    reference_id = artifact["reference_product_id"]
    for item in artifact["months"]:
        record = next(record for record in item["native_records"] if record["product_id"] == reference_id)
        if record["rate_per_1000"] is not None:
            index = int(item["month"][5:7]) - 1
            monthly_totals[index]["total"] += record["rate_per_1000"]
            monthly_totals[index]["count"] += 1
    typical = sorted(
        ((index, values["total"] / values["count"]) for index, values in enumerate(monthly_totals) if values["count"]),
        key=lambda item: item[1],
        reverse=True,
    )[:3]
    typical_label = ", ".join(calendar.month_name[index + 1] for index, _ in typical) or "Unavailable"
    native_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{:.0%}</td><td>{:,}</td><td>{:,}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(next(source["short_name"] for source in artifact["sources"] if source["product_id"] == record["product_id"])),
            "—" if record["rate_per_1000"] is None else f"{record['rate_per_1000']:.1f}",
            record["support_fraction"],
            record["eligible_land_cell_days"],
            record["valid_cell_days"],
            f"{record['detected_cell_days']:,}" if record["detected_cell_days"] is not None else "—",
            html.escape(record["observation_status"].replace("_", " ")),
        )
        for record in month["native_records"]
    )
    blocks = block_rows(artifact)
    block_rows_html = "".join(
        "<tr><td>{}</td><td>{}</td><td>{:.0%}</td><td>{}</td></tr>".format(
            html.escape(row["block_id"]),
            "—" if row["native_rate_per_1000"] is None else f"{row['native_rate_per_1000']:.1f}",
            row["support_fraction"],
            html.escape(row["investigation_priority"]),
        )
        for row in blocks
        if row["month"] == month["month"]
    )
    sources = "".join(f"<li>{html.escape(source['short_name'])} {html.escape(source['version'])} · {html.escape(source['source_url'])}</li>" for source in artifact["sources"])
    limitations = "".join(f"<li>{html.escape(item)}</li>" for item in artifact["limitations"])
    comparison = month["comparison"]
    anomaly = month["anomaly"]
    anomaly_text = anomaly["reason"] or f"{anomaly['difference_per_1000']:+.1f} per 1,000 versus the same-month baseline."
    if comparison["status"] == "available":
        comparison_note = f"<strong>Comparison status:</strong> Available on reference scale (Estimate: {comparison['estimate_per_1000']:.1f} per 1,000; 90% interval [{comparison['lower_90']:.1f}, {comparison['upper_90']:.1f}]).<br><strong>Calibration Release:</strong> {html.escape(comparison['calibration_id'])}"
    else:
        reason_text = html.escape(comparison["reason"] or "")
        comparison_note = f"<strong>Comparison status:</strong> {html.escape(comparison['status'].replace('_', ' '))}. {reason_text}<br><strong>Uncertainty:</strong> no interval is emitted until a calibration release passes evaluation gates."
    return f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><title>Fire Season Monitoring Brief · {month['month']}</title>
<style>body{{font:14px system-ui,sans-serif;color:#182a30;max-width:820px;margin:32px auto;line-height:1.5}}h1{{font:32px Georgia,serif}}table{{width:100%;border-collapse:collapse;margin:18px 0}}td,th{{border-bottom:1px solid #cbd5d2;padding:8px;text-align:left}}.note{{background:#eef4f0;padding:12px;border-left:4px solid #2c6674}}</style></head>
<body><p>FIRE SEASON · MONITORING BRIEF</p><h1>March 2024</h1>
<p>{html.escape(artifact['region']['name'])} · {html.escape(artifact['region']['role'].replace('_', ' '))}<br>Analysis period: {html.escape(artifact['period']['start_date'])} → {html.escape(artifact['period']['end_date'])}<br>Typical higher-activity months: {html.escape(typical_label)}</p>
<div class='note'>{comparison_note}</div>
<h2>Native Sensor Records</h2><table><thead><tr><th>Product</th><th>Rate per 1,000</th><th>Support</th><th>Eligible</th><th>Valid</th><th>Detected</th><th>State</th></tr></thead><tbody>{native_rows}</tbody></table>
<h2>Activity Anomaly</h2><p>{html.escape(anomaly_text)}</p>
<h2>Investigation Priority</h2><table><thead><tr><th>Block</th><th>Native rate</th><th>Support</th><th>Status</th></tr></thead><tbody>{block_rows_html}</tbody></table>
<h2>Limits and sources</h2><ul>{limitations}{sources}</ul><p>Evidence Receipt: {html.escape(receipt['receipt_id'])}</p></body></html>
"""


def write_csv(path: Path, rows: list[dict[str, object]]) -> bytes:
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path.read_bytes()


def build_region(region_key: str) -> dict[str, object]:
    artifact, receipt = build_demo_release(region_key)
    target_dir = RELEASES / ("science-pilot" if region_key == "science" else "local-impact-case")
    region_dir = Path(tempfile.mkdtemp(prefix=f".{target_dir.name}.", dir=RELEASES))

    geo_path = region_dir / "region.geojson"
    write_json(geo_path, region_geojson(region_key))
    geometry_sha = sha256_bytes(geo_path.read_bytes())
    artifact["region"]["geometry_sha256"] = geometry_sha
    receipt["region"]["geometry_sha256"] = geometry_sha

    calendar_path = region_dir / "calendar.csv"
    write_csv(calendar_path, calendar_rows(artifact))
    block_path = region_dir / "block-month.csv"
    write_csv(block_path, block_rows(artifact))
    evaluation_path = region_dir / "evaluation.json"
    write_json(
        evaluation_path,
        {
            "schema_version": "1.0.0",
            "status": "not_evaluated",
            "reason": "This contract fixture has no decoded paired historical masks or calibration candidate.",
            "calibration_release": None,
        },
    )

    brief_path = region_dir / "monitoring-brief.html"
    brief_path.write_text(monitoring_brief_html(artifact, receipt), encoding="utf-8")
    payloads = [
        payload_record(calendar_path, "text/csv"),
        payload_record(block_path, "text/csv"),
        payload_record(evaluation_path, "application/json"),
        payload_record(geo_path, "application/geo+json"),
        payload_record(brief_path, "text/html"),
    ]
    artifact["files"] = payloads
    validate_analysis_artifact(artifact)
    analysis_path = region_dir / "analysis.json"
    analysis_bytes = write_json(analysis_path, artifact)

    receipt["files"] = [
        {"path": "analysis.json", "media_type": "application/json", "size_bytes": len(analysis_bytes), "sha256": sha256_bytes(analysis_bytes)},
        *payloads,
    ]
    validate_evidence_receipt(receipt)
    receipt_path = region_dir / "evidence-receipt.json"
    receipt_bytes = write_json(receipt_path, receipt)

    manifest = {
        "schema_version": "1.0.0",
        "artifact_id": artifact["artifact_id"],
        "manifest_created_at": artifact["generated_at"],
        "files": [
            {"path": "analysis.json", "media_type": "application/json", "size_bytes": len(analysis_bytes), "sha256": sha256_bytes(analysis_bytes)},
            {"path": "evidence-receipt.json", "media_type": "application/json", "size_bytes": len(receipt_bytes), "sha256": sha256_bytes(receipt_bytes)},
            *payloads,
        ],
    }
    validate_release_manifest(manifest)
    write_json(region_dir / "manifest.json", manifest)
    backup_dir = target_dir.with_name(f".{target_dir.name}.previous")
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    if target_dir.exists():
        os.replace(target_dir, backup_dir)
    try:
        os.replace(region_dir, target_dir)
    except Exception:
        if backup_dir.exists() and not target_dir.exists():
            os.replace(backup_dir, target_dir)
        raise
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    return {"key": "science" if region_key == "science" else "local", "role": artifact["region"]["role"], "name": artifact["region"]["name"], "path": str(target_dir.relative_to(ROOT / "app"))}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RELEASES.mkdir(parents=True, exist_ok=True)
    for prefix in (".science-pilot.", ".local-impact-case."):
        for stale in RELEASES.glob(f"{prefix}*"):
            if stale.is_dir():
                shutil.rmtree(stale)
    entries = [build_region("science"), build_region("local")]
    index = {
        "schema_version": "1.0.0",
        "fixture_status": "contract_fixture_not_scientific_result",
        "regions": entries,
    }
    write_json(OUT / "index.json", index)
    data = {
        "index": index,
        "artifacts": {},
        "receipts": {},
        "blocks": {},
    }
    for entry in entries:
        key = entry["key"]
        region_dir = ROOT / "app" / entry["path"]
        data["artifacts"][key] = json.loads((region_dir / "analysis.json").read_text(encoding="utf-8"))
        data["receipts"][key] = json.loads((region_dir / "evidence-receipt.json").read_text(encoding="utf-8"))
        data["blocks"][key] = list(csv.DictReader((region_dir / "block-month.csv").open(encoding="utf-8")))
    js = "window.FIRE_SEASON_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (ROOT / "app" / "data.js").write_text(js, encoding="utf-8")
    print(json.dumps({"output": str(OUT), "regions": [entry["key"] for entry in entries]}, indent=2))


if __name__ == "__main__":
    main()
