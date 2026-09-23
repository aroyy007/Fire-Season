import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.contract import validate_analysis_artifact, validate_evidence_receipt, validate_release_manifest


RELEASES = ROOT / "app" / "data" / "releases"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GeneratedBundleTests(unittest.TestCase):
    def test_generated_regions_validate_and_manifest_hashes_match(self):
        for region_dir in (RELEASES / "science-pilot", RELEASES / "local-impact-case"):
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
                validate_analysis_artifact(analysis)
                validate_evidence_receipt(receipt)
                validate_release_manifest(manifest)

                for entry in manifest["files"]:
                    path = region_dir / entry["path"]
                    self.assertTrue(path.exists(), entry["path"])
                    self.assertEqual(path.stat().st_size, entry["size_bytes"], entry["path"])
                    self.assertEqual(sha256(path), entry["sha256"], entry["path"])

                self.assertEqual(manifest["artifact_id"], analysis["artifact_id"])
                self.assertEqual(receipt["artifact_id"], analysis["artifact_id"])

    def test_static_bundle_has_no_external_runtime_dependency_marker(self):
        app_js = (ROOT / "app" / "app.js").read_text(encoding="utf-8")
        styles = (ROOT / "app" / "styles.css").read_text(encoding="utf-8")
        self.assertNotIn("https://", app_js)
        self.assertNotIn("@import", styles)


if __name__ == "__main__":
    unittest.main()
