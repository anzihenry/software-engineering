from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.p1_acceptance import prepare, source


class AcceptanceBoundaryTests(unittest.TestCase):
    def test_existing_target_is_preserved_before_any_git_or_install_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "existing"
            target.mkdir()
            owned = target / "user.txt"
            owned.write_bytes(b"keep existing content\n")
            with self.assertRaises(FileExistsError):
                prepare(target, root / "missing-harness", "0" * 40, mature=True, repository="x/y")
            self.assertEqual(owned.read_bytes(), b"keep existing content\n")
            self.assertEqual(list(target.iterdir()), [owned])

    def test_symbolic_source_is_rejected_before_archive_destination_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "knowledge"
            repository.mkdir()
            for arguments in (
                ["init", "-b", "main"],
                ["config", "user.name", "Fixture"],
                ["config", "user.email", "fixture@example.invalid"],
                ["commit", "--allow-empty", "-m", "fixture"],
            ):
                subprocess.run(
                    ["git", "-C", str(repository), *arguments], check=True, capture_output=True
                )
            destination = root / "archive"
            with self.assertRaisesRegex(ValueError, "complete fixed source"):
                source(repository, "main", destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
