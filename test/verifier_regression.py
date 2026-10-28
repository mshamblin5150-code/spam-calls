"""Opt-in tests of the actual PowerShell verifier against disposable fixtures."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_BYTES = b"Synthetic source fixture.\n"


class FoundationVerifier(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="custos-verifier-fixture-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        (self.project / "scripts").mkdir()
        shutil.copyfile(VERIFIER, self.project / "scripts/verify-foundation.ps1")
        self.environment = dict(os.environ, POWERSHELL_TELEMETRY_OPTOUT="1", POWERSHELL_UPDATECHECK="Off")
        for variable, directory in (
            ("XDG_CONFIG_HOME", "config"), ("XDG_CACHE_HOME", "cache"),
            ("XDG_DATA_HOME", "data"), ("TMPDIR", "tmp"),
        ):
            target = self.project / directory
            target.mkdir()
            self.environment[variable] = str(target)
        self.collections = {}
        for name in ("matt-pocock", "pstack"):
            base = self.project / ".agents/skills" / name
            self.collections[name] = base
            self.write_collection(base, ["reference.md", ".hidden/entry.tsv"])

    def write_collection(self, base, paths):
        entries = []
        for relative in paths:
            target = base / "references/upstream" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(FIXTURE_BYTES)
            blob = b"blob " + str(len(FIXTURE_BYTES)).encode("ascii") + b"\0" + FIXTURE_BYTES
            entries.append({"path": relative, "bytes": len(FIXTURE_BYTES),
                            "sha256": hashlib.sha256(FIXTURE_BYTES).hexdigest(),
                            "gitBlob": hashlib.sha1(blob).hexdigest()})
        (base / "source-manifest.json").write_text(json.dumps({"files": entries}))
        (base / "catalog.json").write_text(json.dumps([
            {"path": f"references/upstream/{paths[0]}"},
        ]))

    def run_verifier(self):
        return subprocess.run(
            [str(PWSH), "-NoLogo", "-NoProfile", "-NonInteractive",
             "-File", str(self.project / "scripts/verify-foundation.ps1")],
            cwd=self.project, env=self.environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
        )

    def assert_rejected(self, result, diagnostic):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(diagnostic, result.stdout + result.stderr)
        self.assertNotIn("PASS:", result.stdout)

    def test_manifested_hidden_directories_are_included(self):
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("matt-pocock: 2 source files verified; 1 catalog entries", result.stdout)
        self.assertIn("pstack: 2 source files verified; 1 catalog entries", result.stdout)
        self.assertIn("PASS: 4 preserved source files match pinned SHA-256 and Git blob hashes.", result.stdout)

    def test_manifested_hidden_files_are_included(self):
        for base in self.collections.values():
            self.write_collection(base, ["reference.md", ".hidden/entry.tsv", ".hidden.md"])
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("matt-pocock: 3 source files verified; 1 catalog entries", result.stdout)
        self.assertIn("pstack: 3 source files verified; 1 catalog entries", result.stdout)
        self.assertIn("PASS: 6 preserved source files match pinned SHA-256 and Git blob hashes.", result.stdout)

    def test_true_extra_files_are_rejected_including_hidden_paths(self):
        source = self.collections["matt-pocock"] / "references/upstream"
        for relative in ("extra.md", ".extra.md", ".extra/extra.md"):
            with self.subTest(relative=relative):
                target = source / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(FIXTURE_BYTES)
                try:
                    self.assert_rejected(self.run_verifier(), "Unmanifested source file in matt-pocock")
                finally:
                    target.unlink()

    def test_missing_manifested_file_is_rejected(self):
        (self.collections["matt-pocock"] / "references/upstream/.hidden/entry.tsv").unlink()
        self.assert_rejected(self.run_verifier(), "Cannot find path")

    def test_changed_source_bytes_are_rejected(self):
        (self.collections["matt-pocock"] / "references/upstream/.hidden/entry.tsv").write_bytes(b"Altered source fixture.\n")
        self.assert_rejected(self.run_verifier(), "Vendored source mismatch")

    def test_manifest_hash_blob_and_size_drift_are_rejected(self):
        path = self.collections["matt-pocock"] / "source-manifest.json"
        original = path.read_text()
        for field, wrong in (("sha256", "0" * 64), ("gitBlob", "0" * 40), ("bytes", 0)):
            with self.subTest(field=field):
                manifest = json.loads(original)
                manifest["files"][0][field] = wrong
                path.write_text(json.dumps(manifest))
                self.assert_rejected(self.run_verifier(), "Vendored source mismatch")

    def test_manifested_unsupported_file_type_is_rejected(self):
        # This fixture's hashes are correct; only its extension is unsupported.
        base = self.collections["matt-pocock"]
        shutil.rmtree(base / "references/upstream")
        self.write_collection(base, ["unsupported.ps1"])
        self.assert_rejected(self.run_verifier(), "Unexpected source file type")

    def test_missing_catalog_target_is_rejected(self):
        (self.collections["matt-pocock"] / "catalog.json").write_text(
            json.dumps([{"path": "references/upstream/missing.md"}]))
        self.assert_rejected(self.run_verifier(), "Missing catalog source")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pwsh", type=Path, required=True, help="Explicit existing authorized PowerShell executable")
    parser.add_argument("--verifier", type=Path, default=ROOT / "scripts/verify-foundation.ps1",
                        help="Verifier copied into each isolated fixture (default: current checkout)")
    args, unittest_args = parser.parse_known_args()
    PWSH = args.pwsh.resolve(strict=True)
    VERIFIER = args.verifier.resolve(strict=True)
    unittest.main(argv=[parser.prog, *unittest_args], verbosity=2)
