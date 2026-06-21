#!/usr/bin/env python3
"""Deterministic state CLI for the experimental Codex PR packet loop."""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
STATE_DIR = Path(".codex") / "packet-loop"
PACKETS_DIR = STATE_DIR / "packets"
MANIFEST_PATH = STATE_DIR / "manifest.json"
EVENTS_PATH = STATE_DIR / "events.jsonl"
DASHBOARD_PATH = Path("docs") / "codex" / "packet-loop.md"
PACKET_ID_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-")

STATUSES = {
    "candidate",
    "ready",
    "reserved",
    "in-progress",
    "pr-open",
    "reviewing",
    "merge-eligible",
    "needs-fix",
    "blocked",
    "needs-reslice",
    "merged",
    "rejected",
}
RISKS = {"low", "medium", "high"}
PARALLEL_SAFE = {"yes", "no", "maybe"}
MODES = {"planning"}
HUMAN_GATED_STATUSES = {"merged", "rejected"}
ALLOWED_TRANSITIONS = {
    "candidate": {"ready", "blocked", "needs-reslice", "rejected"},
    "ready": {"blocked", "needs-reslice", "rejected"},
    "reserved": {"ready", "in-progress", "blocked", "needs-reslice", "rejected"},
    "in-progress": {"ready", "pr-open", "needs-fix", "blocked", "needs-reslice", "rejected"},
    "pr-open": {"reviewing", "needs-fix", "blocked", "rejected"},
    "reviewing": {"merge-eligible", "needs-fix", "blocked", "rejected"},
    "merge-eligible": {"needs-fix", "blocked", "merged", "rejected"},
    "needs-fix": {"in-progress", "blocked", "needs-reslice", "rejected"},
    "blocked": {"ready", "needs-reslice", "rejected"},
    "needs-reslice": {"candidate", "rejected"},
    "merged": set(),
    "rejected": set(),
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include timezone offset")
    return parsed.astimezone(timezone.utc)


def repo_path(repo: Path, relative: Path) -> Path:
    return repo / relative


def state_dir(repo: Path) -> Path:
    return repo_path(repo, STATE_DIR)


def packets_dir(repo: Path) -> Path:
    return repo_path(repo, PACKETS_DIR)


def manifest_path(repo: Path) -> Path:
    return repo_path(repo, MANIFEST_PATH)


def events_path(repo: Path) -> Path:
    return repo_path(repo, EVENTS_PATH)


def dashboard_path(repo: Path) -> Path:
    return repo_path(repo, DASHBOARD_PATH)


def packet_path(repo: Path, packet_id: str) -> Path:
    safe_packet_id = validate_packet_id(packet_id)
    return packets_dir(repo) / f"{safe_packet_id}.json"


def validate_packet_id(packet_id: str) -> str:
    if (
        not isinstance(packet_id, str)
        or not packet_id
        or Path(packet_id).is_absolute()
        or "/" in packet_id
        or "\\" in packet_id
        or ".." in packet_id
        or not packet_id[0].isalnum()
        or any(char not in PACKET_ID_CHARS for char in packet_id)
    ):
        raise PacketLoopError(f"invalid packet id: {packet_id!r}")
    return packet_id


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise PacketLoopError(f"missing required file: {path}") from None
    except json.JSONDecodeError as exc:
        raise PacketLoopError(f"invalid JSON in {path}: {exc}") from None
    if not isinstance(data, dict):
        raise PacketLoopError(f"expected JSON object in {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def load_manifest(repo: Path) -> dict[str, Any]:
    return read_json(manifest_path(repo))


def write_manifest(repo: Path, manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = now_iso()
    write_json(manifest_path(repo), manifest)


def load_packet(repo: Path, packet_id: str) -> dict[str, Any]:
    return read_json(packet_path(repo, packet_id))


def write_packet(repo: Path, packet: dict[str, Any]) -> None:
    packet["updated_at"] = now_iso()
    write_json(packet_path(repo, str(packet["id"])), packet)


def append_event(repo: Path, event_type: str, details: dict[str, Any]) -> None:
    path = events_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "timestamp": now_iso(),
        "event": event_type,
        "details": details,
    }
    with path.open("a") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def load_packets(repo: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    packets = []
    packet_order = manifest.get("packet_order", [])
    if not isinstance(packet_order, list):
        raise PacketLoopError("manifest packet_order must be a list")
    for packet_id in packet_order:
        if not isinstance(packet_id, str):
            raise PacketLoopError("manifest packet_order entries must be strings")
        packets.append(load_packet(repo, packet_id))
    return packets


def render_dashboard(repo: Path) -> None:
    manifest = load_manifest(repo)
    packets = load_packets(repo, manifest)
    lines = [
        "# Codex PR Packet Loop",
        "",
        f"- Repository: {manifest['repo']['name']}",
        f"- Target branch: {manifest['repo']['target_branch']}",
        f"- Schema version: {manifest['schema_version']}",
        f"- Updated: {manifest['updated_at']}",
        "",
        "| Packet | Status | Goal | Branch | Worktree | Lease owner |",
        "|---|---|---|---|---|---|",
    ]
    for packet in packets:
        lease = packet.get("lease") or {}
        lines.append(
            "| {packet_id} | {status} | {goal} | {branch} | {worktree} | {owner} |".format(
                packet_id=escape_cell(str(packet.get("id", ""))),
                status=escape_cell(str(packet.get("status", ""))),
                goal=escape_cell(str(packet.get("goal", ""))),
                branch=escape_cell(str(packet.get("branch") or "")),
                worktree=escape_cell(str(packet.get("worktree") or "")),
                owner=escape_cell(str(lease.get("owner_thread", ""))),
            )
        )
    lines.append("")
    path = dashboard_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"manifest schema_version must be {SCHEMA_VERSION}")
    repo = manifest.get("repo")
    if not isinstance(repo, dict):
        errors.append("manifest repo must be an object")
    else:
        if not isinstance(repo.get("name"), str) or not repo.get("name"):
            errors.append("manifest repo.name must be a non-empty string")
        if not isinstance(repo.get("default_branch"), str) or not repo.get("default_branch"):
            errors.append("manifest repo.default_branch must be a non-empty string")
        if not isinstance(repo.get("target_branch"), str) or not repo.get("target_branch"):
            errors.append("manifest repo.target_branch must be a non-empty string")
    mode = manifest.get("mode")
    if mode not in MODES:
        errors.append(f"manifest mode is invalid: {mode}")
    dispatch_policy = manifest.get("dispatch_policy")
    if not isinstance(dispatch_policy, dict):
        errors.append("manifest dispatch_policy must be an object")
    else:
        if dispatch_policy.get("mode") != "no_fixed_limit":
            errors.append("manifest dispatch_policy.mode must be no_fixed_limit")
        max_active = dispatch_policy.get("max_active_worktrees")
        if max_active is not None and (isinstance(max_active, bool) or not isinstance(max_active, int) or max_active < 1):
            errors.append("manifest dispatch_policy.max_active_worktrees must be a positive integer or null")
    resource_lanes = manifest.get("resource_lanes")
    if not isinstance(resource_lanes, dict):
        errors.append("manifest resource_lanes must be an object")
    else:
        for lane_name in ("xctest", "computer-use"):
            lane = resource_lanes.get(lane_name)
            if not isinstance(lane, dict):
                errors.append(f"manifest resource_lanes.{lane_name} must be an object")
                continue
            if lane.get("mode") != "serialized":
                errors.append(f"manifest resource_lanes.{lane_name}.mode must be serialized")
            if lane.get("active_packet") is not None and not isinstance(lane.get("active_packet"), str):
                errors.append(f"manifest resource_lanes.{lane_name}.active_packet must be a string or null")
            if not isinstance(lane.get("queue"), list) or any(not isinstance(item, str) for item in lane.get("queue", [])):
                errors.append(f"manifest resource_lanes.{lane_name}.queue must be a list of strings")
    packet_order = manifest.get("packet_order")
    if not isinstance(packet_order, list):
        errors.append("manifest packet_order must be a list")
    else:
        seen = set()
        for packet_id in packet_order:
            if not isinstance(packet_id, str):
                errors.append("manifest packet_order entries must be strings")
            else:
                try:
                    validate_packet_id(packet_id)
                except PacketLoopError as exc:
                    errors.append(str(exc))
                if packet_id in seen:
                    errors.append("manifest packet_order must not contain duplicates")
                else:
                    seen.add(packet_id)
    return errors


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors = []
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"packet {packet.get('id', '<unknown>')} schema_version must be {SCHEMA_VERSION}")
    try:
        validate_packet_id(packet.get("id", ""))
    except PacketLoopError as exc:
        errors.append(str(exc))
    for field in ("id", "title", "goal", "status", "risk", "parallel_safe"):
        if not isinstance(packet.get(field), str) or not packet.get(field):
            errors.append(f"packet {packet.get('id', '<unknown>')} {field} must be a non-empty string")
    status = packet.get("status")
    if status not in STATUSES:
        errors.append(f"packet {packet.get('id', '<unknown>')} status is invalid: {status}")
    risk = packet.get("risk")
    if risk not in RISKS:
        errors.append(f"packet {packet.get('id', '<unknown>')} risk is invalid: {risk}")
    parallel_safe = packet.get("parallel_safe")
    if parallel_safe not in PARALLEL_SAFE:
        errors.append(f"packet {packet.get('id', '<unknown>')} parallel_safe is invalid: {parallel_safe}")
    for field in (
        "allowed_scope",
        "expected_touched_areas",
        "avoid_scope",
        "dependencies",
        "evidence_paths",
        "blockers",
        "reserved_areas",
        "resource_lanes",
        "blocked_by",
        "overlap_notes",
        "source_plan_refs",
    ):
        if not isinstance(packet.get(field), list):
            errors.append(f"packet {packet.get('id', '<unknown>')} {field} must be a list")
    if not isinstance(packet.get("status_reason"), str) or not packet.get("status_reason"):
        errors.append(f"packet {packet.get('id', '<unknown>')} status_reason must be a non-empty string")
    if not isinstance(packet.get("human_review_required"), bool):
        errors.append(f"packet {packet.get('id', '<unknown>')} human_review_required must be a boolean")
    if packet.get("plan_format_status") not in {"pending", "valid", "invalid"}:
        errors.append(f"packet {packet.get('id', '<unknown>')} plan_format_status must be pending, valid, or invalid")
    for optional_field in ("parent_plan_path", "child_plan_path"):
        value = packet.get(optional_field)
        if value is not None and not isinstance(value, str):
            errors.append(f"packet {packet.get('id', '<unknown>')} {optional_field} must be a string or null")
    for optional_field in ("needs_reslice_reason", "last_validation", "worker_report", "review_report"):
        value = packet.get(optional_field)
        if value is not None and not isinstance(value, str):
            errors.append(f"packet {packet.get('id', '<unknown>')} {optional_field} must be a string or null")
    pr = packet.get("pr")
    if not isinstance(pr, dict):
        errors.append(f"packet {packet.get('id', '<unknown>')} pr must be an object")
    else:
        for key in ("url", "state", "head", "base"):
            value = pr.get(key)
            if value is not None and not isinstance(value, str):
                errors.append(f"packet {packet.get('id', '<unknown>')} pr.{key} must be a string or null")
        number = pr.get("number")
        if number is not None and (isinstance(number, bool) or not isinstance(number, int)):
            errors.append(f"packet {packet.get('id', '<unknown>')} pr.number must be an integer or null")
    if "out_of_scope" in packet and not isinstance(packet["out_of_scope"], list):
        errors.append(f"packet {packet.get('id', '<unknown>')} out_of_scope must be a list")
    validation = packet.get("validation")
    if not isinstance(validation, dict):
        errors.append(f"packet {packet.get('id', '<unknown>')} validation must be an object")
    else:
        commands = validation.get("commands")
        if (
            not isinstance(commands, list)
            or not commands
            or any(not isinstance(command, str) or not command for command in commands)
        ):
            errors.append(f"packet {packet.get('id', '<unknown>')} validation.commands must be non-empty strings")
    lease = packet.get("lease")
    if status in {"reserved", "in-progress"}:
        if not isinstance(lease, dict):
            errors.append(f"{status} packet requires lease")
        if not isinstance(packet.get("branch"), str) or not packet.get("branch"):
            errors.append(f"{status} packet requires branch")
        if not isinstance(packet.get("worktree"), str) or not packet.get("worktree"):
            errors.append(f"{status} packet requires worktree")
    if lease is not None:
        if not isinstance(lease, dict):
            errors.append(f"packet {packet.get('id', '<unknown>')} lease must be an object or null")
        else:
            if not isinstance(lease.get("owner_thread"), str) or not lease.get("owner_thread"):
                errors.append(f"packet {packet.get('id', '<unknown>')} lease.owner_thread must be set")
            if not isinstance(lease.get("expires_at"), str) or not lease.get("expires_at"):
                errors.append(f"packet {packet.get('id', '<unknown>')} lease.expires_at must be set")
            else:
                try:
                    parse_time(lease["expires_at"])
                except ValueError:
                    errors.append(f"packet {packet.get('id', '<unknown>')} lease.expires_at is invalid")
    return errors


def validate_repo(repo: Path) -> list[str]:
    errors = []
    try:
        manifest = load_manifest(repo)
    except PacketLoopError as exc:
        return [str(exc)]
    errors.extend(validate_manifest(manifest))
    packet_order = manifest.get("packet_order", [])
    if not isinstance(packet_order, list):
        return errors
    for packet_id in packet_order:
        if not isinstance(packet_id, str):
            continue
        try:
            packet = load_packet(repo, packet_id)
        except PacketLoopError as exc:
            errors.append(str(exc))
            continue
        if packet.get("id") != packet_id:
            errors.append(f"packet file {packet_id}.json contains id {packet.get('id')}")
        errors.extend(validate_packet(packet))
    return errors


def packet_list(values: list[str] | None) -> list[str]:
    return values if values is not None else []


def optional_text(value: str | None) -> str | None:
    return value if value else None


def default_pr() -> dict[str, Any]:
    return {"url": None, "number": None, "state": None, "head": None, "base": None}


def add_unique_path(paths: list[Any], evidence_path: str | None) -> list[Any]:
    if not evidence_path:
        return paths
    if evidence_path not in paths:
        paths.append(evidence_path)
    return paths


def default_resource_lanes() -> dict[str, dict[str, Any]]:
    return {
        "xctest": {"mode": "serialized", "active_packet": None, "queue": []},
        "computer-use": {"mode": "serialized", "active_packet": None, "queue": []},
    }


def cmd_init(args: argparse.Namespace) -> int:
    repo = args.repo
    if manifest_path(repo).exists():
        raise PacketLoopError("packet-loop state already initialized")
    if (
        args.max_active_worktrees is not None
        and (isinstance(args.max_active_worktrees, bool) or args.max_active_worktrees < 1)
    ):
        raise PacketLoopError("max_active_worktrees must be a positive integer or null")
    state_dir(repo).mkdir(parents=True, exist_ok=True)
    packets_dir(repo).mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "repo": {
            "name": args.name,
            "default_branch": args.default_branch,
            "target_branch": args.target_branch,
        },
        "mode": args.mode,
        "dispatch_policy": {"mode": "no_fixed_limit", "max_active_worktrees": args.max_active_worktrees},
        "resource_lanes": default_resource_lanes(),
        "packet_order": [],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    write_json(manifest_path(repo), manifest)
    events_path(repo).touch(exist_ok=True)
    append_event(repo, "init", {"name": args.name, "target_branch": args.target_branch})
    render_dashboard(repo)
    return 0


def cmd_add_packet(args: argparse.Namespace) -> int:
    repo = args.repo
    packet_id = validate_packet_id(args.id)
    manifest = load_manifest(repo)
    if packet_id in manifest.get("packet_order", []):
        raise PacketLoopError(f"packet already exists: {packet_id}")
    if packet_path(repo, packet_id).exists():
        raise PacketLoopError(f"packet file already exists: {packet_id}")
    created_at = now_iso()
    packet = {
        "schema_version": SCHEMA_VERSION,
        "id": packet_id,
        "title": args.title,
        "goal": args.goal,
        "status": "candidate",
        "risk": args.risk,
        "parallel_safe": args.parallel_safe,
        "status_reason": "candidate packet created",
        "allowed_scope": packet_list(args.allowed_scope),
        "expected_touched_areas": packet_list(args.expected_area),
        "avoid_scope": packet_list(args.avoid_scope),
        "out_of_scope": packet_list(args.out_of_scope),
        "dependencies": packet_list(args.dependency),
        "reserved_areas": packet_list(args.reserved_area),
        "resource_lanes": packet_list(args.resource_lane),
        "blocked_by": packet_list(args.blocked_by),
        "overlap_notes": packet_list(args.overlap_note),
        "parent_plan_path": optional_text(args.parent_plan_path),
        "child_plan_path": optional_text(args.child_plan_path),
        "source_plan_refs": packet_list(args.source_plan_ref),
        "plan_format_status": args.plan_format_status,
        "human_review_required": bool(args.human_review_required),
        "needs_reslice_reason": None,
        "last_validation": None,
        "worker_report": None,
        "review_report": None,
        "validation": {"commands": args.validation_command},
        "evidence_paths": [],
        "blockers": [],
        "suggested_branch": args.suggested_branch,
        "notes": args.notes,
        "lease": None,
        "branch": None,
        "worktree": None,
        "pr": default_pr(),
        "created_at": created_at,
        "updated_at": created_at,
    }
    errors = validate_packet(packet)
    if errors:
        raise PacketLoopError("; ".join(errors))
    write_packet(repo, packet)
    manifest.setdefault("packet_order", []).append(packet_id)
    write_manifest(repo, manifest)
    append_event(repo, "add-packet", {"packet": packet_id})
    render_dashboard(repo)
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    repo = args.repo
    packet = load_packet(repo, args.packet)
    current_status = packet["status"]
    target_status = args.status
    if target_status in HUMAN_GATED_STATUSES and not args.human_approved:
        raise PacketLoopError(f"human-gated transition requires --human-approved: {current_status} -> {target_status}")
    if target_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
        raise PacketLoopError(f"invalid transition: {current_status} -> {target_status}")
    packet["status"] = target_status
    packet["status_reason"] = args.reason
    evidence_paths = packet.get("evidence_paths", [])
    if not isinstance(evidence_paths, list):
        evidence_paths = []
    packet["evidence_paths"] = add_unique_path(evidence_paths, args.evidence_path)
    if target_status == "ready":
        packet["lease"] = None
        packet["branch"] = None
        packet["worktree"] = None
    write_packet(repo, packet)
    append_event(
        repo,
        "transition",
        {
            "packet": args.packet,
            "from": current_status,
            "to": target_status,
            "actor": args.actor,
            "reason": args.reason,
            "evidence_path": args.evidence_path,
        },
    )
    render_dashboard(repo)
    return 0


def cmd_lease(args: argparse.Namespace) -> int:
    repo = args.repo
    errors = validate_repo(repo)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    manifest = load_manifest(repo)
    active_count = sum(1 for packet in load_packets(repo, manifest) if isinstance(packet.get("lease"), dict))
    dispatch_policy = manifest.get("dispatch_policy", {})
    active_limit = dispatch_policy.get("max_active_worktrees") if isinstance(dispatch_policy, dict) else None
    if active_limit is not None and active_count >= active_limit:
        raise PacketLoopError(f"active packet limit reached: {active_count}/{active_limit}")
    packet = load_packet(repo, args.packet)
    if packet["status"] != "ready":
        raise PacketLoopError(f"lease requires ready packet, got {packet['status']}")
    acquired_at = datetime.now(timezone.utc)
    expires_at = acquired_at + timedelta(hours=args.ttl_hours)
    packet["status"] = "reserved"
    packet["lease"] = {
        "owner_thread": args.owner_thread,
        "acquired_at": acquired_at.isoformat(timespec="seconds"),
        "expires_at": expires_at.isoformat(timespec="seconds"),
        "ttl_hours": args.ttl_hours,
    }
    packet["branch"] = args.branch
    packet["worktree"] = args.worktree
    write_packet(repo, packet)
    append_event(
        repo,
        "lease",
        {"packet": args.packet, "owner_thread": args.owner_thread, "branch": args.branch, "worktree": args.worktree},
    )
    render_dashboard(repo)
    return 0


def packet_has_pr(packet: dict[str, Any]) -> bool:
    pr = packet.get("pr")
    if isinstance(pr, dict):
        return any(value is not None for value in pr.values())
    return bool(pr) or bool(packet.get("pr_url"))


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate_repo(args.repo)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("valid")
    return 0


def cmd_maintain(args: argparse.Namespace) -> int:
    if not args.expire_stale_leases:
        raise PacketLoopError("maintain requires at least one maintenance action")
    repo = args.repo
    errors = validate_repo(repo)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    manifest = load_manifest(repo)
    now = datetime.now(timezone.utc)
    expired = []
    for packet in load_packets(repo, manifest):
        if packet.get("status") not in {"reserved", "in-progress"}:
            continue
        lease = packet.get("lease")
        if not isinstance(lease, dict):
            continue
        try:
            expires_at = parse_time(lease["expires_at"])
        except (KeyError, ValueError):
            continue
        if expires_at <= now and not packet_has_pr(packet):
            packet["status"] = "ready"
            packet["lease"] = None
            packet["branch"] = None
            packet["worktree"] = None
            write_packet(repo, packet)
            expired.append(packet["id"])
    if expired:
        append_event(repo, "expire-stale-leases", {"packets": expired})
    render_dashboard(repo)
    print(f"expired {len(expired)} stale lease(s)")
    return 0


class PacketLoopError(Exception):
    pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage experimental Codex PR packet loop state.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Target repository root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Initialize packet loop state.")
    init.add_argument("--name", required=True)
    init.add_argument("--default-branch", default="main")
    init.add_argument("--target-branch", default="main")
    init.add_argument("--mode", choices=sorted(MODES), default="planning")
    init.add_argument("--max-active-worktrees", type=int)
    init.set_defaults(func=cmd_init)

    add_packet = subparsers.add_parser("add-packet", help="Add a candidate packet.")
    add_packet.add_argument("--id", required=True)
    add_packet.add_argument("--title", required=True)
    add_packet.add_argument("--goal", required=True)
    add_packet.add_argument("--allowed-scope", action="append", required=True)
    add_packet.add_argument("--expected-area", action="append", required=True)
    add_packet.add_argument("--validation-command", action="append", required=True)
    add_packet.add_argument("--risk", choices=sorted(RISKS), default="medium")
    add_packet.add_argument("--parallel-safe", choices=sorted(PARALLEL_SAFE), default="maybe")
    add_packet.add_argument("--dependency", action="append")
    add_packet.add_argument("--avoid-scope", action="append")
    add_packet.add_argument("--out-of-scope", action="append")
    add_packet.add_argument("--reserved-area", action="append")
    add_packet.add_argument("--resource-lane", action="append")
    add_packet.add_argument("--blocked-by", action="append")
    add_packet.add_argument("--overlap-note", action="append")
    add_packet.add_argument("--parent-plan-path")
    add_packet.add_argument("--child-plan-path")
    add_packet.add_argument("--source-plan-ref", action="append")
    add_packet.add_argument("--plan-format-status", choices=("pending", "valid", "invalid"), default="pending")
    add_packet.add_argument("--human-review-required", action="store_true")
    add_packet.add_argument("--suggested-branch")
    add_packet.add_argument("--notes")
    add_packet.set_defaults(func=cmd_add_packet)

    transition = subparsers.add_parser("transition", help="Move a packet to a new status.")
    transition.add_argument("--packet", required=True)
    transition.add_argument("--status", choices=sorted(STATUSES), required=True)
    transition.add_argument("--human-approved", action="store_true")
    transition.add_argument("--actor", default="agent")
    transition.add_argument("--reason", default="state transition requested")
    transition.add_argument("--evidence-path")
    transition.set_defaults(func=cmd_transition)

    lease = subparsers.add_parser("lease", help="Reserve a ready packet for worker execution.")
    lease.add_argument("--packet", required=True)
    lease.add_argument("--owner-thread", required=True)
    lease.add_argument("--branch", required=True)
    lease.add_argument("--worktree", required=True)
    lease.add_argument("--ttl-hours", type=int, default=24)
    lease.set_defaults(func=cmd_lease)

    validate = subparsers.add_parser("validate", help="Validate packet loop state.")
    validate.set_defaults(func=cmd_validate)

    maintain = subparsers.add_parser("maintain", help="Run packet loop state maintenance.")
    maintain.add_argument("--expire-stale-leases", action="store_true")
    maintain.set_defaults(func=cmd_maintain)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.repo = args.repo.resolve()
    try:
        return args.func(args)
    except PacketLoopError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
