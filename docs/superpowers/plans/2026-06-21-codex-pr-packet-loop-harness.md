# Codex PR Packet Loop Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first experimental Codex PR packet loop harness as a validated skill suite with durable repo state, packet leases, scoped worker execution, packet PR review, and merge recommendation flows.

**Architecture:** Keep the entire MVP under `experimental/codex-pr-packet-loop/` until it proves out. Use JSON files under `.codex/packet-loop/` as the source of truth in target repos, generated Markdown under `docs/codex/packet-loop.md` for humans, and a Python standard-library CLI for deterministic validation, transitions, leases, and dashboard generation. Dedicated experimental stage skills stay small and route agents through the shared core contract instead of duplicating state rules.

**Tech Stack:** Codex skills in Markdown, `agents/openai.yaml` metadata, Python 3 standard library, `unittest`, Bash validation scripts, JSON schema-style validation without third-party dependencies.

---

## Scope

This plan builds the manual MVP that can run a 3-packet trial safely:

- initialize packet-loop state in a target repo
- slice a plan into packet records
- reserve and lease one packet per worker
- run one worker in one worktree for one packet
- review packet PRs against scope and evidence
- recommend merge order without merging
- maintain state, expire deterministic leases, and regenerate the dashboard

This plan does not create scheduled multi-repo automation. It creates `codex-packet-maintain` so a local automation can invoke the maintenance workflow once the manual loop is proven.

All implementation files for this MVP must live under `experimental/codex-pr-packet-loop/`. Do not add root `skills/` entries, plugin mirror entries, root package metadata, or root user-facing docs in this plan. Promotion into shipped skills is a separate follow-up after the experimental loop passes a real trial.

## File Structure

Create these experimental skill directories:

- `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/`: shared state contract, deterministic CLI, tests, and validation instructions.
- `experimental/codex-pr-packet-loop/skills/codex-packet-init/`: initialize packet-loop state in a repo.
- `experimental/codex-pr-packet-loop/skills/codex-packet-slice/`: convert an approved plan into packet JSON records.
- `experimental/codex-pr-packet-loop/skills/codex-packet-dispatch/`: reserve a ready packet and produce a worker prompt.
- `experimental/codex-pr-packet-loop/skills/codex-packet-worker/`: execute exactly one leased packet in a worktree.
- `experimental/codex-pr-packet-loop/skills/codex-packet-review/`: review or refresh a packet PR against packet scope and evidence.
- `experimental/codex-pr-packet-loop/skills/codex-packet-integrate/`: sequence merge candidates and stop before human-gated actions.
- `experimental/codex-pr-packet-loop/skills/codex-packet-maintain/`: validate state, expire deterministic stale leases, and regenerate dashboard output.

Add shared validation:

- `experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py`: validates experimental skill frontmatter, `agents/openai.yaml`, and packet-loop CLI tests.

Add experimental documentation only:

- `experimental/codex-pr-packet-loop/README.md`
- `experimental/codex-pr-packet-loop/docs/manual.md`

Target repo packet-loop state created by the skills:

- `.codex/packet-loop/manifest.json`
- `.codex/packet-loop/packets/<packet-id>.json`
- `.codex/packet-loop/events.jsonl`
- `.codex/packet-loop/evidence/<packet-id>/`
- `docs/codex/packet-loop.md`

## State Contract

Use JSON as the structured state format because Python can validate it without new dependencies.

Manifest shape:

```json
{
  "schema_version": "0.1.0",
  "repo": {
    "name": "repo-name",
    "default_branch": "main",
    "target_branch": "main"
  },
  "mode": "planning",
  "active_packet_limit": 3,
  "packet_order": ["P001"],
  "updated_at": "2026-06-21T12:00:00Z"
}
```

Packet shape:

```json
{
  "schema_version": "0.1.0",
  "id": "P001",
  "title": "short packet title",
  "status": "candidate",
  "goal": "One sentence outcome.",
  "allowed_scope": ["experimental/codex-pr-packet-loop/skills/example/SKILL.md"],
  "expected_touched_areas": ["experimental/codex-pr-packet-loop/skills/example"],
  "avoid_scope": ["skills/example", "plugins/codex-skills/skills/example"],
  "dependencies": [],
  "risk": "low",
  "parallel_safe": "yes",
  "validation": {
    "commands": ["python3 -m unittest experimental/codex-pr-packet-loop/skills/example/tests/test_example.py"]
  },
  "lease": null,
  "branch": null,
  "worktree": null,
  "pr": null,
  "evidence_paths": [],
  "blockers": [],
  "updated_at": "2026-06-21T12:00:00Z"
}
```

Allowed packet statuses:

```text
candidate
ready
reserved
in-progress
pr-open
reviewing
needs-fix
blocked
needs-reslice
merge-eligible
merged
rejected
```

Allowed automatic transitions:

```text
candidate -> ready
ready -> reserved
reserved -> in-progress
in-progress -> pr-open
pr-open -> reviewing
reviewing -> needs-fix
reviewing -> blocked
reviewing -> needs-reslice
reviewing -> merge-eligible
needs-fix -> in-progress
blocked -> ready
needs-reslice -> candidate
```

Human-gated transitions:

```text
merge-eligible -> merged
any live status -> rejected
any status requiring branch deletion, PR closing, force-push, default-branch write, or security-sensitive change
```

---

### Task 1: Add Core CLI Tests First

**Files:**
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/fixtures/plan.md`

- [ ] **Step 1: Create the plan fixture**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/fixtures/plan.md`:

```markdown
# Example Plan

## Phase 1

Create a small experimental skill with metadata and validation.

## Phase 2

Document the experimental workflow after the experimental skill validates.
```

- [ ] **Step 2: Write failing core CLI tests**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py`:

```python
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "packet_loop.py"


