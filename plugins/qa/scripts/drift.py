#!/usr/bin/env python3
"""Compute the stack-drift records and the `Packs:` line for /qa:review (step 3).

Usage: drift.py [--layers backend,frontend] [--plugin-root DIR] [PROJECT_ROOT]

Reads the project's .claude/project-profile.md (`stacks`, `Layout`), the manifests and
lockfiles in the project root and in each Layout path, and the plugin's `stack-signals.md`
and reference files. Prints one record per line, then `Packs: ...`. Records never fix anything.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import tomllib
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}
FILE_SIGNALS = {
    "docker": ["Dockerfile*", "docker-compose*.yml", "compose*.yaml"],
    "caddy": ["Caddyfile*"],
}
PY_MANIFESTS = ("pyproject.toml", "setup.cfg")
SPEC = re.compile(r"(?<![<!])(?:==|>=|~=|\^|~|=)?\s*v?(\d+)")


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.strip().lower())


def read_profile(root: Path) -> tuple[list[str], list[str]]:
    """Return (stacks, layout directories relative to root)."""
    text = (root / ".claude" / "project-profile.md").read_text()
    stacks: list[str] = []
    m = re.search(r"^stacks:\s*\[(.*?)\]", text, re.M | re.S)
    if m:
        stacks = [s.strip().strip("'\"") for s in m.group(1).split(",") if s.strip()]
    else:
        m = re.search(r"^stacks:\s*\n((?:\s*-\s*\S+\n?)+)", text, re.M)
        if m:
            stacks = [s.strip().lstrip("-").strip() for s in m.group(1).splitlines() if s.strip()]
    dirs: list[str] = []
    sec = re.search(r"^## Layout\n(.*?)^## ", text, re.S | re.M)
    for line in (sec.group(1) if sec else "").splitlines():
        m = re.match(r"-\s*([\w-]+):\s*(.*)$", line.strip())
        if not m or m.group(1) == "ignore":
            continue
        for entry in re.sub(r"\([^)]*\)", "", m.group(2)).split(","):
            entry = entry.strip().strip("`")
            if not entry:
                continue
            entry = entry.split("*")[0]
            p = entry if entry.endswith("/") or "." not in entry.rsplit("/", 1)[-1] else entry.rsplit("/", 1)[0]
            dirs.append(p.strip("/") or ".")
    return stacks, sorted(set(dirs))


def read_signals(plugin_root: Path) -> dict[str, tuple[str, set[str]]]:
    """Map stack key -> (layer, dependency names). File-based keys get an empty set."""
    out: dict[str, tuple[str, set[str]]] = {}
    for line in (plugin_root / "stack-signals.md").read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or not re.fullmatch(r"`[\w-]+`", cells[0]):
            continue
        key = cells[0].strip("`")
        names = {norm(n) for n in re.findall(r"`([^`]+)`", cells[2])} if key not in FILE_SIGNALS else set()
        out[key] = (cells[1], names)
    return out


def read_packs(plugin_root: Path) -> dict[str, tuple[str, int]]:
    """Map stack key -> (layer, written-for major)."""
    out: dict[str, tuple[str, int]] = {}
    for f in sorted((plugin_root / "skills" / "review" / "references").glob("*-*.md")):
        layer, key = f.stem.split("-", 1)
        lines = f.read_text().splitlines()
        m = re.search(r"(\d+)\s*$", lines[2]) if len(lines) > 2 else None
        out[key] = (layer, int(m.group(1)) if m else 0)
    return out


def lower_bound_major(spec: str) -> int | None:
    m = SPEC.search(spec)
    return int(m.group(1)) if m else None


def manifest_deps(d: Path) -> tuple[dict[str, list[int]], bool, int | None]:
    """Return ({dependency: [majors]}, has_python_manifest, requires-python major)."""
    deps: dict[str, list[int]] = {}
    has_py = False
    py_major: int | None = None

    def add(name: str, spec: str) -> None:
        major = lower_bound_major(spec)
        deps.setdefault(norm(re.sub(r"\[.*?\]", "", name)), [])
        if major is not None:
            deps[norm(re.sub(r"\[.*?\]", "", name))].append(major)

    def add_req(req: str) -> None:
        m = re.match(r"\s*([A-Za-z0-9_.\-\[\]]+)\s*(.*)", req.split(";")[0])
        if m and not req.lstrip().startswith(("#", "-")):
            add(m.group(1), m.group(2))

    pp = d / "pyproject.toml"
    if pp.is_file():
        has_py = True
        try:
            data = tomllib.loads(pp.read_text())
        except tomllib.TOMLDecodeError:
            data = {}
        proj = data.get("project", {})
        for r in proj.get("dependencies", []):
            add_req(r)
        for group in proj.get("optional-dependencies", {}).values():
            for r in group:
                add_req(r)
        for group in data.get("dependency-groups", {}).values():
            for r in group:
                if isinstance(r, str):
                    add_req(r)
        poetry = data.get("tool", {}).get("poetry", {})
        tables = [poetry.get("dependencies", {})] + [g.get("dependencies", {}) for g in poetry.get("group", {}).values()]
        for t in tables:
            for name, spec in t.items():
                if name.lower() != "python":
                    add(name, spec if isinstance(spec, str) else str(spec.get("version", "")))
        rp = proj.get("requires-python") or poetry.get("dependencies", {}).get("python")
        if isinstance(rp, str):
            py_major = lower_bound_major(rp)
    if (d / "setup.cfg").is_file():
        has_py = True
        m = re.search(r"install_requires\s*=\s*\n((?:[ \t]+.+\n?)+)", (d / "setup.cfg").read_text())
        for r in (m.group(1).splitlines() if m else []):
            add_req(r)
    for f in d.glob("requirements*.txt"):
        has_py = True
        for r in f.read_text().splitlines():
            add_req(r)
    pj = d / "package.json"
    if pj.is_file():
        try:
            data = json.loads(pj.read_text())
        except json.JSONDecodeError:
            data = {}
        for sect in ("dependencies", "devDependencies"):
            for name, spec in data.get(sect, {}).items():
                add(name, str(spec))
    return deps, has_py, py_major


def resolved(d: Path) -> dict[str, list[int]]:
    """Resolved versions from lockfiles in d: {dependency: [majors]}."""
    out: dict[str, list[int]] = {}

    def put(name: str, version: str) -> None:
        m = re.match(r"v?(\d+)", version)
        if m:
            out.setdefault(norm(name), []).append(int(m.group(1)))

    for lock in ("uv.lock", "poetry.lock"):
        f = d / lock
        if f.is_file():
            try:
                for pkg in tomllib.loads(f.read_text()).get("package", []):
                    put(pkg.get("name", ""), str(pkg.get("version", "")))
            except tomllib.TOMLDecodeError:
                pass
    f = d / "package-lock.json"
    if f.is_file():
        try:
            for path, info in json.loads(f.read_text()).get("packages", {}).items():
                if path.startswith("node_modules/") and "node_modules/" not in path[13:]:
                    put(path[13:], str(info.get("version", "")))
        except json.JSONDecodeError:
            pass
    f = d / "pnpm-lock.yaml"
    if f.is_file():
        for m in re.finditer(r"^\s+'?/?((?:@[\w.\-]+/)?[\w.\-]+)@(\d[\w.\-]*)", f.read_text(), re.M):
            put(m.group(1), m.group(2))
    return out


def file_signal(root: Path, dirs: list[Path], globs: list[str]) -> bool:
    for base in dirs:
        for p in base.rglob("*"):
            if any(part in SKIP_DIRS for part in p.relative_to(base).parts[:-1]):
                continue
            if p.is_file() and any(fnmatch.fnmatch(p.name, g) for g in globs):
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--layers", default="")
    ap.add_argument("--plugin-root", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    root = Path(args.root).resolve()
    plugin = Path(args.plugin_root)
    layers = {x for x in args.layers.split(",") if x}

    stacks, layout_dirs = read_profile(root)
    search = [root] + [root / d for d in layout_dirs if d != "." and (root / d).is_dir()]
    signals = read_signals(plugin)
    packs = read_packs(plugin)

    deps: dict[str, list[int]] = {}
    has_py = False
    py_major: int | None = None
    locked: dict[str, list[int]] = {}
    for d in search:
        dd, hp, pm = manifest_deps(d)
        for k, v in dd.items():
            deps.setdefault(k, []).extend(v)
        has_py = has_py or hp
        py_major = pm if pm is not None else py_major
        for k, v in resolved(d).items():
            locked.setdefault(k, []).extend(v)

    def project_major(key: str) -> str:
        if key == "python":
            return str(py_major) if py_major is not None else "?"
        names = signals.get(key, ("", set()))[1]
        for source in (locked, deps):
            found = [m for n in names for m in source.get(n, [])]
            if found:
                return str(max(found))
        return "?"

    matched: list[str] = []
    for key, (_layer, names) in signals.items():
        if key == "python":
            hit = has_py
        elif key in FILE_SIGNALS:
            hit = file_signal(root, search, FILE_SIGNALS[key])
        else:
            hit = any(n in deps for n in names)
        if hit:
            matched.append(key)

    records: list[str] = []
    for key in matched:
        if key not in stacks:
            records.append(f"STACK {key} ({'pack available' if key in packs else 'no pack'})")
    for key in stacks:
        if key not in matched and key not in packs:
            records.append(f"STACK {key} (unknown key)")
    if not matched and not has_py and not any((d / "package.json").is_file() for d in search):
        records.append("STACK ? (no manifest found in " + ", ".join(str(d.relative_to(root)) or "." for d in search) + ")")

    loaded: list[str] = []
    for key in stacks:
        if key in packs and (not layers or packs[key][0] in layers):
            written = packs[key][1]
            proj = project_major(key)
            loaded.append(f"{key} {written}/{proj}")
            if proj != "?" and int(proj) > written:
                records.append(f"PACK {key} (written for {written}, project uses {proj}): may be stale")

    print("\n".join(records) if records else "none")
    print("Packs: " + (", ".join(loaded) if loaded else "none loaded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
