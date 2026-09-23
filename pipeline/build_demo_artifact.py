#!/usr/bin/env python3
"""Build the portable Fire Season contract fixture and static data bundle."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.contract import validate_analysis_artifact, validate_evidence_receipt
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
        rows.append({
            "artifact_id": artifact["artifact_id"],
            "region_id": artifact["region"]["region_id"],
            "block_id": f"{artifact['region']['region_id']}_b01_01",
            "month": month["month"],
            "product_id": record["product_id"],
            "native_rate_per_1000": record["rate_per_1000"],
            "support_fraction": record["support_fraction"],
            "comparison_status": month["comparison"]["status"],
            "investigation_priority": month["investigation_priority"]["status"],
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> bytes:
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path.read_bytes()


def build_region(region_key: str) -> dict[str, object]:
    artifact, receipt = build_demo_release(region_key)
    region_dir = RELEASES / ("science-pilot" if region_key == "science" else "local-impact-case")
    if region_dir.exists():
        shutil.rmtree(region_dir)
    region_dir.mkdir(parents=True)

    geo_path = region_dir / "region.geojson"
    write_json(geo_path, region_geojson(region_key))
    geometry_sha = sha256_bytes(geo_path.read_bytes())
    artifact["region"]["geometry_sha256"] = geometry_sha
    receipt["region"]["geometry_sha256"] = geometry_sha

    calendar_path = region_dir / "calendar.csv"
    write_csv(calendar_path, calendar_rows(artifact))
    block_path = region_dir / "block-month.csv"
    write_csv(block_path, block_rows(artifact))

    brief_path = region_dir / "monitoring-brief.html"
    brief_path.write_text(
        "<!doctype html><meta charset='utf-8'><title>Fire Season contract fixture</title>"
        "<p>This Monitoring Brief is a contract fixture. No Calibration Release is present.</p>",
        encoding="utf-8",
    )
    payloads = [
        payload_record(calendar_path, "text/csv"),
        payload_record(block_path, "text/csv"),
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
    write_json(region_dir / "manifest.json", manifest)
    return {"key": "science" if region_key == "science" else "local", "role": artifact["region"]["role"], "name": artifact["region"]["name"], "path": str(region_dir.relative_to(ROOT / "app"))}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if RELEASES.exists():
        RELEASES.mkdir(parents=True, exist_ok=True)
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