class PacketLoopCLITests(unittest.TestCase):
    def run_cli(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), "--repo", str(repo), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_init_creates_manifest_events_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = self.run_cli(repo, "init", "--name", "demo", "--target-branch", "main")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((repo / ".codex/packet-loop/manifest.json").is_file())
            self.assertTrue((repo / ".codex/packet-loop/events.jsonl").is_file())
            self.assertTrue((repo / "docs/codex/packet-loop.md").is_file())

            manifest = json.loads((repo / ".codex/packet-loop/manifest.json").read_text())
            self.assertEqual(manifest["schema_version"], "0.1.0")
            self.assertEqual(manifest["repo"]["name"], "demo")
            self.assertEqual(manifest["packet_order"], [])

    def test_add_packet_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            result = self.run_cli(
                repo,
                "add-packet",
                "--id",
                "P001",
                "--title",
                "Add core skill",
                "--goal",
                "Create the core packet-loop skill.",
                "--allowed-scope",
                "experimental/codex-pr-packet-loop/skills/codex-packet-loop-core",
                "--expected-area",
                "experimental/codex-pr-packet-loop/skills/codex-packet-loop-core",
                "--validation-command",
                "python3 -m unittest experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["status"], "candidate")
            self.assertEqual(packet["risk"], "medium")
            self.assertEqual(packet["parallel_safe"], "maybe")

            validate = self.run_cli(repo, "validate")
            self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_transition_rejects_invalid_status_move(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(
                self.run_cli(
                    repo,
                    "add-packet",
                    "--id",
                    "P001",
                    "--title",
                    "Packet",
                    "--goal",
                    "Do one packet.",
                    "--allowed-scope",
                    "skills/demo",
                    "--expected-area",
                    "skills/demo",
                    "--validation-command",
                    "python3 -m unittest",
                ).returncode,
                0,
            )
            result = self.run_cli(repo, "transition", "--packet", "P001", "--status", "merged")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("human-gated", result.stderr)

    def test_lease_ready_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(
                self.run_cli(
                    repo,
                    "add-packet",
                    "--id",
                    "P001",
                    "--title",
                    "Packet",
                    "--goal",
                    "Do one packet.",
                    "--allowed-scope",
                    "skills/demo",
                    "--expected-area",
                    "skills/demo",
                    "--validation-command",
                    "python3 -m unittest",
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "ready").returncode, 0)
            result = self.run_cli(
                repo,
                "lease",
                "--packet",
                "P001",
                "--owner-thread",
                "thread-123",
                "--branch",
                "codex/p001-demo",
                "--worktree",
                "/tmp/demo-worktree",
                "--ttl-hours",
                "24",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["status"], "reserved")
            self.assertEqual(packet["lease"]["owner_thread"], "thread-123")
            self.assertEqual(packet["branch"], "codex/p001-demo")
            self.assertEqual(packet["worktree"], "/tmp/demo-worktree")

    def test_maintenance_expires_reserved_packet_without_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(
                self.run_cli(
                    repo,
                    "add-packet",
                    "--id",
                    "P001",
                    "--title",
                    "Packet",
                    "--goal",
                    "Do one packet.",
                    "--allowed-scope",
                    "skills/demo",
                    "--expected-area",
                    "skills/demo",
                    "--validation-command",
                    "python3 -m unittest",
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "ready").returncode, 0)
            self.assertEqual(
                self.run_cli(
                    repo,
                    "lease",
                    "--packet",
                    "P001",
                    "--owner-thread",
                    "thread-123",
                    "--branch",
                    "codex/p001-demo",
                    "--worktree",
                    "/tmp/demo-worktree",
                    "--ttl-hours",
                    "0",
                ).returncode,
                0,
            )
            result = self.run_cli(repo, "maintain", "--expire-stale-leases")
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["status"], "ready")
            self.assertIsNone(packet["lease"])
```

- [ ] **Step 3: Run the failing test**

Run:

```bash
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
```

Expected result:

```text
can't open file
```

or:

```text
No such file or directory: .../scripts/packet_loop.py
```

---

### Task 2: Implement Core Packet Loop CLI

**Files:**
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py`
- Modify: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py`

- [ ] **Step 1: Create the CLI script**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py` with these public commands:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
LIVE_STATUSES = {"reserved", "in-progress", "pr-open", "reviewing", "needs-fix", "merge-eligible"}
STATUSES = {
    "candidate",
    "ready",
    "reserved",
    "in-progress",
    "pr-open",
    "reviewing",
    "needs-fix",
    "blocked",
    "needs-reslice",
    "merge-eligible",
    "merged",
    "rejected",
}
AUTOMATIC_TRANSITIONS = {
    ("candidate", "ready"),
    ("ready", "reserved"),
    ("reserved", "in-progress"),
    ("in-progress", "pr-open"),
    ("pr-open", "reviewing"),
    ("reviewing", "needs-fix"),
    ("reviewing", "blocked"),
    ("reviewing", "needs-reslice"),
    ("reviewing", "merge-eligible"),
    ("needs-fix", "in-progress"),
    ("blocked", "ready"),
    ("needs-reslice", "candidate"),
}
HUMAN_GATED_TRANSITIONS = {("merge-eligible", "merged")}


class PacketLoopError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def loop_root(repo: Path) -> Path:
    return repo / ".codex" / "packet-loop"


def packets_root(repo: Path) -> Path:
    return loop_root(repo) / "packets"


def events_path(repo: Path) -> Path:
    return loop_root(repo) / "events.jsonl"


def manifest_path(repo: Path) -> Path:
    return loop_root(repo) / "manifest.json"


def dashboard_path(repo: Path) -> Path:
    return repo / "docs" / "codex" / "packet-loop.md"


def packet_path(repo: Path, packet_id: str) -> Path:
    return packets_root(repo) / f"{packet_id}.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def append_event(repo: Path, event: str, payload: dict[str, Any]) -> None:
    events_path(repo).parent.mkdir(parents=True, exist_ok=True)
    record = {"at": utc_now(), "event": event, "payload": payload}
    with events_path(repo).open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def load_manifest(repo: Path) -> dict[str, Any]:
    path = manifest_path(repo)
    if not path.is_file():
        raise PacketLoopError("packet loop is not initialized")
    return read_json(path)


def load_packet(repo: Path, packet_id: str) -> dict[str, Any]:
    path = packet_path(repo, packet_id)
    if not path.is_file():
        raise PacketLoopError(f"packet not found: {packet_id}")
    return read_json(path)


def save_packet(repo: Path, packet: dict[str, Any]) -> None:
    packet["updated_at"] = utc_now()
    write_json(packet_path(repo, packet["id"]), packet)


def cmd_init(repo: Path, args: argparse.Namespace) -> None:
    root = loop_root(repo)
    packets_root(repo).mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "repo": {
            "name": args.name,
            "default_branch": args.default_branch,
            "target_branch": args.target_branch,
        },
        "mode": "planning",
        "active_packet_limit": args.active_packet_limit,
        "packet_order": [],
        "updated_at": utc_now(),
    }
    write_json(manifest_path(repo), manifest)
    events_path(repo).write_text("")
    append_event(repo, "initialized", {"repo": args.name})
    render_dashboard(repo)


