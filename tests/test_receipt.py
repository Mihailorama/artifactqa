import tempfile
import unittest
from pathlib import Path

import artifactqa


class ArtifactQAContractTest(unittest.TestCase):
    def test_inspection_receipt_binds_verdict_to_exact_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "clip.mp4"
            artifact.write_bytes(b"first-version")

            receipt = artifactqa.inspect(
                artifact,
                inspector=lambda _: artifactqa.Inspection(verdict="pass", summary="clean"),
                inspector_name="offline-test",
                policy_version="v1",
            )

            self.assertEqual(receipt.verdict, "pass")
            self.assertTrue(receipt.artifact_sha256)

            artifact.write_bytes(b"changed-version")
            self.assertFalse(receipt.matches(artifact))

    def test_inspector_failure_is_unknown_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "still.png"
            artifact.write_bytes(b"image")

            def unavailable(_: Path) -> artifactqa.Inspection:
                raise RuntimeError("inspector unavailable")

            receipt = artifactqa.inspect(
                artifact,
                inspector=unavailable,
                inspector_name="offline-test",
                policy_version="v1",
            )

            self.assertEqual(receipt.verdict, "unknown")
            self.assertIn("inspector unavailable", receipt.reason or "")
