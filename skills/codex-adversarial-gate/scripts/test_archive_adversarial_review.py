#!/usr/bin/env python3
"""Smoke test for archive_adversarial_review.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def run_archive(
    script: Path,
    repo: Path,
    *args: str,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo",
            str(repo),
            *args,
        ],
        check=check,
        text=True,
        capture_output=True,
        input=input_text,
    )


def main() -> int:
    script = Path(__file__).with_name("archive_adversarial_review.py")
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        review = Path(tmp) / "review.md"
        original_review = "\n  # Review\n\n- Disposition: PASS\n\n"
        review.write_text(original_review)

        command = [
            "--kind",
            "completion",
            "--phase",
            "Sample Slice",
            "--reviewer",
            "completion-reviewer",
            "--verdict",
            "PASS",
            "--review-file",
            str(review),
        ]

        result = run_archive(script, repo, *command)
        legacy_command = command.copy()
        legacy_flag_index = legacy_command.index("--reviewer")
        legacy_command[legacy_flag_index] = "--agent"
        second_result = run_archive(script, repo, *legacy_command)

        archive_path = Path(result.stdout.strip())
        second_archive_path = Path(second_result.stdout.strip())
        assert archive_path.exists(), archive_path
        assert second_archive_path.exists(), second_archive_path
        assert archive_path != second_archive_path
        assert archive_path.parent.resolve() == (repo / "docs" / "Adversarial Reviews").resolve()
        text = archive_path.read_text()
        assert "Review kind: `completion`" in text
        assert "Disposition: PASS" in text
        assert text.split("## Review\n\n", 1)[1] == original_review

        stdin_result = run_archive(
            script,
            repo,
            "--kind",
            "critic",
            "--phase",
            "stdin slice",
            "--reviewer",
            "completion-critic",
            "--verdict",
            "AGREE_PASS",
            "--stdin",
            input_text=original_review,
        )
        stdin_archive_path = Path(stdin_result.stdout.strip())
        assert stdin_archive_path.exists(), stdin_archive_path
        assert stdin_archive_path.read_text().split("## Review\n\n", 1)[1] == original_review

        blank_review = Path(tmp) / "blank.md"
        blank_review.write_text("   \n", encoding="utf-8")
        before_blank = sorted((repo / "docs" / "Adversarial Reviews").glob("*.md"))
        blank_result = run_archive(
            script,
            repo,
            "--kind",
            "completion",
            "--phase",
            "blank file",
            "--reviewer",
            "completion-reviewer",
            "--verdict",
            "PASS",
            "--review-file",
            str(blank_review),
            check=False,
        )
        assert blank_result.returncode != 0
        assert "review text is empty" in blank_result.stderr
        assert sorted((repo / "docs" / "Adversarial Reviews").glob("*.md")) == before_blank

        blank_stdin_result = run_archive(
            script,
            repo,
            "--kind",
            "critic",
            "--phase",
            "blank stdin",
            "--reviewer",
            "completion-critic",
            "--verdict",
            "AGREE_PASS",
            "--stdin",
            input_text=" \n",
            check=False,
        )
        assert blank_stdin_result.returncode != 0
        assert "review text is empty" in blank_stdin_result.stderr

        outside = Path(tmp) / "outside"
        outside.mkdir()
        symlink_repo = Path(tmp) / "symlink-repo"
        symlink_repo.mkdir()
        (symlink_repo / "docs").symlink_to(outside, target_is_directory=True)
        escape_result = run_archive(
            script,
            symlink_repo,
            "--kind",
            "completion",
            "--phase",
            "symlink escape",
            "--reviewer",
            "completion-reviewer",
            "--verdict",
            "PASS",
            "--review-file",
            str(review),
            check=False,
        )
        assert escape_result.returncode != 0
        assert "archive directory escapes repo" in escape_result.stderr
        assert not list(outside.rglob("*.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
