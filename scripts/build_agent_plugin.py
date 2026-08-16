#!/usr/bin/env python3
"""Build a clean Agent Plugins v1 package from the shared plugin sources."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "plugins/codex-skills"


def build_agent_plugin(
    output: Path,
    source_root: Path = SOURCE_ROOT,
    license_path: Path = REPO_ROOT / "LICENSE",
) -> None:
    source = source_root.resolve()
    destination = output.resolve()
    if destination == source or source in destination.parents:
        raise ValueError("output must be outside plugins/codex-skills")
    if destination.exists():
        raise FileExistsError(f"output already exists: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}-", dir=destination.parent)
    )
    try:
        shutil.copy2(source / "plugin.json", staging / "plugin.json")
        shutil.copytree(
            source / "skills",
            staging / "skills",
            ignore=lambda directory, _: (
                {"agents"} if Path(directory).parent == source / "skills" else set()
            ),
        )
        portable_mcp = source / "mcp.json"
        if portable_mcp.is_file():
            shutil.copy2(portable_mcp, staging / "mcp.json")
        shutil.copy2(license_path, staging / "LICENSE")
        staging.rename(destination)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a portable Agent Plugins v1 directory"
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        build_agent_plugin(args.output)
    except (FileExistsError, OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Built Agent Plugins package: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
