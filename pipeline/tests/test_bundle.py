import hashlib
import json
import sys
import shutil
import tempfile
import unittest
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.contract import validate_analysis_artifact, validate_artifact_receipt_pair, validate_evidence_receipt, validate_release_manifest
from fireseason.sample import REGIONS, build_march_2023_sample, region_id
from build_research_bundle import _assert_revision_geometry_unchanged, _verify_existing_release, _write_release, release_target


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GeneratedBundleTests(unittest.TestCase):
    def test_generated_regions_validate_and_manifest_hashes_match(self):
        index = json.loads((ROOT / "app" / "data" / "index.json").read_text(encoding="utf-8"))
        for index_entry in index["regions"]:
            region_dir = ROOT / "app" / index_entry["path"]
            with self.subTest(region=region_dir.name):
                analysis_path = region_dir / "analysis.json"
                receipt_path = region_dir / "evidence-receipt.json"
                manifest_path = region_dir / "manifest.json"
                self.assertTrue(analysis_path.exists())
                self.assertTrue(receipt_path.exists())
                self.assertTrue(manifest_path.exists())

                analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                geometry_payloads = {
                    analysis["region"]["geometry_ref"]: (region_dir / analysis["region"]["geometry_ref"]).read_bytes()
                }
                validate_analysis_artifact(analysis, geometry_payloads=geometry_payloads)
                validate_evidence_receipt(receipt, geometry_payloads=geometry_payloads)
                validate_artifact_receipt_pair(analysis, receipt, geometry_payloads=geometry_payloads)
                validate_release_manifest(manifest)

                for manifest_entry in manifest["files"]:
                    path = region_dir / manifest_entry["path"]
                    self.assertTrue(path.exists(), manifest_entry["path"])
                    self.assertEqual(path.stat().st_size, manifest_entry["size_bytes"], manifest_entry["path"])
                    self.assertEqual(sha256(path), manifest_entry["sha256"], manifest_entry["path"])

                self.assertEqual(manifest["artifact_id"], analysis["artifact_id"])
                self.assertEqual(receipt["artifact_id"], analysis["artifact_id"])
                self.assertEqual(index_entry["artifact_id"], analysis["artifact_id"])
                self.assertEqual(index_entry["manifest_sha256"], sha256(manifest_path))
                suffix = analysis["artifact_id"].rsplit("_", 1)[-1]
                self.assertRegex(suffix, r"^[0-9a-f]{12}$")
                self.assertEqual(receipt["receipt_id"], f"rcpt_{suffix}")
                with (region_dir / "block-month.csv").open(encoding="utf-8") as block_file:
                    block_rows = list(csv.DictReader(block_file))
                self.assertGreater(len(block_rows), 0)
                self.assertEqual(analysis["release_status"], "native_only")
                self.assertIsNone(analysis["calibration"])
                self.assertEqual(analysis["months"][0]["month"], "2023-03")
                self.assertTrue(all(month["comparison"]["estimate_per_1000"] is None for month in analysis["months"]))

    def test_existing_release_rejects_manifest_refreshed_for_changed_geometry(self):
        index = json.loads((ROOT / "app" / "data" / "index.json").read_text(encoding="utf-8"))
        entry = index["regions"][0]
        source = ROOT / "app" / entry["path"]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "release"
            shutil.copytree(source, target)
            analysis = json.loads((target / "analysis.json").read_text(encoding="utf-8"))
            receipt = json.loads((target / "evidence-receipt.json").read_text(encoding="utf-8"))
            manifest_path = target / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            geometry_path = target / analysis["region"]["geometry_ref"]
            geometry_path.write_bytes(geometry_path.read_bytes() + b"\n")
            geometry_entry = next(item for item in manifest["files"] if item["path"] == analysis["region"]["geometry_ref"])
            geometry_entry["size_bytes"] = geometry_path.stat().st_size
            geometry_entry["sha256"] = sha256(geometry_path)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "manifest payload metadata differs from artifact and receipt records for region.geojson"):
                _verify_existing_release(
                    "science",
                    target,
                    analysis["artifact_id"],
                    receipt["analysis"]["source_manifest_sha256"],
                    analysis["region"]["geometry_sha256"],
                )

    def test_receipt_source_metadata_must_match_artifact(self):
        index = json.loads((ROOT / "app" / "data" / "index.json").read_text(encoding="utf-8"))
        region_dir = ROOT / "app" / index["regions"][0]["path"]
        artifact = json.loads((region_dir / "analysis.json").read_text(encoding="utf-8"))
        receipt = json.loads((region_dir / "evidence-receipt.json").read_text(encoding="utf-8"))
        receipt["sources"][0]["version"] = "Collection 99"

        with self.assertRaisesRegex(ValueError, "source .* version differs"):
            validate_artifact_receipt_pair(artifact, receipt)

    def test_receipt_metric_and_daily_coverage_match_artifact_period(self):
        index = json.loads((ROOT / "app" / "data" / "index.json").read_text(encoding="utf-8"))
        region_dir = ROOT / "app" / index["regions"][0]["path"]
        artifact = json.loads((region_dir / "analysis.json").read_text(encoding="utf-8"))
        receipt_path = region_dir / "evidence-receipt.json"

        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["analysis"]["metric_id"] = "other_metric"
        with self.assertRaisesRegex(ValueError, "metric"):
            validate_artifact_receipt_pair(artifact, receipt)

        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        coverage = receipt["analysis"]["daily_coverage"]
        coverage.update(expected_calendar_days=30, myd14a1_observed_days=30, vnp14a1_observed_days=30)
        with self.assertRaisesRegex(ValueError, "inclusive analysis period"):
            validate_artifact_receipt_pair(artifact, receipt)

    def test_manifest_artifact_id_must_match_analysis_artifact(self):
        index = json.loads((ROOT / "app" / "data" / "index.json").read_text(encoding="utf-8"))
        region_dir = ROOT / "app" / index["regions"][0]["path"]
        artifact = json.loads((region_dir / "analysis.json").read_text(encoding="utf-8"))
        manifest = json.loads((region_dir / "manifest.json").read_text(encoding="utf-8"))
        validate_release_manifest(manifest, expected_artifact_id=artifact["artifact_id"])
        manifest["artifact_id"] = "art_other_candidate_000000000000"

        with self.assertRaisesRegex(ValueError, "does not match the analysis artifact"):
            validate_release_manifest(manifest, expected_artifact_id=artifact["artifact_id"])

    def test_manifest_must_list_every_bundle_file(self):
        index = json.loads((ROOT / "app" / "data" / "index.json").read_text(encoding="utf-8"))
        region_dir = ROOT / "app" / index["regions"][0]["path"]
        artifact = json.loads((region_dir / "analysis.json").read_text(encoding="utf-8"))
        manifest = json.loads((region_dir / "manifest.json").read_text(encoding="utf-8"))
        expected_paths = {"analysis.json", "evidence-receipt.json", *(entry["path"] for entry in artifact["files"])}
        validate_release_manifest(
            manifest,
            expected_artifact_id=artifact["artifact_id"],
            expected_file_paths=expected_paths,
        )
        manifest["files"] = [entry for entry in manifest["files"] if entry["path"] != "monitoring-brief.html"]

        with self.assertRaisesRegex(ValueError, "complete release bundle"):
            validate_release_manifest(
                manifest,
                expected_artifact_id=artifact["artifact_id"],
                expected_file_paths=expected_paths,
            )

    def test_generated_records_match_stored_raster_decode(self):
        sample = build_march_2023_sample()
        index = json.loads((ROOT / "app" / "data" / "index.json").read_text(encoding="utf-8"))
        release_paths = {entry["key"]: ROOT / "app" / entry["path"] for entry in index["regions"]}
        for region_key, region_dir in release_paths.items():
            analysis = json.loads((region_dir / "analysis.json").read_text(encoding="utf-8"))
            expected = sample["regions"][region_key]["native_records"]
            self.assertEqual(analysis["months"][0]["native_records"], expected)
            with (region_dir / "block-month.csv").open(encoding="utf-8") as block_file:
                block_rows = list(csv.DictReader(block_file))
            self.assertEqual(len(block_rows), len(sample["regions"][region_key]["blocks"]))
            self.assertEqual(len(sample["sources"]["modis"]), 5)
            self.assertEqual(len(sample["sources"]["viirs"]), 31)
            self.assertTrue(all(len(source["sha256"]) == 64 for group in sample["sources"].values() for source in group))

    def test_identical_rebuild_keeps_published_release_files_immutable(self):
        sample = build_march_2023_sample()
        for region_key in ("science", "local"):
            entry = _write_release(region_key, sample)
            region_dir = ROOT / "app" / entry["path"]
            filenames = ("analysis.json", "evidence-receipt.json", "manifest.json")
            before = {name: (region_dir / name).read_bytes() for name in filenames}

            repeated_entry = _write_release(region_key, sample)

            self.assertEqual(entry["path"], repeated_entry["path"])
            self.assertEqual(before, {name: (region_dir / name).read_bytes() for name in filenames})

    def test_region_revision_creates_a_new_release_identity_and_path(self):
        region = REGIONS["science"]
        revision = region["revision"]
        source_id = "src_0123456789ab"
        fingerprint = "0123456789abcdef"
        first_id = region_id(region)
        first_target = release_target("science", source_id, fingerprint)
        try:
            region["revision"] = revision + 1
            second_id = region_id(region)
            second_target = release_target("science", source_id, fingerprint)
        finally:
            region["revision"] = revision

        self.assertNotEqual(first_id, second_id)
        self.assertNotEqual(first_target, second_target)

    def test_boundary_change_within_same_revision_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            revision_dir = Path(temporary_directory) / "r2"
            existing_release = revision_dir / "source-fingerprint"
            existing_release.mkdir(parents=True)
            (existing_release / "analysis.json").write_text(
                json.dumps({"region": {"geometry_sha256": "a" * 64}}),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "increment the region revision"):
                _assert_revision_geometry_unchanged(revision_dir, "b" * 64)

    def test_static_bundle_has_no_external_runtime_dependency_marker(self):
        app_js = (ROOT / "app" / "app.js").read_text(encoding="utf-8")
        styles = (ROOT / "app" / "styles.css").read_text(encoding="utf-8")
        self.assertNotIn("https://", app_js)
        self.assertNotIn("@import", styles)


if __name__ == "__main__":
    unittest.main()
