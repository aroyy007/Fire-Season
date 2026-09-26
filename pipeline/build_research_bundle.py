#!/usr/bin/env python3
"""Build the offline app bundle from the stored, AOI-clipped March 2023 rasters."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.contract import validate_analysis_artifact, validate_artifact_receipt_pair, validate_release_manifest
from fireseason.sample import REGIONS, build_march_2023_sample
from fireseason.science_release import build_research_release, candidate_region_geojson

OUT = ROOT / "app" / "data"
RELEASES = OUT / "releases"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: object) -> bytes:
    data = json_bytes(value)
    path.write_bytes(data)
    return data


def release_fingerprint(region_key: str, sample: dict[str, Any], geometry_sha256: str) -> str:
    """Bind an immutable release ID to its inputs, code, region and runtime."""
    code_files = [
        ROOT / "pipeline" / "build_research_bundle.py",
        *sorted((ROOT / "pipeline" / "fireseason").glob("*.py")),
        *sorted((ROOT / "backend" / "schemas").glob("*.json")),
        ROOT / "pipeline" / "requirements-science.lock",
    ]
    parts = [
        f"region={region_key}:r{REGIONS[region_key]['revision']}",
        f"geometry={geometry_sha256}",
        f"source_manifest={sample['source_manifest_sha256']}",
        f"runtime={platform.python_version()}:{platform.system()}",
    ]
    parts.extend(f"{path.relative_to(ROOT)}:{sha256_bytes(path.read_bytes())}" for path in code_files)
    return sha256_bytes("\n".join(parts).encode("utf-8"))[:16]


def revision_directory(region_key: str) -> Path:
    region_dir_name = "science-pilot" if region_key == "science" else "local-impact-case"
    revision = REGIONS[region_key]["revision"]
    return RELEASES / region_dir_name / f"r{revision}"


def release_target(region_key: str, source_manifest_id: str, fingerprint: str) -> Path:
    return revision_directory(region_key) / f"{source_manifest_id}-{fingerprint}"


def payload_record(path: Path, media_type: str) -> dict[str, object]:
    data = path.read_bytes()
    return {"path": path.name, "media_type": media_type, "size_bytes": len(data), "sha256": sha256_bytes(data)}


def _assert_manifest_matches_records(
    manifest: dict[str, Any],
    artifact: dict[str, Any],
    receipt: dict[str, Any],
    analysis_bytes: bytes,
    receipt_bytes: bytes,
) -> None:
    actual_artifacts = {entry["path"]: entry for entry in artifact["files"]}
    receipt_records = {entry["path"]: entry for entry in receipt["files"]}
    manifest_records = {entry["path"]: entry for entry in manifest["files"]}
    expected = {
        **actual_artifacts,
        "analysis.json": {
            "path": "analysis.json",
            "media_type": "application/json",
            "size_bytes": len(analysis_bytes),
            "sha256": sha256_bytes(analysis_bytes),
        },
        "evidence-receipt.json": {
            "path": "evidence-receipt.json",
            "media_type": "application/json",
            "size_bytes": len(receipt_bytes),
            "sha256": sha256_bytes(receipt_bytes),
        },
    }
    if set(receipt_records) != {"analysis.json", *actual_artifacts}:
        raise ValueError("receipt file inventory differs from the artifact payload inventory")
    for path, artifact_record in actual_artifacts.items():
        receipt_record = receipt_records[path]
        if any(receipt_record.get(field) != artifact_record.get(field) for field in ("media_type", "size_bytes", "sha256")):
            raise ValueError(f"receipt payload metadata differs from artifact record for {path}")
    if set(manifest_records) != set(expected):
        raise ValueError("manifest file inventory differs from artifact and receipt records")
    for path, expected_record in expected.items():
        manifest_record = manifest_records[path]
        if any(manifest_record.get(field) != expected_record.get(field) for field in ("media_type", "size_bytes", "sha256")):
            raise ValueError(f"manifest payload metadata differs from artifact and receipt records for {path}")


def write_csv(path: Path, rows: list[dict[str, object]]) -> bytes:
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path.read_bytes()


def calendar_rows(artifact: dict[str, Any]) -> list[dict[str, object]]:
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


def monitoring_brief_html(artifact: dict[str, Any], receipt: dict[str, Any], blocks: list[dict[str, Any]]) -> str:
    month = artifact["months"][0]
    native_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{:.1%}</td><td>{:,}</td><td>{:,}</td><td>{:,}</td></tr>".format(
            html.escape(next(source["short_name"] for source in artifact["sources"] if source["product_id"] == record["product_id"])),
            "—" if record["rate_per_1000"] is None else f"{record['rate_per_1000']:.2f}",
            record["support_fraction"],
            record["eligible_land_cell_days"],
            record["valid_cell_days"],
            record["detected_cell_days"],
        )
        for record in month["native_records"]
    )
    block_rows_html = "".join(
        "<tr><td>{}</td><td>{:.5f}, {:.5f}</td><td>{}</td><td>{}</td><td>{:,}</td><td>{:,}</td></tr>".format(
            html.escape(row["block_id"]), row["longitude"], row["latitude"],
            "—" if row["native_rate_per_1000"] is None else f"{row['native_rate_per_1000']:.2f}",
            f"{row['support_fraction']:.0%}", row["valid_cell_days"], row["detected_cell_days"],
        )
        for row in blocks
    )
    sources = "".join(
        "<li><strong>{} {}</strong> · {} granules used · <a href='{}'>{}</a></li>".format(
            html.escape(source["short_name"]), html.escape(source["version"]),
            len(receipt_source["provider_objects"]), html.escape(source["product_guide_url"]), "product guide",
        )
        for source, receipt_source in zip(artifact["sources"], receipt["sources"])
    )
    limitations = "".join(f"<li>{html.escape(item)}</li>" for item in artifact["limitations"])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Fire Season Raster Sample · {month['month']}</title>
<style>body{{font:14px/1.5 system-ui,sans-serif;color:#182a30;max-width:1000px;margin:32px auto;padding:0 18px}}h1{{font:700 32px/1.15 system-ui,sans-serif;letter-spacing:-.03em}}table{{width:100%;border-collapse:collapse;margin:18px 0;font-variant-numeric:tabular-nums}}td,th{{border-bottom:1px solid #cbd5d2;padding:8px;text-align:left}}.note{{background:#f2f5f3;padding:12px;border-left:4px solid #2c6674}}small{{color:#52656b}}</style></head>
<body><p>FIRE SEASON · RASTER RESEARCH SAMPLE</p><h1>{html.escape(month['month'])} · {html.escape(artifact['region']['name'])}</h1>
<p>Native-grid research sample · bounds {artifact['region']['revision']} candidate revision · metric: {html.escape(artifact['metric']['unit'])}</p>
<div class="note"><strong>Comparable Activity:</strong> unavailable. The two native records are not treated as directly comparable; no transfer model, anomaly, confidence interval, or priority score has passed the declared gates.</div>
<h2>Native sensor records</h2><table><thead><tr><th>Product</th><th>Rate / 1,000</th><th>Support</th><th>Eligible cell-days</th><th>Valid cell-days</th><th>Detected cell-days</th></tr></thead><tbody>{native_rows}</tbody></table>
<h2>Reference-product 10×10 native-pixel blocks</h2><small>Each block is 10×10 cells on the h26v06 grid; cells use projected pixel-center membership.</small>
<table><thead><tr><th>Block ID</th><th>Lon, lat</th><th>Rate / 1,000</th><th>Support</th><th>Valid cell-days</th><th>Detected cell-days</th></tr></thead><tbody>{block_rows_html}</tbody></table>
<h2>Sources and limitations</h2><ul>{sources}{limitations}</ul><p>Evidence Receipt: {html.escape(receipt['receipt_id'])}</p></body></html>"""