def cmd_add_packet(repo: Path, args: argparse.Namespace) -> None:
    manifest = load_manifest(repo)
    if packet_path(repo, args.id).exists():
        raise PacketLoopError(f"packet already exists: {args.id}")
    packet = {
        "schema_version": SCHEMA_VERSION,
        "id": args.id,
        "title": args.title,
        "status": "candidate",
        "goal": args.goal,
        "allowed_scope": args.allowed_scope,
        "expected_touched_areas": args.expected_area,
        "avoid_scope": args.avoid_scope,
        "dependencies": args.dependency,
        "risk": args.risk,
        "parallel_safe": args.parallel_safe,
        "validation": {"commands": args.validation_command},
        "lease": None,
        "branch": None,
        "worktree": None,
        "pr": None,
        "evidence_paths": [],
        "blockers": [],
        "updated_at": utc_now(),
    }
    save_packet(repo, packet)
    manifest["packet_order"].append(args.id)
    manifest["updated_at"] = utc_now()
    write_json(manifest_path(repo), manifest)
    append_event(repo, "packet_added", {"packet": args.id})
    render_dashboard(repo)


def cmd_transition(repo: Path, args: argparse.Namespace) -> None:
    packet = load_packet(repo, args.packet)
    current = packet["status"]
    target = args.status
    if target not in STATUSES:
        raise PacketLoopError(f"invalid status: {target}")
    if (current, target) in HUMAN_GATED_TRANSITIONS and not args.human_approved:
        raise PacketLoopError(f"human-gated transition requires --human-approved: {current} -> {target}")
    if (current, target) not in AUTOMATIC_TRANSITIONS and (current, target) not in HUMAN_GATED_TRANSITIONS:
        raise PacketLoopError(f"invalid transition: {current} -> {target}")
    packet["status"] = target
    save_packet(repo, packet)
    append_event(repo, "packet_transitioned", {"packet": args.packet, "from": current, "to": target})
    render_dashboard(repo)


def cmd_lease(repo: Path, args: argparse.Namespace) -> None:
    packet = load_packet(repo, args.packet)
    if packet["status"] != "ready":
        raise PacketLoopError(f"only ready packets can be leased: {args.packet}")
    if packet["lease"] is not None:
        raise PacketLoopError(f"packet already has a lease: {args.packet}")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires_at = now + timedelta(hours=args.ttl_hours)
    packet["status"] = "reserved"
    packet["lease"] = {
        "owner_thread": args.owner_thread,
        "branch": args.branch,
        "worktree": args.worktree,
        "leased_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
        "allowed_scope": packet["allowed_scope"],
    }
    packet["branch"] = args.branch
    packet["worktree"] = args.worktree
    save_packet(repo, packet)
    append_event(repo, "packet_leased", {"packet": args.packet, "owner_thread": args.owner_thread})
    render_dashboard(repo)


def cmd_validate(repo: Path, _args: argparse.Namespace) -> None:
    manifest = load_manifest(repo)
    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("manifest schema_version mismatch")
    seen: set[str] = set()
    for packet_id in manifest.get("packet_order", []):
        if packet_id in seen:
            errors.append(f"duplicate packet in manifest: {packet_id}")
        seen.add(packet_id)
        try:
            packet = load_packet(repo, packet_id)
            validate_packet(packet, errors)
        except PacketLoopError as exc:
            errors.append(str(exc))
    live_leases: dict[str, str] = {}
    for packet_id in seen:
        packet = load_packet(repo, packet_id)
        lease = packet.get("lease")
        if lease:
            owner = lease.get("owner_thread", "")
            if owner in live_leases:
                errors.append(f"duplicate live lease owner {owner}: {live_leases[owner]} and {packet_id}")
            live_leases[owner] = packet_id
    if errors:
        raise PacketLoopError("; ".join(errors))


def validate_packet(packet: dict[str, Any], errors: list[str]) -> None:
    required = [
        "schema_version",
        "id",
        "title",
        "status",
        "goal",
        "allowed_scope",
        "expected_touched_areas",
        "dependencies",
        "risk",
        "parallel_safe",
        "validation",
        "updated_at",
    ]
    for key in required:
        if key not in packet:
            errors.append(f"{packet.get('id', '<unknown>')} missing {key}")
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{packet.get('id')} schema_version mismatch")
    if packet.get("status") not in STATUSES:
        errors.append(f"{packet.get('id')} invalid status {packet.get('status')}")
    if packet.get("risk") not in {"low", "medium", "high"}:
        errors.append(f"{packet.get('id')} invalid risk {packet.get('risk')}")
    if packet.get("parallel_safe") not in {"yes", "no", "maybe"}:
        errors.append(f"{packet.get('id')} invalid parallel_safe {packet.get('parallel_safe')}")


