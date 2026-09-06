from __future__ import annotations

import json
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.github_lifecycle.__main__ import main
from scripts.github_lifecycle.adoption import apply_install, plan_install
from scripts.github_lifecycle.common import LifecycleError
from scripts.github_lifecycle.installation import (
    INSTALLATION_RECORD_PATH,
    load_installation_record,
    parse_installation_record,
)
from scripts.github_lifecycle.upgrade import (
    _atomic_write,
    apply_upgrade,
    materialize_package,
    plan_upgrade,
)

MANIFEST = Path("automation/github-lifecycle-manifest.json")
REPOSITORY = "example/upgrade-service"


def create_package(root: Path, files: dict[str, str]) -> None:
    manifest = root / MANIFEST
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps({"schema_version": 1, "files": sorted(files)}) + "\n",
        encoding="utf-8",
    )
    for relative, content in files.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def install_old_version(source: Path, target: Path) -> None:
    plan, files = plan_install(
        source,
        MANIFEST,
        target,
        repository=REPOSITORY,
        default_branch="main",
        profile="full",
        adapter="external",
        source_ref="v1.1.0",
    )
    apply_install(plan, files, confirmation=f"install:{REPOSITORY}")


class InstallationRecordTests(unittest.TestCase):
    def test_install_records_an_immutable_source_and_file_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            target.mkdir()
            create_package(source, {"asset.txt": "old\n"})

            install_old_version(source, target)

            record = load_installation_record(target / INSTALLATION_RECORD_PATH)
            self.assertEqual(record.source_ref, "v1.1.0")
            self.assertEqual(record.profile, "full")
            self.assertEqual(set(record.files), {"asset.txt"})

            second, _ = plan_install(
                source,
                MANIFEST,
                target,
                repository=REPOSITORY,
                default_branch="main",
                profile="full",
                adapter="external",
            )
            self.assertEqual(second.source_ref, "v1.1.0")
            self.assertTrue(all(entry.action == "unchanged" for entry in second.entries))

    def test_record_rejects_unsafe_paths_and_mutable_refs(self) -> None:
        record = {
            "schema_version": 1,
            "repository": REPOSITORY,
            "default_branch": "main",
            "profile": "full",
            "adapter": "external",
            "source_ref": "main",
            "manifest_schema_version": 1,
            "files": {"../secret": "a" * 64},
        }
        with self.assertRaisesRegex(LifecycleError, "unsafe file path"):
            parse_installation_record({**record, "source_ref": "v1.1.0"})
        with self.assertRaisesRegex(LifecycleError, "source_ref"):
            parse_installation_record({**record, "files": {"asset.txt": "a" * 64}})


class UpgradeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.old = self.root / "old"
        self.new = self.root / "new"
        self.target = self.root / "target"
        self.old.mkdir()
        self.new.mkdir()
        self.target.mkdir()
        create_package(
            self.old,
            {
                "changed.txt": "old\n",
                "removed.txt": "preserve me\n",
                "same.txt": "same\n",
            },
        )
        create_package(
            self.new,
            {
                "changed.txt": "new\n",
                "created.txt": "created\n",
                "same.txt": "same\n",
            },
        )
        install_old_version(self.old, self.target)

    def tearDown(self) -> None:
        self.directory.cleanup()

    def plan(self):
        return plan_upgrade(
            self.old,
            self.new,
            self.target,
            repository=REPOSITORY,
            default_branch="main",
            from_ref="v1.1.0",
            to_ref="v1.2.0",
            profile="full",
            from_profile="full",
            manifest=MANIFEST,
        )

    def test_safe_upgrade_updates_creates_and_preserves_removed_files(self) -> None:
        plan, files = self.plan()
        actions = {entry.path: entry.action for entry in plan.entries}
        self.assertEqual(actions["changed.txt"], "safe-update")
        self.assertEqual(actions["created.txt"], "create")
        self.assertEqual(actions["same.txt"], "unchanged")
        self.assertEqual(actions["removed.txt"], "removed-upstream")
        self.assertEqual(plan.blockers, ())

        with self.assertRaisesRegex(LifecycleError, "confirmation"):
            apply_upgrade(plan, files, confirmation="upgrade:wrong")
        apply_upgrade(plan, files, confirmation=plan.confirmation)

        self.assertEqual((self.target / "changed.txt").read_text(), "new\n")
        self.assertEqual((self.target / "created.txt").read_text(), "created\n")
        self.assertEqual((self.target / "removed.txt").read_text(), "preserve me\n")
        record = load_installation_record(self.target / INSTALLATION_RECORD_PATH)
        self.assertEqual(record.source_ref, "v1.2.0")
        self.assertNotIn("removed.txt", record.files)

        repeated, _ = self.plan()
        self.assertEqual(repeated.blockers, ())
        self.assertTrue(
            all(entry.action in {"unchanged", "removed-upstream"} for entry in repeated.entries)
        )

    def test_local_modification_blocks_without_overwriting(self) -> None:
        changed = self.target / "changed.txt"
        changed.write_text("local\n", encoding="utf-8")

        plan, files = self.plan()

        self.assertIn("changed.txt", plan.blockers)
        with self.assertRaisesRegex(LifecycleError, "unresolved files"):
            apply_upgrade(plan, files, confirmation=plan.confirmation)
        self.assertEqual(changed.read_text(), "local\n")

    def test_apply_rechecks_files_after_dry_run(self) -> None:
        plan, files = self.plan()
        (self.target / "changed.txt").write_text("changed after plan\n", encoding="utf-8")

        with self.assertRaisesRegex(LifecycleError, "changed after planning"):
            apply_upgrade(plan, files, confirmation=plan.confirmation)
        self.assertFalse((self.target / "created.txt").exists())

    def test_write_failure_rolls_back_already_applied_files(self) -> None:
        plan, files = self.plan()
        calls = 0

        def fail_second_write(path: Path, content: bytes) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated disk failure")
            _atomic_write(path, content)

        with (
            patch(
                "scripts.github_lifecycle.upgrade._atomic_write",
                side_effect=fail_second_write,
            ),
            self.assertRaisesRegex(LifecycleError, "was rolled back"),
        ):
            apply_upgrade(plan, files, confirmation=plan.confirmation)

        self.assertEqual((self.target / "changed.txt").read_text(), "old\n")
        self.assertFalse((self.target / "created.txt").exists())
        record = load_installation_record(self.target / INSTALLATION_RECORD_PATH)
        self.assertEqual(record.source_ref, "v1.1.0")

    def test_legacy_install_requires_exact_old_package_contents(self) -> None:
        (self.target / INSTALLATION_RECORD_PATH).unlink()
        plan, _ = self.plan()
        self.assertEqual(plan.blockers, ())

        (self.target / "changed.txt").write_text("unknown local baseline\n", encoding="utf-8")
        blocked, _ = self.plan()
        self.assertIn("changed.txt", blocked.blockers)

    def test_packages_reject_path_traversal_and_symlinks(self) -> None:
        traversal = self.root / "traversal.zip"
        with zipfile.ZipFile(traversal, "w") as archive:
            archive.writestr("../outside", "bad")
        with (
            self.assertRaisesRegex(LifecycleError, "unsafe path"),
            materialize_package(traversal),
        ):
            pass

        symlink = self.root / "symlink.zip"
        entry = zipfile.ZipInfo("link")
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(symlink, "w") as archive:
            archive.writestr(entry, "target")
        with (
            self.assertRaisesRegex(LifecycleError, "symlinks"),
            materialize_package(symlink),
        ):
            pass

    def test_upgrade_cli_defaults_to_dry_run(self) -> None:
        output = self.root / "plan.json"
        arguments = [
            "github-lifecycle",
            "upgrade",
            "--from-package",
            str(self.old),
            "--to-package",
            str(self.new),
            "--target",
            str(self.target),
            "--repository",
            REPOSITORY,
            "--default-branch",
            "main",
            "--from-ref",
            "v1.1.0",
            "--to-ref",
            "v1.2.0",
            "--output",
            str(output),
        ]

        with patch("sys.argv", arguments):
            self.assertEqual(main(), 0)

        rendered = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(rendered["mode"], "dry-run")
        self.assertEqual(rendered["confirmation"], plan_confirmation())
        self.assertEqual((self.target / "changed.txt").read_text(), "old\n")


def plan_confirmation() -> str:
    return f"upgrade:{REPOSITORY}:v1.1.0:v1.2.0"


if __name__ == "__main__":
    unittest.main()