def _release_entry(region_key: str, path: Path) -> dict[str, Any]:
    region = REGIONS[region_key]
    analysis = json.loads((path / "analysis.json").read_text(encoding="utf-8"))
    manifest_sha256 = sha256_bytes((path / "manifest.json").read_bytes())
    return {
        "key": region_key,
        "role": region["role"],
        "name": region["name"],
        "artifact_id": analysis["artifact_id"],
        "manifest_sha256": manifest_sha256,
        "path": str(path.relative_to(ROOT / "app")),
        "boundary_status": "candidate_not_frozen",
        "region_revision": region["revision"],
        "bounds_wsen": list(region["bounds"]),
    }


def _assert_revision_geometry_unchanged(parent: Path, geometry_sha: str) -> None:
    if not parent.exists():
        return
    for artifact_path in parent.glob("*/analysis.json"):
        existing = json.loads(artifact_path.read_text(encoding="utf-8"))
        if existing["region"]["geometry_sha256"] != geometry_sha:
            raise ValueError(
                f"Region geometry changed within revision r{parent.name[1:]}; increment the region revision before rebuilding."
            )


def _verify_existing_release(
    region_key: str,
    target: Path,
    artifact_id: str,
    source_manifest_sha256: str,
    geometry_sha: str,
) -> dict[str, Any]:
    analysis_path = target / "analysis.json"
    receipt_path = target / "evidence-receipt.json"
    manifest_path = target / "manifest.json"
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    analysis_bytes = analysis_path.read_bytes()
    receipt_bytes = receipt_path.read_bytes()
    validate_release_manifest(
        manifest,
        expected_artifact_id=analysis["artifact_id"],
        expected_file_paths={"analysis.json", "evidence-receipt.json", *(entry["path"] for entry in analysis["files"])},
    )
    _assert_manifest_matches_records(manifest, analysis, receipt, analysis_bytes, receipt_bytes)
    if analysis["artifact_id"] != artifact_id:
        raise ValueError(f"Immutable release identity collision at {target}")
    if analysis["region"]["geometry_sha256"] != geometry_sha:
        raise ValueError(f"Immutable release geometry changed at {target}")
    if receipt["analysis"]["source_manifest_sha256"] != source_manifest_sha256:
        raise ValueError(f"Immutable release source manifest changed at {target}")
    geometry_payloads = {}
    for entry in manifest["files"]:
        path = target / entry["path"]
        if not path.is_file():
            raise ValueError(f"Immutable release payload is missing: {path}")
        payload = path.read_bytes()
        if len(payload) != entry["size_bytes"] or sha256_bytes(payload) != entry["sha256"]:
            raise ValueError(f"Immutable release payload checksum mismatch: {path}")
        if entry["media_type"] == "application/geo+json":
            geometry_payloads[entry["path"]] = payload
    calibration_evaluation = None
    calibration = analysis.get("calibration")
    if isinstance(calibration, dict):
        evaluation_ref = calibration.get("evaluation_ref")
        if not isinstance(evaluation_ref, str) or not evaluation_ref or Path(evaluation_ref).is_absolute() or ".." in Path(evaluation_ref).parts:
            raise ValueError("Immutable release evaluation reference is unsafe")
        evaluation_path = target / evaluation_ref
        if not evaluation_path.is_file():
            raise ValueError(f"Immutable release evaluation payload is missing: {evaluation_path}")
        calibration_evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    validate_artifact_receipt_pair(
        analysis,
        receipt,
        calibration_evaluation=calibration_evaluation,
        geometry_payloads=geometry_payloads,
    )
    return _release_entry(region_key, target)


