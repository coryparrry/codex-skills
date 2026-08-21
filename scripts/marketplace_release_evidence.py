#!/usr/bin/env python3
"""Emit machine-readable evidence for the Codex Git marketplace boundary."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_release_contract import (  # noqa: E402
    AGENT_PLUGIN_MANIFEST,
    CODEX_PLUGIN_MANIFEST,
    MARKETPLACE_MANIFEST,
    changed_paths,
    load_json,
    parse_semver,
    shipped_plugin_change,
    validate_catalogue,
)

PLUGIN_NAME = "codex-skills"
COMMIT = re.compile(r"^[0-9a-fA-F]{40}$")
POST_MERGE_COMMANDS = [
    "codex plugin marketplace upgrade codex-skills",
    "codex plugin remove codex-skills@codex-skills",
    "codex plugin add codex-skills@codex-skills --json",
    "codex plugin list --marketplace codex-skills --available --json",
]


class EvidenceError(Exception):
    """An invalid repository or evidence input."""


def _git(repo: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        raise EvidenceError(f"git {' '.join(arguments)} failed: {detail}") from error
    return result.stdout.strip()


def _required_json(repo: Path, relative_path: Path) -> dict[str, Any]:
    data, errors = load_json(repo / relative_path)
    if errors:
        raise EvidenceError("; ".join(errors))
    return data


def _manifest_versions(repo: Path) -> dict[str, str]:
    codex = _required_json(repo, CODEX_PLUGIN_MANIFEST)
    portable = _required_json(repo, AGENT_PLUGIN_MANIFEST)
    if codex.get("name") != PLUGIN_NAME:
        raise EvidenceError(f"Codex manifest name must be {PLUGIN_NAME}")
    if portable.get("name") != PLUGIN_NAME:
        raise EvidenceError(f"portable manifest name must be {PLUGIN_NAME}")
    try:
        parse_semver(str(codex.get("version", "")))
        parse_semver(str(portable.get("version", "")))
    except ValueError as error:
        raise EvidenceError(str(error)) from error
    codex_version = codex.get("version")
    portable_version = portable.get("version")
    if codex_version != portable_version:
        raise EvidenceError(
            "Codex and portable manifest versions must match: "
            f"{codex_version} != {portable_version}"
        )
    return {
        "plugin_version": codex_version,
        "codex_manifest_version": codex_version,
        "portable_manifest_version": portable_version,
    }


def _marketplace_evidence(repo: Path) -> dict[str, Any]:
    marketplace = _required_json(repo, MARKETPLACE_MANIFEST)
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        raise EvidenceError("marketplace must contain exactly one plugin")
    entry = plugins[0]
    if not isinstance(entry, dict):
        raise EvidenceError("marketplace plugin entry must be an object")
    source = entry.get("source")
    policy = entry.get("policy")
    if not isinstance(source, dict) or not isinstance(policy, dict):
        raise EvidenceError("marketplace source and policy must be objects")
    category = entry.get("category")
    if not isinstance(category, str) or not category.strip():
        raise EvidenceError("marketplace plugin category is required")
    return {
        "marketplace_name": marketplace.get("name"),
        "marketplace_plugin_name": entry.get("name"),
        "marketplace_source": {
            "source": source.get("source"),
            "path": source.get("path"),
        },
        "marketplace_policy": {
            "installation": policy.get("installation"),
            "authentication": policy.get("authentication"),
        },
        "marketplace_category": category,
    }


def _resolve_commit(repo: Path, value: str, label: str) -> str:
    if not value or not COMMIT.fullmatch(value):
        raise EvidenceError(f"{label} must be a full 40-character commit SHA")
    resolved = _git(
        repo,
        "rev-parse",
        "--verify",
        "--quiet",
        "--end-of-options",
        f"{value}^{{commit}}",
    )
    if resolved.lower() != value.lower():
        raise EvidenceError(f"{label} does not resolve to the supplied commit")
    return resolved


def _resolve_base(repo: Path, base_ref: str | None) -> tuple[str | None, str | None]:
    if base_ref is None:
        return None, None
    if not base_ref.strip() or "\x00" in base_ref:
        raise EvidenceError("base ref must be non-empty")
    resolved = _git(
        repo,
        "rev-parse",
        "--verify",
        "--quiet",
        "--end-of-options",
        f"{base_ref}^{{commit}}",
    )
    if not COMMIT.fullmatch(resolved):
        raise EvidenceError(f"base ref does not resolve to a commit: {base_ref}")
    return base_ref, resolved


def build_receipt(
    repo: Path,
    *,
    event: str,
    base_ref: str | None = None,
    tested_commit: str | None = None,
    pull_request_head_commit: str | None = None,
    ref: str | None = None,
) -> dict[str, Any]:
    if event not in {"pull_request", "push", "workflow_dispatch"}:
        raise EvidenceError(f"unsupported event: {event}")
    repo = repo.resolve()
    if event == "pull_request" and not base_ref:
        raise EvidenceError("pull_request evidence requires --base-ref")

    tested_commit = tested_commit or (
        os.environ.get("GITHUB_SHA") if event == "push" else None
    )
    tested_head = _git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    if not COMMIT.fullmatch(tested_head):
        raise EvidenceError("repository HEAD is not a full commit SHA")
    if event == "push" and tested_commit is None:
        raise EvidenceError("push evidence requires --tested-commit or GITHUB_SHA")
    if tested_commit is not None:
        _resolve_commit(repo, tested_commit, "tested commit evidence")
        if tested_commit.lower() != tested_head.lower():
            raise EvidenceError(
                "tested commit evidence does not match repository HEAD"
            )
    if pull_request_head_commit is not None:
        _resolve_commit(repo, pull_request_head_commit, "pull-request head commit")

    supplied_ref = ref if ref is not None else os.environ.get("GITHUB_REF")
    if event == "push" and supplied_ref and supplied_ref != "refs/heads/main":
        raise EvidenceError("push evidence must target refs/heads/main")
    resolved_base_ref, resolved_base = _resolve_base(repo, base_ref)
    if resolved_base is None:
        changed: list[str] = []
        change_errors: list[str] = []
    else:
        changed_set, change_errors = changed_paths(repo, resolved_base)
        changed = sorted(changed_set)
    if change_errors:
        raise EvidenceError("; ".join(change_errors))

    catalogue_errors, _ = validate_catalogue(repo)
    if catalogue_errors:
        raise EvidenceError("; ".join(catalogue_errors))
    manifest = _manifest_versions(repo)
    marketplace = _marketplace_evidence(repo)
    shipped_changed = (
        shipped_plugin_change(set(changed)) if resolved_base is not None else None
    )
    if shipped_changed is True:
        local_status = "required_after_merge"
    elif shipped_changed is False:
        local_status = "not_required_for_change"
    else:
        local_status = "unknown"

    return {
        "schema_version": 1,
        "event": event,
        "ref": supplied_ref,
        "tested_commit": tested_head,
        "base_ref": resolved_base_ref,
        "base_commit": resolved_base,
        "pull_request_head_commit": pull_request_head_commit,
        "changed_paths": changed,
        "shipped_plugin_content_changed": shipped_changed,
        **manifest,
        **marketplace,
        "plugin": {
            "name": PLUGIN_NAME,
            "version": manifest["plugin_version"],
            "codex_manifest_version": manifest["codex_manifest_version"],
            "portable_manifest_version": manifest["portable_manifest_version"],
        },
        "marketplace": {
            "name": marketplace["marketplace_name"],
            "plugin_name": marketplace["marketplace_plugin_name"],
            "source": marketplace["marketplace_source"],
            "policies": marketplace["marketplace_policy"],
            "category": marketplace["marketplace_category"],
        },
        "mirror_catalogue": {"status": "valid"},
        "mirror_catalogue_status": "valid",
        "repository_candidate_status": "valid",
        "repository_candidate": {
            "status": "valid",
            "tested_commit": tested_head,
            "source": "Git repository snapshot",
        },
        "local_codex_refresh_verified": False,
        "local_codex_refresh_status": local_status,
        "post_merge_commands": POST_MERGE_COMMANDS,
    }


def _write_receipt(receipt: dict[str, Any], output: str | None) -> None:
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--event",
        required=True,
        choices=("pull_request", "push", "workflow_dispatch"),
    )
    parser.add_argument("--base-ref", help="Git base commit or ref")
    parser.add_argument(
        "--tested-commit",
        "--head-commit",
        dest="tested_commit",
        help="Exact commit SHA checked out and tested by CI",
    )
    parser.add_argument(
        "--pull-request-head-commit",
        help="Optional PR source commit SHA, distinct from a merge commit",
    )
    parser.add_argument("--ref", help="Git ref associated with the event")
    parser.add_argument("--output", help="Write the receipt to this path")
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository checkout (defaults to this script's repository)",
    )
    args = parser.parse_args(argv)
    try:
        receipt = build_receipt(
            args.repo,
            event=args.event,
            base_ref=args.base_ref,
            tested_commit=args.tested_commit,
            pull_request_head_commit=args.pull_request_head_commit,
            ref=args.ref,
        )
        _write_receipt(receipt, args.output)
    except (EvidenceError, OSError) as error:
        print(f"marketplace release evidence: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
