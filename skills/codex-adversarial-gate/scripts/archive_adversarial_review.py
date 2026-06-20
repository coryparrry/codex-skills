#!/usr/bin/env python3
"""Archive an adversarial review under docs/Adversarial Reviews."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ARCHIVE_DIR = Path("docs") / "Adversarial Reviews"


def slugify(value: str, fallback: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or fallback


def read_review(args: argparse.Namespace) -> str:
    if args.stdin:
        text = sys.stdin.read()
    else:
        text = Path(args.review_file).read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit("review text is empty")
    return text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Repository root.")
    parser.add_argument(
        "--kind",
        required=True,
        choices=("plan", "completion", "critic"),
        help="Review kind.",
    )
    parser.add_argument("--phase", required=True, help="Plan, phase, or slice name.")
    parser.add_argument("--reviewer", dest="reviewer", help="Reviewer role or label.")
    parser.add_argument("--agent", dest="reviewer", help=argparse.SUPPRESS)
    parser.add_argument("--verdict", required=True, help="Reviewer disposition/verdict.")
    parser.add_argument("--resolution", default="", help="Implementer resolution when known.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--review-file", help="Path containing exact review output.")
    source.add_argument("--stdin", action="store_true", help="Read exact review output from stdin.")
    return parser


def ensure_repo_child(path: Path, repo: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(repo)
    except ValueError as exc:
        raise SystemExit(f"{label} escapes repo: {path}") from exc
    return resolved


def prepare_archive_dir(repo: Path) -> Path:
    archive_dir = repo / ARCHIVE_DIR
    existing_parent = archive_dir
    while not existing_parent.exists():
        existing_parent = existing_parent.parent
    ensure_repo_child(existing_parent, repo, "archive directory")
    archive_dir.mkdir(parents=True, exist_ok=True)
    return ensure_repo_child(archive_dir, repo, "archive directory")


def write_archive_file(archive_dir: Path, archive_path: Path, content: str) -> bool:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=archive_dir,
            prefix=".tmp-",
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temp_path, archive_path)
        temp_path.unlink()
        return True
    except FileExistsError:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        return False
    except OSError as exc:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise SystemExit(f"could not write archive: {exc}") from exc


def main() -> int:
    args = build_parser().parse_args()
    if not args.reviewer:
        raise SystemExit("--reviewer is required")
    repo = Path(args.repo).expanduser().resolve()
    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"repo does not exist or is not a directory: {repo}")

    review = read_review(args)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S%fZ")
    phase_slug = slugify(args.phase, "review")
    verdict_slug = slugify(args.verdict, "verdict")
    filename_stem = f"{timestamp}-{args.kind}-{phase_slug}-{verdict_slug}"
    archive_dir = prepare_archive_dir(repo)

    for suffix in [""] + [f"-{index}" for index in range(1, 1000)]:
        archive_path = archive_dir / f"{filename_stem}{suffix}.md"
        rel_path = archive_path.relative_to(repo)
        title = f"{args.kind.title()} Adversarial Review: {args.phase}"
        metadata = [
            f"# {title}",
            "",
            f"- Review kind: `{args.kind}`",
            f"- Phase/slice: `{args.phase}`",
            f"- Reviewer: `{args.reviewer}`",
            f"- Verdict: `{args.verdict}`",
            f"- Created: `{timestamp}`",
            f"- Archive path: `{rel_path}`",
        ]
        if args.resolution:
            metadata.append(f"- Implementer resolution: `{args.resolution}`")
        content = "\n".join(metadata) + "\n\n## Review\n\n" + review
        if write_archive_file(archive_dir, archive_path, content):
            break
    else:
        raise SystemExit("could not create a unique archive filename")

    print(archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