def _write_release(region_key: str, sample: dict[str, Any]) -> dict[str, Any]:
    geojson = candidate_region_geojson(region_key)
    geometry_sha = sha256_bytes(json_bytes(geojson))
    region = REGIONS[region_key]
    revision_dir = revision_directory(region_key)
    _assert_revision_geometry_unchanged(revision_dir, geometry_sha)
    fingerprint = release_fingerprint(region_key, sample, geometry_sha)
    artifact, receipt = build_research_release(region_key, sample, fingerprint)
    region_dir_target = release_target(region_key, sample["source_manifest_id"], fingerprint)
    if region_dir_target.exists():
        return _verify_existing_release(
            region_key,
            region_dir_target,
            artifact["artifact_id"],
            sample["source_manifest_sha256"],
            geometry_sha,
        )

    region_dir_target.parent.mkdir(parents=True, exist_ok=True)
    region_dir = Path(tempfile.mkdtemp(prefix=".release-", dir=region_dir_target.parent))
    geometry_path = region_dir / "region.geojson"
    write_json(geometry_path, geojson)
    artifact["region"]["geometry_sha256"] = geometry_sha
    receipt["region"]["geometry_sha256"] = geometry_sha

    blocks = sample["regions"][region_key]["blocks"]
    for block in blocks:
        block["artifact_id"] = artifact["artifact_id"]
    calendar_path = region_dir / "calendar.csv"
    write_csv(calendar_path, calendar_rows(artifact))
    blocks_path = region_dir / "block-month.csv"
    write_csv(blocks_path, blocks)
    evaluation_path = region_dir / "evaluation.json"
    write_json(evaluation_path, {
        "schema_version": "1.0.0",
        "status": "not_evaluated",
        "candidate_model": None,
        "release_eligible": False,
        "reason": "The single-month sample does not provide independent temporal or geographic validation or interval coverage.",
    })
    brief_path = region_dir / "monitoring-brief.html"
    brief_path.write_text(monitoring_brief_html(artifact, receipt, blocks), encoding="utf-8")

    payloads = [
        payload_record(calendar_path, "text/csv"),
        payload_record(blocks_path, "text/csv"),
        payload_record(evaluation_path, "application/json"),
        payload_record(geometry_path, "application/geo+json"),
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
    validate_artifact_receipt_pair(artifact, receipt, geometry_payloads={"region.geojson": geometry_path.read_bytes()})
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
    validate_release_manifest(
        manifest,
        expected_artifact_id=artifact["artifact_id"],
        expected_file_paths={"analysis.json", "evidence-receipt.json", *(entry["path"] for entry in artifact["files"])},
    )
    write_json(region_dir / "manifest.json", manifest)

    try:
        os.replace(region_dir, region_dir_target)
    except Exception:
        shutil.rmtree(region_dir, ignore_errors=True)
        raise
    return _release_entry(region_key, region_dir_target)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RELEASES.mkdir(parents=True, exist_ok=True)
    sample = build_march_2023_sample()
    entries = [_write_release(region_key, sample) for region_key in ("science", "local")]
    index = {
        "schema_version": "1.0.0",
        "sample_status": "real_raster_sample_native_only",
        "sample_month": sample["month"],
        "expected_daily_planes_per_product": sample["expected_days"],
        "regions": entries,
    }
    write_json(OUT / "index.json", index)
    data: dict[str, Any] = {"index": index, "artifacts": {}, "receipts": {}, "blocks": {}}
    for entry in entries:
        key = entry["key"]
        region_dir = ROOT / "app" / entry["path"]
        data["artifacts"][key] = json.loads((region_dir / "analysis.json").read_text(encoding="utf-8"))
        data["receipts"][key] = json.loads((region_dir / "evidence-receipt.json").read_text(encoding="utf-8"))
        with (region_dir / "block-month.csv").open(encoding="utf-8") as handle:
            data["blocks"][key] = list(csv.DictReader(handle))
    (ROOT / "app" / "data.js").write_text(
        "window.FIRE_SEASON_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    for region_dir_name in ("science-pilot", "local-impact-case"):
        legacy_dir = RELEASES / region_dir_name
        for legacy_file in legacy_dir.glob("*"):
            if legacy_file.is_file():
                legacy_file.unlink()
    print(json.dumps({"sample_month": sample["month"], "regions": entries}, indent=2))


if __name__ == "__main__":
    main()
