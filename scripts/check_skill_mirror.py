#!/usr/bin/env python3
"""Check source skill and plugin mirror parity."""

from __future__ import annotations

import filecmp
import sys
from pathlib import Path


IGNORED_NAMES = {"__pycache__", ".pytest_cache", ".DS_Store"}


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_NAMES for part in path.parts):
            continue
        if path.is_file():
            files.append(path.relative_to(root))
    return files


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_skill_mirror.py <skill-name>", file=sys.stderr)
        return 2

    skill_name = sys.argv[1]
    repo = Path.cwd()
    source = repo / "skills" / skill_name
    mirror = repo / "plugins" / "codex-skills" / "skills" / skill_name

    if not source.is_dir():
        print(f"missing source skill: {source}", file=sys.stderr)
        return 1
    if not mirror.is_dir():
        print(f"missing plugin mirror: {mirror}", file=sys.stderr)
        return 1

    source_files = set(iter_files(source))
    mirror_files = set(iter_files(mirror))
    failures: list[str] = []

    for path in sorted(source_files - mirror_files):
        failures.append(f"missing from mirror: {path}")
    for path in sorted(mirror_files - source_files):
        failures.append(f"extra in mirror: {path}")
    for path in sorted(source_files & mirror_files):
        if not filecmp.cmp(source / path, mirror / path, shallow=False):
            failures.append(f"content differs: {path}")

    if failures:
        print("\n".join(failures))
        return 1

    print(f"mirror ok: {skill_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
