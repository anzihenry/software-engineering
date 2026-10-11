from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.requirements_check import validate

ROOT = Path(__file__).resolve().parents[1]


class RequirementsCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((ROOT / "docs/harness-requirements.json").read_text())

    def test_current_sources(self) -> None:
        self.assertEqual(validate(ROOT, self.data), [])

    def test_omission_is_rejected(self) -> None:
        self.data["requirements"].pop()
        self.assertTrue(any("uncovered" in e for e in validate(ROOT, self.data)))

    def test_stale_source_and_unmapped_new_constraint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for source in self.data["sources"]:
                target = root / source["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / source["path"]).read_text())
            (root / "AGENTS.md").write_text(
                (root / "AGENTS.md").read_text() + "\n不得伪造新检查。\n"
            )
            errors = validate(root, self.data)
            self.assertTrue(any("source changed" in e for e in errors))
            self.assertTrue(any("uncovered" in e for e in errors))

    def test_mapping_or_adoption_cannot_be_faked(self) -> None:
        data = copy.deepcopy(self.data)
        data["controls"]["coding"]["method"] = ""
        data["requirements"][0]["adoption"] = "verified"
        errors = validate(ROOT, data)
        self.assertTrue(any("mapping incomplete" in e for e in errors))
        self.assertTrue(any("must not certify" in e for e in errors))

    def test_baseline_capability_and_retirement_cannot_be_forged(self) -> None:
        for field, value in (
            ("baseline", "0" * 40),
            (
                "retired",
                [{"id": "REQ-" + "0" * 16, "replacements": [], "owner": "x", "reason": "x"}],
            ),
        ):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data[field] = value
                self.assertTrue(validate(ROOT, data))
        for field, value in (
            ("capability", "automatically-enforced"),
            ("gaps", ["GAP-NONEXISTENT"]),
            ("controls", []),
        ):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                data["requirements"][0][field] = value
                self.assertTrue(validate(ROOT, data))
        data = copy.deepcopy(self.data)
        data["controls"]["coding"]["executor"] = "README.md"
        self.assertTrue(validate(ROOT, data))

    def test_whole_source_deletion_requires_retirement(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in {s["path"] for s in self.data["sources"]} | {
                c["executor"] for c in self.data["controls"].values()
            }:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / path).read_text())

            def git(*args: str) -> str:
                return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

            git("init", "-q")
            git("add", ".")
            git(
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "baseline",
            )
            data = copy.deepcopy(self.data)
            data["baseline"] = git("rev-parse", "HEAD")
            removed = "skills/01-demand-and-opportunity/problem-framing/SKILL.md"
            (root / removed).unlink()
            data["scope"].remove(removed)
            data["sources"] = [s for s in data["sources"] if s["path"] != removed]
            data["requirements"] = [r for r in data["requirements"] if r["source"] != removed]
            self.assertTrue(any("removed without retirement" in e for e in validate(root, data)))

    def test_retirement_with_and_without_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in {s["path"] for s in self.data["sources"]} | {
                c["executor"] for c in self.data["controls"].values()
            }:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / path).read_text())
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.invalid",
                    "commit",
                    "-qm",
                    "baseline",
                ],
                cwd=root,
                check=True,
            )
            data = copy.deepcopy(self.data)
            data["baseline"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            removed = "skills/01-demand-and-opportunity/problem-framing/SKILL.md"
            (root / removed).unlink()
            old_rows = [r for r in data["requirements"] if r["source"] == removed]
            data["scope"].remove(removed)
            data["sources"] = [s for s in data["sources"] if s["path"] != removed]
            data["requirements"] = [r for r in data["requirements"] if r["source"] != removed]
            for disposition in ["replaced", "retired"]:
                with self.subTest(disposition=disposition):
                    data["retired"] = [
                        {
                            "id": r["id"],
                            "owner": "process-owner",
                            "reason": "fixture removal",
                            "decision": "independent fixture",
                            "disposition": disposition,
                            "replacements": [data["requirements"][0]["id"]]
                            if disposition == "replaced"
                            else [],
                        }
                        for r in old_rows
                    ]
                    self.assertEqual(validate(root, data), [])