def cmd_maintain(repo: Path, args: argparse.Namespace) -> None:
    load_manifest(repo)
    expired: list[str] = []
    now = datetime.now(timezone.utc)
    if args.expire_stale_leases:
        for path in sorted(packets_root(repo).glob("*.json")):
            packet = read_json(path)
            lease = packet.get("lease")
            if not lease:
                continue
            if packet["status"] not in {"reserved", "in-progress"}:
                continue
            if parse_time(lease["expires_at"]) <= now and packet.get("pr") is None:
                packet["status"] = "ready"
                packet["lease"] = None
                packet["branch"] = None
                packet["worktree"] = None
                save_packet(repo, packet)
                expired.append(packet["id"])
    if expired:
        append_event(repo, "leases_expired", {"packets": expired})
    render_dashboard(repo)
    cmd_validate(repo, args)


def render_dashboard(repo: Path) -> None:
    manifest = load_manifest(repo)
    lines = [
        "# Codex Packet Loop",
        "",
        f"Schema: `{manifest['schema_version']}`",
        f"Mode: `{manifest['mode']}`",
        f"Target branch: `{manifest['repo']['target_branch']}`",
        "",
        "| Packet | Status | Risk | Parallel | Branch | PR | Goal |",
        "|---|---|---|---|---|---|---|",
    ]
    for packet_id in manifest.get("packet_order", []):
        packet = load_packet(repo, packet_id)
        lines.append(
            "| {id} | {status} | {risk} | {parallel_safe} | {branch} | {pr} | {goal} |".format(
                id=packet["id"],
                status=packet["status"],
                risk=packet["risk"],
                parallel_safe=packet["parallel_safe"],
                branch=packet.get("branch") or "",
                pr=packet.get("pr") or "",
                goal=packet["goal"].replace("|", "/"),
            )
        )
    dashboard_path(repo).parent.mkdir(parents=True, exist_ok=True)
    dashboard_path(repo).write_text("\n".join(lines) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init")
    init.add_argument("--name", required=True)
    init.add_argument("--default-branch", default="main")
    init.add_argument("--target-branch", default="main")
    init.add_argument("--active-packet-limit", type=int, default=3)

    add_packet = subparsers.add_parser("add-packet")
    add_packet.add_argument("--id", required=True)
    add_packet.add_argument("--title", required=True)
    add_packet.add_argument("--goal", required=True)
    add_packet.add_argument("--allowed-scope", action="append", required=True)
    add_packet.add_argument("--expected-area", action="append", required=True)
    add_packet.add_argument("--avoid-scope", action="append", default=[])
    add_packet.add_argument("--dependency", action="append", default=[])
    add_packet.add_argument("--risk", choices=["low", "medium", "high"], default="medium")
    add_packet.add_argument("--parallel-safe", choices=["yes", "no", "maybe"], default="maybe")
    add_packet.add_argument("--validation-command", action="append", required=True)

    transition = subparsers.add_parser("transition")
    transition.add_argument("--packet", required=True)
    transition.add_argument("--status", required=True)
    transition.add_argument("--human-approved", action="store_true")

    lease = subparsers.add_parser("lease")
    lease.add_argument("--packet", required=True)
    lease.add_argument("--owner-thread", required=True)
    lease.add_argument("--branch", required=True)
    lease.add_argument("--worktree", required=True)
    lease.add_argument("--ttl-hours", type=int, default=24)

    subparsers.add_parser("validate")

    maintain = subparsers.add_parser("maintain")
    maintain.add_argument("--expire-stale-leases", action="store_true")
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo = args.repo.resolve()
    try:
        if args.command == "init":
            cmd_init(repo, args)
        elif args.command == "add-packet":
            cmd_add_packet(repo, args)
        elif args.command == "transition":
            cmd_transition(repo, args)
        elif args.command == "lease":
            cmd_lease(repo, args)
        elif args.command == "validate":
            cmd_validate(repo, args)
        elif args.command == "maintain":
            cmd_maintain(repo, args)
        return 0
    except PacketLoopError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

- [ ] **Step 2: Make the script executable**

Run:

```bash
chmod +x experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py
```

- [ ] **Step 3: Run the core tests**

Run:

```bash
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
```

Expected result:

```text
Ran 5 tests

OK
```

- [ ] **Step 4: Commit**

```bash
git add experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py \
  experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/fixtures/plan.md \
  experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py
git commit -m "test(packet-loop): add core state CLI coverage"
```

---

### Task 3: Add Core Skill Contract And Metadata

**Files:**
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/agents/openai.yaml`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/state-contract.md`

- [ ] **Step 1: Create the state contract reference**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/state-contract.md` with:

````markdown
# Packet Loop State Contract

## Source Of Truth

Structured state lives under `.codex/packet-loop/`.

- `.codex/packet-loop/manifest.json` is the repo loop manifest.
- `.codex/packet-loop/packets/<packet-id>.json` is one packet record.
- `.codex/packet-loop/events.jsonl` records state changes and deterministic repairs.
- `.codex/packet-loop/evidence/<packet-id>/` stores packet-local evidence.
- `docs/codex/packet-loop.md` is generated human-readable dashboard output.

Agents must treat the JSON state as authoritative. Markdown dashboard text is derived output.

## Worker Write Boundary

Workers may update only:

- their leased packet record
- `.codex/packet-loop/evidence/<packet-id>/`
- implementation files inside the packet allowed scope

Workers must not edit the manifest, other packet records, or generated dashboard unless a stage skill explicitly assigns that work.

## Human Gates

Stop for human approval before:

- merge
- branch deletion
- PR closing
- force-push
- default-branch write
- security-sensitive change

## CLI

Use `scripts/packet_loop.py` for deterministic state changes:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> validate
python3 <core-skill>/scripts/packet_loop.py --repo <repo> maintain --expire-stale-leases
```
````

- [ ] **Step 2: Create core SKILL.md**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/SKILL.md` with:

````markdown
---
name: codex-packet-loop-core
description: Shared state contract and deterministic CLI for Codex PR packet loop skills. Use when validating packet-loop JSON state, lifecycle transitions, leases, generated dashboards, or packet-loop helper behavior.
---

# Codex Packet Loop Core

Use this skill as the shared contract for the Codex PR packet loop suite.

## Required Context

Read `references/state-contract.md` before changing packet-loop state.

## Deterministic CLI

Use `scripts/packet_loop.py` for state operations instead of editing JSON by hand when the operation is supported.

Common commands:

```bash
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> init --name <repo-name>
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> validate
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> maintain --expire-stale-leases
```

## Rules

- Treat JSON under `.codex/packet-loop/` as authoritative.
- Treat `docs/codex/packet-loop.md` as generated output.
- Log deterministic repairs through the CLI so `events.jsonl` stays audit-ready.
- Refuse human-gated transitions unless the human explicitly approved them.
````

- [ ] **Step 3: Create core metadata**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/agents/openai.yaml`:

```yaml
interface:
  display_name: "Packet Loop Core"
  short_description: "Validate packet-loop state and leases"
  default_prompt: "Use $codex-packet-loop-core to validate the packet-loop state for this repo."
```

- [ ] **Step 4: Validate core skill**

Run:

```bash
python3 /Users/coryparry/.codex/skills/.system/skill-creator/scripts/quick_validate.py experimental/codex-pr-packet-loop/skills/codex-packet-loop-core
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
```

Expected result:

```text
Skill is valid
Ran 5 tests

OK
```

- [ ] **Step 5: Commit**

```bash
git add experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/SKILL.md \
  experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/agents/openai.yaml \
  experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/state-contract.md
git commit -m "feat(packet-loop): add core state contract skill"
```

---

### Task 4: Add Stage Skills

**Files:**
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-init/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-init/agents/openai.yaml`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-slice/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-slice/agents/openai.yaml`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-dispatch/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-dispatch/agents/openai.yaml`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-worker/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-worker/agents/openai.yaml`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-review/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-review/agents/openai.yaml`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-integrate/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-integrate/agents/openai.yaml`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-maintain/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-maintain/agents/openai.yaml`

- [ ] **Step 1: Create `codex-packet-init`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-init/SKILL.md`:

````markdown
---
name: codex-packet-init
description: Initialize Codex PR packet loop state in a repository. Use when a repo opts into packet-loop orchestration or needs `.codex/packet-loop/` manifest, packet directory, event log, and generated dashboard setup.
---

# Codex Packet Init

Use this skill to opt a repo into the PR packet loop.

## Workflow

1. Read repo instructions and confirm the target repo root.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Refuse to overwrite existing `.codex/packet-loop/manifest.json` unless the user explicitly approves reinitialization.
4. Run:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> init --name <repo-name> --target-branch <branch>
```

5. Run:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> validate
```

6. Report the created files and next valid skill: `$codex-packet-slice`.
````

Create `experimental/codex-pr-packet-loop/skills/codex-packet-init/agents/openai.yaml`:

```yaml
interface:
  display_name: "Packet Init"
  short_description: "Initialize packet-loop repo state"
  default_prompt: "Use $codex-packet-init to initialize packet-loop state in this repo."
```

- [ ] **Step 2: Create `codex-packet-slice`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-slice/SKILL.md`:

```markdown
---
name: codex-packet-slice
description: Convert an approved plan into small Codex PR packet records. Use when slicing broad implementation plans into packet JSON with dependencies, allowed scope, validation commands, risk, and overlap notes.
---

# Codex Packet Slice

Use this skill after packet-loop state is initialized and a plan has been approved for implementation.

## Workflow

1. Read the plan and repo instructions.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run packet-loop validation before editing state.
4. Propose packet boundaries before writing records when the source plan is broad or ambiguous.
5. Create one packet per reviewable PR unit with:
   - one goal
   - allowed scope
   - expected touched areas
   - avoid scope
   - dependencies
   - risk
   - parallel safety
   - validation commands
6. Add packets with `packet_loop.py add-packet`.
7. Transition packets from `candidate` to `ready` only when dependencies and validation are clear.
8. Regenerate dashboard through the CLI and report next valid skill: `$codex-packet-dispatch`.

## Packet Quality Rules

- Prefer packets that can be reviewed without reading the whole plan.
- Mark generated files, lockfiles, central state, public API, security, and broad UI flows as higher risk.
- Keep dependent packets serial unless the dependency is already merged.
- Do not hide ambiguous owner decisions inside packet text.
```

Create `experimental/codex-pr-packet-loop/skills/codex-packet-slice/agents/openai.yaml`:

```yaml
interface:
  display_name: "Packet Slice"
  short_description: "Slice plans into PR packets"
  default_prompt: "Use $codex-packet-slice to convert this approved plan into packet-loop records."
```

- [ ] **Step 3: Create `codex-packet-dispatch`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-dispatch/SKILL.md`:

````markdown
---
name: codex-packet-dispatch
description: Reserve a ready Codex PR packet, create or prepare a worktree worker assignment, and record the packet lease. Use when dispatching one ready packet to one Codex worker thread.
---

# Codex Packet Dispatch

Use this skill to assign one ready packet to one worker.

## Workflow

1. Read repo instructions, manifest, ready packets, and active leases.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run packet-loop validation.
4. Choose one ready packet whose dependencies are satisfied and whose expected areas do not collide with live leases.
5. Create a branch name in this form:

```text
codex/<packet-id-lower>-<short-title>
```

6. Create or request a fresh worktree thread for the worker.
7. Record the lease:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> lease --packet <packet-id> --owner-thread <thread-id> --branch <branch> --worktree <path> --ttl-hours 24
```

8. Produce a worker prompt that explicitly invokes `$codex-packet-worker` and includes the packet id, branch, worktree, allowed scope, validation command, and stop conditions.
9. Report next valid skill: `$codex-packet-worker` in the worker thread.

## Refusal Conditions

- Refuse dispatch when the packet is not `ready`.
- Refuse dispatch when dependencies are unmerged.
- Refuse dispatch when expected areas collide with a live lease.
- Refuse dispatch when no fresh worktree/thread route is available.
````

Create `experimental/codex-pr-packet-loop/skills/codex-packet-dispatch/agents/openai.yaml`:

```yaml
interface:
  display_name: "Packet Dispatch"
  short_description: "Lease packets to worker threads"
  default_prompt: "Use $codex-packet-dispatch to reserve the next safe packet and prepare a worker prompt."
```

- [ ] **Step 4: Create `codex-packet-worker`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-worker/SKILL.md`:

```markdown
---
name: codex-packet-worker
description: Execute exactly one leased Codex PR packet in one worktree. Use when a worker thread receives a packet assignment with allowed scope, validation route, branch, and lease.
---

# Codex Packet Worker

Use this skill inside the assigned packet worktree.

## Workflow

1. Read repo instructions.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Validate the packet exists, is leased to this worker, and is `reserved`.
4. Transition the packet to `in-progress`.
5. Inspect only files needed for the packet.
6. Implement the smallest change that satisfies the packet goal.
7. Run the packet validation commands.
8. Fix only failures caused by the packet.
9. Stop after two failed fix attempts with the same root cause.
10. Record evidence under `.codex/packet-loop/evidence/<packet-id>/`.
11. Prepare or open one PR for the packet.
12. Transition to `pr-open` only after evidence and validation are recorded.
13. Report next valid skill: `$codex-packet-review`.

## Stop Conditions

Stop and mark the packet `blocked` or `needs-reslice` when:

- required changes leave `allowed_scope`
- validation requires unrelated fixes
- a reserved area is needed
- dependencies are missing
- the packet goal is ambiguous after code inspection
- security-sensitive decisions are required

Do not implement adjacent packets.
```

Create `experimental/codex-pr-packet-loop/skills/codex-packet-worker/agents/openai.yaml`:

```yaml
interface:
  display_name: "Packet Worker"
  short_description: "Execute one leased packet"
  default_prompt: "Use $codex-packet-worker to execute the assigned packet in this worktree."
```

- [ ] **Step 5: Create `codex-packet-review`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-review/SKILL.md`:

```markdown
---
name: codex-packet-review
description: Review or refresh a Codex PR packet against its packet record, allowed scope, validation evidence, PR diff, and overlap risk. Use when a packet PR is open, stale, conflicted, or ready for merge eligibility review.
---

# Codex Packet Review

Use this skill after a packet PR exists or a packet branch needs scoped refresh.

## Workflow

1. Read repo instructions, packet record, PR metadata, changed files, and validation evidence.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run packet-loop validation.
4. Compare actual changed files with `allowed_scope` and `expected_touched_areas`.
5. Check dependencies, live leases, generated-file overlap, interface overlap, behavior overlap, test overlap, documentation overlap, and validation freshness.
6. If the branch is stale or conflicted, produce a refresh packet scoped to the original packet only.
7. Move the packet to exactly one status:
   - `needs-fix`
   - `blocked`
   - `needs-reslice`
   - `merge-eligible`
8. Report evidence checked and next valid skill: `$codex-packet-worker` for fixes or `$codex-packet-integrate` for merge candidates.

## Review Verdict Rules

- Use `merge-eligible` only when the PR matches packet scope and validation is current.
- Use `needs-reslice` when useful work exists but the packet boundary was wrong.
- Use `blocked` when owner input or human-gated action is required.
- Treat worker summaries as claims until verified against files, diffs, checks, PR state, and evidence.
```

Create `experimental/codex-pr-packet-loop/skills/codex-packet-review/agents/openai.yaml`:

```yaml
interface:
  display_name: "Packet Review"
  short_description: "Review packet PR scope and evidence"
  default_prompt: "Use $codex-packet-review to review this packet PR against its packet record."
```

- [ ] **Step 6: Create `codex-packet-integrate`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-integrate/SKILL.md`:

```markdown
---
name: codex-packet-integrate
description: Sequence merge-eligible Codex packet PRs, detect overlap, recommend merge order, and update packet-loop state after approved merges. Use when one or more packet PRs are merge-eligible.
---

# Codex Packet Integrate

Use this skill to prepare safe merge sequencing. Do not merge unless the human explicitly approves the merge action.

## Workflow

1. Read repo instructions, manifest, packet records, open PRs, changed files, and validation evidence.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run packet-loop validation.
4. Build a merge matrix with file, area, interface, behavior, test, generated-file, dependency, and documentation overlap.
5. Recommend a serial merge order.
6. Identify packets that need refresh before merge.
7. Stop before merge, branch deletion, PR closing, force-push, default-branch write, or security-sensitive action.
8. After an approved merge has happened, transition only that packet to `merged` with `--human-approved`, regenerate dashboard, and re-check remaining packets.

## Default Merge Policy

Parallel implementation is allowed. Parallel merging is not allowed in this MVP.
```

Create `experimental/codex-pr-packet-loop/skills/codex-packet-integrate/agents/openai.yaml`:

```yaml
interface:
  display_name: "Packet Integrate"
  short_description: "Sequence merge-ready packet PRs"
  default_prompt: "Use $codex-packet-integrate to recommend a safe merge order for eligible packet PRs."
```

- [ ] **Step 7: Create `codex-packet-maintain`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-maintain/SKILL.md`:

````markdown
---
name: codex-packet-maintain
description: Maintain Codex packet-loop state by validating JSON records, expiring deterministic stale leases, regenerating dashboards, and reporting controller-safe next actions. Use for scheduled or manual packet-loop maintenance.
---

# Codex Packet Maintain

Use this skill for manual maintenance or as the repo-local workflow a local automation invokes.

## Workflow

1. Read repo instructions and packet-loop state.
2. Load `$codex-packet-loop-core` and read its state contract.
3. Run:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> maintain --expire-stale-leases
```

4. Report:
   - expired leases
   - invalid records
   - ready packets
   - blocked packets
   - merge-eligible packets
   - next safe skill to run

## Repair Boundary

Deterministic repair may expire a stale lease for a packet without a PR. Destructive, external, or security-sensitive actions require human approval.
````

Create `experimental/codex-pr-packet-loop/skills/codex-packet-maintain/agents/openai.yaml`:

```yaml
interface:
  display_name: "Packet Maintain"
  short_description: "Repair and report packet-loop state"
  default_prompt: "Use $codex-packet-maintain to validate packet-loop state and report next safe actions."
```

- [ ] **Step 8: Validate stage skill frontmatter**

Run:

```bash
for skill in codex-packet-init codex-packet-slice codex-packet-dispatch codex-packet-worker codex-packet-review codex-packet-integrate codex-packet-maintain; do
  python3 /Users/coryparry/.codex/skills/.system/skill-creator/scripts/quick_validate.py "experimental/codex-pr-packet-loop/skills/$skill"
done
```

Expected result: each skill prints `Skill is valid`.

- [ ] **Step 9: Commit**

```bash
git add experimental/codex-pr-packet-loop/skills/codex-packet-init \
  experimental/codex-pr-packet-loop/skills/codex-packet-slice \
  experimental/codex-pr-packet-loop/skills/codex-packet-dispatch \
  experimental/codex-pr-packet-loop/skills/codex-packet-worker \
  experimental/codex-pr-packet-loop/skills/codex-packet-review \
  experimental/codex-pr-packet-loop/skills/codex-packet-integrate \
  experimental/codex-pr-packet-loop/skills/codex-packet-maintain
git commit -m "feat(packet-loop): add stage workflow skills"
```

---

### Task 5: Add Experimental Skill Validation

**Files:**
- Create: `experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py`

- [ ] **Step 1: Create validation script**

Create `experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED_AGENT_KEYS = {"display_name", "short_description", "default_prompt"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "---":
        fail(f"{path} missing frontmatter")
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return values
        if ":" not in line:
            fail(f"{path} invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    fail(f"{path} unterminated frontmatter")


def parse_simple_openai_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    in_interface = False
    for raw in path.read_text().splitlines():
        line = raw.rstrip()
        if line == "interface:":
            in_interface = True
            continue
        if in_interface and line.startswith("  ") and ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"')
    return values


def validate_skill(skill_dir: Path) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail(f"{skill_dir} missing SKILL.md")
    frontmatter = parse_frontmatter(skill_file)
    expected_name = skill_dir.name
    if frontmatter.get("name") != expected_name:
        fail(f"{skill_file} name must be {expected_name}")
    if not frontmatter.get("description"):
        fail(f"{skill_file} missing description")
    metadata = skill_dir / "agents" / "openai.yaml"
    if not metadata.is_file():
        fail(f"{skill_dir} missing agents/openai.yaml")
    interface = parse_simple_openai_yaml(metadata)
    missing = REQUIRED_AGENT_KEYS - interface.keys()
    if missing:
        fail(f"{metadata} missing interface keys: {', '.join(sorted(missing))}")
    if f"${expected_name}" not in interface["default_prompt"]:
        fail(f"{metadata} default_prompt must mention ${expected_name}")


def run_core_tests() -> None:
    test_paths = [
        SKILLS / "codex-packet-loop-core" / "tests" / "test_packet_loop.py",
        SKILLS / "codex-packet-loop-core" / "tests" / "test_packet_loop_trial.py",
    ]
    for test_path in test_paths:
        if not test_path.exists():
            continue
        result = subprocess.run([sys.executable, str(test_path)], cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


def main() -> int:
    if not (ROOT / "README.md").is_file():
        fail("experimental README.md is missing")
    for skill_dir in sorted(SKILLS.iterdir()):
        if skill_dir.is_dir():
            validate_skill(skill_dir)
    run_core_tests()
    print("Experimental packet-loop validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Make validation script executable**

Run:

```bash
chmod +x experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```

- [ ] **Step 3: Run experimental validation**

Run:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```

Expected result:

```text
Ran 5 tests

OK
Experimental packet-loop validation passed
```

- [ ] **Step 4: Commit**

```bash
git add experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
git commit -m "test(packet-loop): add experimental validation script"
```

---

### Task 6: Update Experimental README

**Files:**
- Modify: `experimental/codex-pr-packet-loop/README.md`

- [ ] **Step 1: Add experimental-only boundary**

Append this section to `experimental/codex-pr-packet-loop/README.md`:

````markdown
## Experimental Skill Suite

The first packet-loop harness lives entirely under this `experimental/codex-pr-packet-loop/` directory.

Do not mirror these skills into `skills/`, `plugins/codex-skills/skills/`, or package metadata until a separate promotion plan is approved.

### Skills

- `codex-packet-loop-core` validates packet-loop JSON state, leases, transitions, and dashboard output.
- `codex-packet-init` initializes packet-loop state in a target repo.
- `codex-packet-slice` converts approved plans into scoped PR packet records.
- `codex-packet-dispatch` reserves ready packets and prepares worker prompts.
- `codex-packet-worker` executes one leased packet in one worktree.
- `codex-packet-review` reviews packet PRs against scope, validation, and overlap risk.
- `codex-packet-integrate` recommends merge order and stops before human-gated actions.
- `codex-packet-maintain` validates, repairs deterministic lease drift, and regenerates packet dashboards.

### Validation

Run the experimental validation command from the repo root:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```
````

- [ ] **Step 2: Run experimental validation**

Run:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```

Expected result:

```text
Experimental packet-loop validation passed
```

- [ ] **Step 3: Commit**

```bash
git add experimental/codex-pr-packet-loop/README.md
git commit -m "docs(packet-loop): document experimental skill suite"
```

---

### Task 7: Add Usage Documentation And Trial Script

**Files:**
- Create: `experimental/codex-pr-packet-loop/docs/manual.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py`

- [ ] **Step 1: Write user documentation**

Create `experimental/codex-pr-packet-loop/docs/manual.md`:

````markdown
# Codex PR Packet Loop

The Codex PR packet loop turns a large approved plan into small PR packets that can be assigned to isolated Codex worktree workers.

## First Run

1. Initialize state:

```text
Use $codex-packet-init to initialize packet-loop state in this repo.
```

2. Slice the approved plan:

```text
Use $codex-packet-slice to convert this approved plan into packet records.
```

3. Dispatch one packet:

```text
Use $codex-packet-dispatch to lease the next safe ready packet.
```

4. Run the worker in the assigned worktree:

```text
Use $codex-packet-worker to execute packet P001 only.
```

5. Review the packet PR:

```text
Use $codex-packet-review to review the packet PR against its packet record.
```

6. Prepare merge sequencing:

```text
Use $codex-packet-integrate to recommend a safe merge order.
```

7. Maintain state:

```text
Use $codex-packet-maintain to validate packet-loop state and report next safe actions.
```

## Human Gates

The loop stops for human approval before merge, branch deletion, PR closing, force-push, default-branch writes, or security-sensitive changes.

## State Files

Structured state lives under `.codex/packet-loop/`. The generated dashboard lives at `docs/codex/packet-loop.md`.
````

- [ ] **Step 2: Add a 3-packet trial test**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py`:

```python
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "packet_loop.py"


class PacketLoopTrialTests(unittest.TestCase):
    def run_cli(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI), "--repo", str(repo), *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_three_packet_trial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "trial").returncode, 0)
            packets = [
                ("P001", "Core", "experimental/codex-pr-packet-loop/skills/codex-packet-loop-core"),
                ("P002", "Slice", "experimental/codex-pr-packet-loop/skills/codex-packet-slice"),
                ("P003", "Review", "experimental/codex-pr-packet-loop/skills/codex-packet-review"),
            ]
            for packet_id, title, area in packets:
                self.assertEqual(
                    self.run_cli(
                        repo,
                        "add-packet",
                        "--id",
                        packet_id,
                        "--title",
                        title,
                        "--goal",
                        f"Build {title}.",
                        "--allowed-scope",
                        area,
                        "--expected-area",
                        area,
                        "--validation-command",
                        "python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py",
                    ).returncode,
                    0,
                )
                self.assertEqual(self.run_cli(repo, "transition", "--packet", packet_id, "--status", "ready").returncode, 0)
            self.assertEqual(
                self.run_cli(
                    repo,
                    "lease",
                    "--packet",
                    "P001",
                    "--owner-thread",
                    "thread-p001",
                    "--branch",
                    "codex/p001-core",
                    "--worktree",
                    "/tmp/p001-core",
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cli(repo, "validate").returncode, 0)
            manifest = json.loads((repo / ".codex/packet-loop/manifest.json").read_text())
            self.assertEqual(manifest["packet_order"], ["P001", "P002", "P003"])
            dashboard = (repo / "docs/codex/packet-loop.md").read_text()
            self.assertIn("| P001 | reserved |", dashboard)
            self.assertIn("| P002 | ready |", dashboard)
            self.assertIn("| P003 | ready |", dashboard)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run documentation and trial checks**

Run:

```bash
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
git diff --check
```

Expected result:

```text
Ran 1 test

OK
Experimental packet-loop validation passed
```

- [ ] **Step 4: Commit**

```bash
git add experimental/codex-pr-packet-loop/docs/manual.md \
  experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py
git commit -m "docs(packet-loop): document manual packet loop trial"
```

---

### Task 8: Final Validation And Closeout

**Files:**
- Modify only files already touched by earlier tasks if validation finds a scoped issue.

- [ ] **Step 1: Run full repo validation**

Run:

```bash
bash scripts/test_install.sh
bash -n scripts/install.sh
bash -n skills/codex-adversarial-gate/scripts/install.sh
python3 -m json.tool skills.sh.json >/dev/null
python3 -m json.tool plugins/codex-skills/.codex-plugin/plugin.json >/dev/null
python3 skills/codex-adversarial-gate/scripts/test_archive_adversarial_review.py
python3 skills/git-clean-merged-branch/tests/test_clean_merged_branch.py
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
git diff --check
```

Expected result:

```text
Install tests passed
Experimental packet-loop validation passed
```

and every Python test exits with status 0.

- [ ] **Step 2: Run autoreview if executable behavior changed**

Run `$autoreview` because this plan adds executable Python behavior and validation scripts.

Classify findings against this packet-loop scope:

- Fix in-scope correctness, safety, packaging, and validation findings.
- Reject findings that expand into scheduled automation, cloud orchestration, GitHub Actions runners, automatic merges, or unrelated skill rewrites.
- Rerun the relevant checks after every accepted fix.

- [ ] **Step 3: Confirm changed files are scoped**

Run:

```bash
git status --short
git diff --stat
```

Expected changed areas:

```text
experimental/codex-pr-packet-loop/skills/codex-packet-*
experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
experimental/codex-pr-packet-loop/docs/manual.md
experimental/codex-pr-packet-loop/README.md
```

- [ ] **Step 4: Final commit**

If autoreview or final validation required changes, commit them:

```bash
git add <scoped-fixed-files>
git commit -m "fix(packet-loop): address validation review findings"
```

If no files changed after the previous commits, do not create an empty commit.

- [ ] **Step 5: Final report**

Report:

- created packet-loop skills
- state files and dashboard generated by the loop
- validation commands and outcomes
- autoreview outcome
- skipped checks with reasons
- remaining scope not included in the MVP: scheduled multi-repo automation, automatic merges, cloud task orchestration, and hosted callbacks

---

## Self-Review Checklist

- Every new skill has `SKILL.md` and `agents/openai.yaml`.
- Every MVP file remains under `experimental/codex-pr-packet-loop/`.
- Root `skills/`, plugin mirror, package metadata, and root docs remain unchanged by this plan.
- Core state changes are made through `packet_loop.py` where supported.
- Workers can update only their packet record and packet evidence.
- Human-gated actions stop before merge, branch deletion, PR close, force-push, default-branch write, and security-sensitive changes.
- Tests cover init, packet creation, invalid transition refusal, lease creation, deterministic lease expiry, dashboard generation, and a 3-packet trial.
- The plan intentionally proves the manual loop before scheduled multi-repo automation.
