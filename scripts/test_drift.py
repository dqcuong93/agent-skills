#!/usr/bin/env python3
"""Tests for plugins/qa/scripts/drift.py, run against a fake plugin tree and fake projects."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "plugins" / "qa" / "scripts" / "drift.py"
SIGNALS = """# Stack signals

| Stack key | Layer | Signals (dependency names) |
|---|---|---|
| `python` | backend | any Python manifest above |
| `django` | backend | `django`, `djangorestframework` |
| `celery` | backend | `celery` |
| `vue` | frontend | `vue` |
| `docker` | infra | a `Dockerfile*` anywhere in the repo |
| `caddy` | infra | a `Caddyfile*` anywhere in the repo |
| `mkdocs` | docs | a `mkdocs.yml` anywhere in the repo |
"""


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class DriftTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.plugin = base / "plugin"
        self.proj = base / "proj"
        write(self.plugin / "stack-signals.md", SIGNALS)
        refs = self.plugin / "skills" / "review" / "references"
        write(refs / "backend-python.md", "# P\n\nWritten for: Python 3\n")
        write(refs / "backend-django.md", "# D\n\nWritten for: Django 6\n")
        write(refs / "frontend-vue.md", "# V\n\nWritten for: Vue 3\n")
        write(refs / "docs-mkdocs.md", "# M\n\nWritten for: MkDocs 1\n")
        for layer in ("backend", "frontend", "docs"):
            write(refs / f"{layer}.md", f"# {layer}\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def profile(self, stacks: str, layout: str = "- backend: .\n- frontend: fe/\n",
                front: str = "confirmed: 2026-10-01\n", extra: str = "") -> None:
        write(self.proj / ".claude" / "project-profile.md",
              f"---\nstacks: [{stacks}]\n{front}---\n\n# Project profile\n\n## Layout\n\n{layout}\n"
              f"## Commands\n\n## Backend checks\n\n## Frontend checks\n\n{extra}")

    def run_drift(self, *extra: str) -> list[str]:
        out = subprocess.run(
            [sys.executable, str(SCRIPT), "--plugin-root", str(self.plugin), "--today", "2026-10-06", *extra, str(self.proj)],
            capture_output=True, text=True, check=True,
        ).stdout
        return out.strip().splitlines()

    def test_clean_with_lockfile_and_manifests(self) -> None:
        self.profile("python, django, vue")
        write(self.proj / "pyproject.toml",
              '[project]\nrequires-python = ">=3.12"\ndependencies = ["django>=5"]\n')
        write(self.proj / "uv.lock", '[[package]]\nname = "django"\nversion = "6.0.7"\n')
        write(self.proj / "fe" / "package.json", '{"dependencies": {"vue": "^3.5.0"}}')
        self.assertEqual(self.run_drift(), ["none", "Packs: python 3/3, django 6/6, vue 3/3"])

    def test_stale_pack_when_project_major_is_higher(self) -> None:
        self.profile("python, django")
        write(self.proj / "pyproject.toml", '[project]\ndependencies = ["django>=7.0"]\n')
        out = self.run_drift()
        self.assertIn("PACK django (written for 6, project uses 7): may be stale", out)
        self.assertEqual(out[-1], "Packs: python 3/?, django 6/7")

    def test_layers_argument_limits_loaded_packs(self) -> None:
        self.profile("python, django, vue")
        write(self.proj / "pyproject.toml", '[project]\ndependencies = ["django==6.0"]\n')
        write(self.proj / "fe" / "package.json", '{"dependencies": {"vue": "3.5.0"}}')
        self.assertEqual(self.run_drift("--layers", "frontend")[-1], "Packs: vue 3/3")

    def test_missing_keys_pack_available_and_no_pack(self) -> None:
        self.profile("python")
        write(self.proj / "pyproject.toml", '[project]\ndependencies = ["django>=6", "celery>=5"]\n')
        write(self.proj / "fe" / "package.json", '{"dependencies": {"vue": "^3"}}')
        out = self.run_drift()
        self.assertIn("STACK django (pack available)", out)
        self.assertIn("STACK celery (no pack)", out)
        self.assertIn("STACK vue (pack available)", out)

    def test_unknown_key(self) -> None:
        self.profile("python, rails")
        write(self.proj / "pyproject.toml", "[project]\n")
        self.assertIn("STACK rails (unknown key)", self.run_drift())

    def test_no_manifest(self) -> None:
        self.profile("python")
        out = self.run_drift()
        self.assertTrue(any(line.startswith("STACK ? (no manifest found in") for line in out))

    def test_docker_found_in_nested_dir_without_pack(self) -> None:
        self.profile("python", "- backend: be/\n")
        write(self.proj / "be" / "pyproject.toml", "[project]\n")
        write(self.proj / "be" / "Dockerfile", "FROM python:3.12\n")
        self.assertIn("STACK docker (no pack)", self.run_drift())

    def test_layout_note_and_commas_in_parentheses_are_ignored(self) -> None:
        self.profile("python", "- backend: be/ (Django, DRF)\n- ignore: scripts/\n")
        write(self.proj / "be" / "pyproject.toml", '[project]\ndependencies = ["django>=6"]\n')
        out = self.run_drift()
        self.assertIn("STACK django (pack available)", out)

    def test_mkdocs_file_signal_and_loaded_pack(self) -> None:
        self.profile("python", "- backend: .\n- docs: docs/\n")
        write(self.proj / "pyproject.toml", "[project]\n")
        write(self.proj / "mkdocs-config" / "mkdocs.yml", "site_name: x\n")
        self.assertIn("STACK mkdocs (pack available)", self.run_drift())
        self.profile("python, mkdocs", "- backend: .\n- docs: docs/\n")
        self.assertEqual(self.run_drift("--layers", "docs"), ["none", "Packs: mkdocs 1/?"])

    def test_profile_not_confirmed_or_too_old(self) -> None:
        write(self.proj / "pyproject.toml", "[project]\n")
        self.profile("python", "- backend: .\n", front="")
        self.assertIn("PROFILE (no confirmed date)", self.run_drift())
        self.profile("python", "- backend: .\n", front="confirmed: 2026-01-01\nreview-after-days: 30\n")
        self.assertIn("PROFILE (confirmed 2026-01-01, 278 days ago; limit 30)", self.run_drift())
        self.profile("python", "- backend: .\n", front="confirmed: 2026-09-20\n")
        self.assertNotIn("PROFILE", " ".join(self.run_drift()))

    def test_profile_written_with_older_plugin(self) -> None:
        write(self.proj / "pyproject.toml", "[project]\n")
        write(self.plugin / ".claude-plugin" / "plugin.json", '{"version": "0.4.1"}')
        self.profile("python", "- backend: .\n", front="confirmed: 2026-10-01\nplugin: 0.3.0\n")
        self.assertIn("PROFILE (written with plugin 0.3.0, installed 0.4.1)", self.run_drift())
        self.profile("python", "- backend: .\n", front="confirmed: 2026-10-01\nplugin: 0.4.0\n")
        self.assertNotIn("PROFILE", " ".join(self.run_drift()))

    def test_gap_for_layer_without_checklist_or_profile_checks(self) -> None:
        write(self.proj / "pyproject.toml", "[project]\n")
        write(self.plugin / "skills" / "review" / "references" / "backend.md", "# B\n")
        self.profile("python", "- backend: .\n- ops: ops/\n- tests: t/\n- ignore: x/\n")
        out = self.run_drift()
        self.assertIn("GAP layer ops (no checklist in the plugin and no profile checks)", out)
        self.assertNotIn("GAP layer backend (no checklist in the plugin and no profile checks)", out)
        self.assertFalse(any(l.startswith("GAP layer tests") or l.startswith("GAP layer ignore") for l in out))
        self.profile("python", "- backend: .\n- ops: ops/\n", extra="## Ops checks\n\n- Rotate keys.\n")
        self.assertNotIn("GAP layer ops (no checklist in the plugin and no profile checks)", self.run_drift())


if __name__ == "__main__":
    unittest.main()
