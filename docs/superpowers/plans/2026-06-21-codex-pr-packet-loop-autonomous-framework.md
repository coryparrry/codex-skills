# Codex PR Packet Loop Autonomous Framework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the experimental Codex PR packet loop into a controller-led autonomous workflow framework with script-backed state, explicit stage routing, and behavioral validation.

**Architecture:** Keep all shipped behavior inside `experimental/codex-pr-packet-loop/`. The `codex-packet-loop` skill becomes the controller/router, `codex-packet-loop-core` owns deterministic state helpers and shared protocol references, and stage skills become concise operators that load the shared protocol before acting. Python CLI tests cover state mechanics; validation fixtures cover routing and behavioral skill expectations.

**Tech Stack:** Markdown skills and references, Python 3 standard library, `argparse`, `json`, `unittest`, shell validation commands already used by the repository.

## Global Constraints

- Keep framework changes under `experimental/codex-pr-packet-loop/`; this pass must not promote skills into `skills/`, `plugins/codex-skills/skills/`, or package metadata.
- Add no new third-party dependencies.
- Treat `.codex/packet-loop/*.json` as authoritative state; treat `docs/codex/packet-loop.md` as generated output.
- Use `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py` for deterministic state changes when a supported command exists.
- Do not impose a default fixed active-worktree cap. Dispatch as many dependency-ready packets as the controller can actively monitor, constrained by review capacity, overlap risk, and serialized resource lanes.
- Serialize scarce validation or proof lanes such as XCTest, UI automation, and Computer Use while allowing implementation, static checks, and low-risk docs work to continue in parallel.
- Human approval is required before merge, force-push, branch deletion, PR closing, default-branch writes, destructive Git operations, discarding useful work, or security-sensitive tradeoffs.
- Worker summaries are untrusted claims until review verifies packet JSON, actual diff, PR state, validation evidence, and scope.
- Workers prepare one PR by default; they may open or update a PR only when direct user instructions or repo-local packet-loop configuration authorizes that external action.
- Do not touch the existing untracked `docs/brainstorms/` directory unless the user separately scopes it.

---

## File Structure

- Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop/SKILL.md`: controller/router skill and autonomous loop contract.
- Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop/agents/openai.yaml`: controller metadata.
- Modify `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/SKILL.md`: point to the new shared references and CLI commands.
- Modify `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/state-contract.md`: turn it into a compatibility index that points to the new references.
- Create core references:
  - `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/workflow-protocol.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/state-machine.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/autonomy-policy.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/handoff-contracts.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/evidence-contract.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/overlap-policy.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/recovery-playbook.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/behavioral-evals.md`
- Modify `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py`: extend packet schema, transition logging, evidence indexing, PR metadata, and state summary commands.
- Modify `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py`: add focused CLI tests for schema, transition metadata, evidence, PR metadata, status summary, and overlap refusal.
- Modify `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py`: expand the three-packet trial to exercise controller-ready status output and evidence paths.
- Create `experimental/codex-pr-packet-loop/evals/fixtures/*.md`: prompt-level behavioral fixtures for later trace grading.
- Modify stage skills:
  - `experimental/codex-pr-packet-loop/skills/codex-packet-init/SKILL.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-slice/SKILL.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-dispatch/SKILL.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-worker/SKILL.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-review/SKILL.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-integrate/SKILL.md`
  - `experimental/codex-pr-packet-loop/skills/codex-packet-maintain/SKILL.md`
- Modify `experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py`: enforce controller skill, references, routing hooks, metadata, behavioral fixtures, and test suite execution.
- Modify `experimental/codex-pr-packet-loop/README.md` and `experimental/codex-pr-packet-loop/docs/manual.md`: document controller-first operation and validation.

## Task 1: Strengthen Core State Schema and Transition Events

**Files:**
- Modify: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py`
- Modify: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py`

**Interfaces:**
- Consumes: existing CLI commands `init`, `add-packet`, `transition`, `lease`, `validate`, `maintain`.
- Produces: packet records with `status_reason`, `reserved_areas`, `resource_lanes`, `blocked_by`, `overlap_notes`, `human_review_required`, `needs_reslice_reason`, `last_validation`, `worker_report`, `review_report`, and structured `pr` fields.
- Produces: manifest records with `dispatch_policy.mode` set to `no_fixed_limit` and `resource_lanes` definitions for serialized tool lanes.
- Produces: transition events with `actor`, `reason`, and optional `evidence_path`.

- [ ] **Step 1: Add failing tests for the richer packet schema**

Append these tests to `PacketLoopCLITests` in `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py`:

```python
    def test_init_sets_unbounded_dispatch_policy_and_serial_resource_lanes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = self.run_cli(repo, "init", "--name", "demo")
            self.assertEqual(result.returncode, 0, result.stderr)

            manifest = json.loads((repo / ".codex/packet-loop/manifest.json").read_text())
            self.assertEqual(manifest["dispatch_policy"], {"mode": "no_fixed_limit", "max_active_worktrees": None})
            self.assertEqual(manifest["resource_lanes"]["xctest"]["mode"], "serialized")
            self.assertEqual(manifest["resource_lanes"]["xctest"]["active_packet"], None)
            self.assertEqual(manifest["resource_lanes"]["xctest"]["queue"], [])
            self.assertEqual(manifest["resource_lanes"]["computer-use"]["mode"], "serialized")
            self.assertEqual(manifest["resource_lanes"]["computer-use"]["active_packet"], None)
            self.assertEqual(manifest["resource_lanes"]["computer-use"]["queue"], [])

    def test_add_packet_sets_autonomous_contract_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            result = self.run_cli(
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
                "--reserved-area",
                "skills/demo",
                "--resource-lane",
                "xctest",
                "--overlap-note",
                "No live overlap.",
                "--human-review-required",
                "--validation-command",
                "python3 -m unittest",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["status_reason"], "candidate packet created")
            self.assertEqual(packet["reserved_areas"], ["skills/demo"])
            self.assertEqual(packet["resource_lanes"], ["xctest"])
            self.assertEqual(packet["blocked_by"], [])
            self.assertEqual(packet["overlap_notes"], ["No live overlap."])
            self.assertTrue(packet["human_review_required"])
            self.assertIsNone(packet["needs_reslice_reason"])
            self.assertIsNone(packet["last_validation"])
            self.assertIsNone(packet["worker_report"])
            self.assertIsNone(packet["review_report"])
            self.assertEqual(
                packet["pr"],
                {"url": None, "number": None, "state": None, "head": None, "base": None},
            )

    def test_transition_records_actor_reason_and_evidence_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)

            result = self.run_cli(
                repo,
                "transition",
                "--packet",
                "P001",
                "--status",
                "ready",
                "--actor",
                "controller",
                "--reason",
                "dependencies are satisfied",
                "--evidence-path",
                ".codex/packet-loop/evidence/P001/slice-report.md",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["status"], "ready")
            self.assertEqual(packet["status_reason"], "dependencies are satisfied")
            self.assertIn(".codex/packet-loop/evidence/P001/slice-report.md", packet["evidence_paths"])

            events = [
                json.loads(line)
                for line in (repo / ".codex/packet-loop/events.jsonl").read_text().splitlines()
                if line.strip()
            ]
            transition_event = events[-1]
            self.assertEqual(transition_event["event"], "transition")
            self.assertEqual(transition_event["details"]["actor"], "controller")
            self.assertEqual(transition_event["details"]["reason"], "dependencies are satisfied")
            self.assertEqual(
                transition_event["details"]["evidence_path"],
                ".codex/packet-loop/evidence/P001/slice-report.md",
            )
```

- [ ] **Step 2: Run the targeted tests and confirm they fail for missing CLI/schema support**

Run:

```bash
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
```

Expected: failure mentions unknown `--reserved-area`, unknown `--overlap-note`, unknown `--human-review-required`, unknown `--actor`, or missing packet fields.

- [ ] **Step 3: Extend the CLI schema with minimal helpers**

In `packet_loop.py`, add this helper near `packet_list`:

```python
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
```

Update `cmd_init` so the manifest uses explicit scheduler policy instead of a default worker cap:

```python
        "dispatch_policy": {"mode": "no_fixed_limit", "max_active_worktrees": args.max_active_worktrees},
        "resource_lanes": default_resource_lanes(),
```

Remove the default `active_packet_limit` manifest field. Keep `max_active_worktrees` nullable; it is an explicit owner override, not a hidden default cap.

Then update `cmd_add_packet` to set these fields:

```python
        "status_reason": "candidate packet created",
        "reserved_areas": packet_list(args.reserved_area),
        "resource_lanes": packet_list(args.resource_lane),
        "blocked_by": packet_list(args.blocked_by),
        "overlap_notes": packet_list(args.overlap_note),
        "human_review_required": bool(args.human_review_required),
        "needs_reslice_reason": None,
        "last_validation": None,
        "worker_report": None,
        "review_report": None,
        "pr": default_pr(),
```

Replace the existing `"pr": None` entry in the same packet literal with the structured `pr` object above.

- [ ] **Step 4: Validate the new manifest and packet fields**

In `validate_manifest`, replace the required positive `active_packet_limit` validation with:

```python
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
```

In `validate_packet`, include the list fields:

```python
        "reserved_areas",
        "resource_lanes",
        "blocked_by",
        "overlap_notes",
```

After the list-field loop, add these checks:

```python
    if not isinstance(packet.get("status_reason"), str) or not packet.get("status_reason"):
        errors.append(f"packet {packet.get('id', '<unknown>')} status_reason must be a non-empty string")
    if not isinstance(packet.get("human_review_required"), bool):
        errors.append(f"packet {packet.get('id', '<unknown>')} human_review_required must be a boolean")
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
```

- [ ] **Step 5: Add parser flags for init policy, packet creation, and transition metadata**

In `build_parser`, add this `init` flag near the existing init parser setup:

```python
    init.add_argument("--max-active-worktrees", type=int)
```

Then add these `add-packet` flags near the existing add-packet parser setup:

```python
    add_packet.add_argument("--reserved-area", action="append")
    add_packet.add_argument("--resource-lane", action="append")
    add_packet.add_argument("--blocked-by", action="append")
    add_packet.add_argument("--overlap-note", action="append")
    add_packet.add_argument("--human-review-required", action="store_true")
```

Add these `transition` flags:

```python
    transition.add_argument("--actor", default="agent")
    transition.add_argument("--reason", default="state transition requested")
    transition.add_argument("--evidence-path")
```

- [ ] **Step 6: Record transition metadata in packet JSON and events**

In `cmd_transition`, after `packet["status"] = target_status`, add:

```python
    packet["status_reason"] = args.reason
    evidence_paths = packet.get("evidence_paths", [])
    if not isinstance(evidence_paths, list):
        evidence_paths = []
    packet["evidence_paths"] = add_unique_path(evidence_paths, args.evidence_path)
```

Replace the current transition event details with:

```python
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
```

- [ ] **Step 7: Run the targeted tests and fix only schema or parser failures**

Run:

```bash
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
```

Expected: all tests in `test_packet_loop.py` pass.

- [ ] **Step 8: Commit Task 1**

Run:

```bash
git add experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
git commit -m "feat(packet-loop): strengthen packet state contract"
```

## Task 2: Add Evidence, PR Metadata, Status Summary, and Overlap Guards

**Files:**
- Modify: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py`
- Modify: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py`
- Modify: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py`

**Interfaces:**
- Consumes: packet schema from Task 1.
- Produces CLI commands:
  - `record-evidence --packet <id> --kind <worker-report|review-report|validation|diffstat|scope-check|merge-matrix|integration-report|maintenance-report> --path <relative-path> [--summary <text>] [--actor <name>]`
  - `set-pr --packet <id> [--url <url>] [--number <int>] [--state <state>] [--head <branch>] [--base <branch>]`
  - `status --format json`
- Produces overlap refusal for `lease` using `reserved_areas` and live packet leases.

- [ ] **Step 1: Add failing tests for evidence, PR metadata, status summary, and reserved-area collisions**

Append these tests to `PacketLoopCLITests`:

```python
    def test_record_evidence_updates_report_fields_and_event_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)

            result = self.run_cli(
                repo,
                "record-evidence",
                "--packet",
                "P001",
                "--kind",
                "worker-report",
                "--path",
                ".codex/packet-loop/evidence/P001/worker-report.md",
                "--summary",
                "worker finished scoped change",
                "--actor",
                "worker",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["worker_report"], ".codex/packet-loop/evidence/P001/worker-report.md")
            self.assertIn(".codex/packet-loop/evidence/P001/worker-report.md", packet["evidence_paths"])
            events = [json.loads(line) for line in (repo / ".codex/packet-loop/events.jsonl").read_text().splitlines()]
            self.assertEqual(events[-1]["event"], "record-evidence")
            self.assertEqual(events[-1]["details"]["summary"], "worker finished scoped change")

    def test_set_pr_records_structured_pr_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)

            result = self.run_cli(
                repo,
                "set-pr",
                "--packet",
                "P001",
                "--url",
                "https://github.com/example/repo/pull/12",
                "--number",
                "12",
                "--state",
                "open",
                "--head",
                "codex/p001-demo",
                "--base",
                "main",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(
                packet["pr"],
                {
                    "url": "https://github.com/example/repo/pull/12",
                    "number": 12,
                    "state": "open",
                    "head": "codex/p001-demo",
                    "base": "main",
                },
            )

    def test_status_json_groups_packets_for_controller(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo, "P001").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo, "P002").returncode, 0)
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "ready").returncode, 0)
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P002", "--status", "ready").returncode, 0)
            self.assertEqual(
                self.run_cli(
                    repo,
                    "lease",
                    "--packet",
                    "P001",
                    "--owner-thread",
                    "thread-001",
                    "--branch",
                    "codex/p001-demo",
                    "--worktree",
                    "/tmp/p001",
                ).returncode,
                0,
            )

            result = self.run_cli(repo, "status", "--format", "json")

            self.assertEqual(result.returncode, 0, result.stderr)
            status = json.loads(result.stdout)
            self.assertEqual(status["dispatch_policy"]["mode"], "no_fixed_limit")
            self.assertEqual(status["active_lease_count"], 1)
            self.assertEqual(status["resource_lanes"]["xctest"]["mode"], "serialized")
            self.assertEqual(status["resource_lanes"]["computer-use"]["mode"], "serialized")
            self.assertEqual(status["groups"]["reserved"], ["P001"])
            self.assertEqual(status["groups"]["ready"], ["P002"])
            self.assertEqual(status["next_actions"][0]["skill"], "codex-packet-dispatch")

    def test_lease_rejects_reserved_area_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            for packet_id in ("P001", "P002"):
                self.assertEqual(
                    self.run_cli(
                        repo,
                        "add-packet",
                        "--id",
                        packet_id,
                        "--title",
                        "Packet",
                        "--goal",
                        "Do one packet.",
                        "--allowed-scope",
                        "skills/demo",
                        "--expected-area",
                        "skills/demo",
                        "--reserved-area",
                        "skills/shared",
                        "--validation-command",
                        "python3 -m unittest",
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
                    "thread-001",
                    "--branch",
                    "codex/p001-demo",
                    "--worktree",
                    "/tmp/p001",
                ).returncode,
                0,
            )

            result = self.run_cli(
                repo,
                "lease",
                "--packet",
                "P002",
                "--owner-thread",
                "thread-002",
                "--branch",
                "codex/p002-demo",
                "--worktree",
                "/tmp/p002",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reserved area collision", result.stderr)
```

- [ ] **Step 2: Run the targeted tests and confirm they fail for missing commands and collision logic**

Run:

```bash
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
```

Expected: failure mentions missing subcommands `record-evidence`, `set-pr`, `status`, or missing reserved-area collision behavior.

- [ ] **Step 3: Implement evidence recording**

In `packet_loop.py`, add constants near `MODES`:

```python
EVIDENCE_KINDS = {
    "worker-report": "worker_report",
    "review-report": "review_report",
    "validation": "last_validation",
    "diffstat": None,
    "scope-check": None,
    "merge-matrix": None,
    "integration-report": None,
    "maintenance-report": None,
}
```

Add this command function before `cmd_validate`:

```python
def cmd_record_evidence(args: argparse.Namespace) -> int:
    repo = args.repo
    packet = load_packet(repo, args.packet)
    evidence_paths = packet.get("evidence_paths", [])
    if not isinstance(evidence_paths, list):
        evidence_paths = []
    packet["evidence_paths"] = add_unique_path(evidence_paths, args.path)
    field = EVIDENCE_KINDS[args.kind]
    if field is not None:
        packet[field] = args.path
    write_packet(repo, packet)
    append_event(
        repo,
        "record-evidence",
        {
            "packet": args.packet,
            "kind": args.kind,
            "path": args.path,
            "summary": args.summary,
            "actor": args.actor,
        },
    )
    render_dashboard(repo)
    return 0
```

- [ ] **Step 4: Implement PR metadata updates**

Add this function after `cmd_record_evidence`:

```python
def cmd_set_pr(args: argparse.Namespace) -> int:
    repo = args.repo
    packet = load_packet(repo, args.packet)
    pr = packet.get("pr")
    if not isinstance(pr, dict):
        pr = default_pr()
    for key in ("url", "state", "head", "base"):
        value = getattr(args, key)
        if value is not None:
            pr[key] = value
    if args.number is not None:
        pr["number"] = args.number
    packet["pr"] = pr
    write_packet(repo, packet)
    append_event(repo, "set-pr", {"packet": args.packet, "pr": pr})
    render_dashboard(repo)
    return 0
```

- [ ] **Step 5: Implement status summary output**

Add this helper and command function:

```python
def build_status_summary(repo: Path) -> dict[str, Any]:
    errors = validate_repo(repo)
    manifest = load_manifest(repo) if not errors else {}
    packets = load_packets(repo, manifest) if not errors else []
    groups: dict[str, list[str]] = {status: [] for status in sorted(STATUSES)}
    for packet in packets:
        groups[str(packet["status"])].append(str(packet["id"]))
    active_lease_count = sum(1 for packet in packets if isinstance(packet.get("lease"), dict))
    next_actions: list[dict[str, str]] = []
    if errors:
        next_actions.append({"skill": "codex-packet-maintain", "reason": "state validation failed"})
    elif groups["pr-open"] or groups["reviewing"]:
        next_actions.append({"skill": "codex-packet-review", "reason": "packet PRs need verification"})
    elif groups["ready"]:
        next_actions.append({"skill": "codex-packet-dispatch", "reason": "dependency-ready packets are available"})
    elif groups["merge-eligible"]:
        next_actions.append({"skill": "codex-packet-integrate", "reason": "merge-eligible packets require human-gated sequencing"})
    elif groups["blocked"] or groups["needs-reslice"]:
        next_actions.append({"skill": "codex-packet-slice", "reason": "blocked or mis-sliced packets need replanning"})
    else:
        next_actions.append({"skill": "codex-packet-maintain", "reason": "no executable packet action found"})
    return {
        "valid": not errors,
        "errors": errors,
        "dispatch_policy": manifest.get("dispatch_policy", {"mode": "no_fixed_limit"}),
        "resource_lanes": manifest.get("resource_lanes", {}),
        "active_lease_count": active_lease_count,
        "groups": groups,
        "next_actions": next_actions,
    }


def cmd_status(args: argparse.Namespace) -> int:
    summary = build_status_summary(args.repo)
    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"valid: {summary['valid']}")
        print(f"active leases: {summary['active_lease_count']}")
        print(f"dispatch policy: {summary['dispatch_policy'].get('mode')}")
        for action in summary["next_actions"]:
            print(f"next: ${action['skill']} - {action['reason']}")
    return 0 if summary["valid"] else 1
```

- [ ] **Step 6: Reject live reserved-area collisions in `cmd_lease`**

Add this helper:

```python
def packet_reserved_areas(packet: dict[str, Any]) -> set[str]:
    values = packet.get("reserved_areas", [])
    if not isinstance(values, list):
        return set()
    return {str(value) for value in values if isinstance(value, str) and value}
```

In `cmd_lease`, after loading `packet`, add:

```python
    target_areas = packet_reserved_areas(packet)
    for live_packet in load_packets(repo, manifest):
        if live_packet.get("id") == packet.get("id"):
            continue
        if not isinstance(live_packet.get("lease"), dict):
            continue
        collision = sorted(target_areas & packet_reserved_areas(live_packet))
        if collision:
            raise PacketLoopError(
                "reserved area collision with {packet_id}: {areas}".format(
                    packet_id=live_packet.get("id"),
                    areas=", ".join(collision),
                )
            )
```

- [ ] **Step 7: Register the new parser subcommands**

In `build_parser`, add:

```python
    record_evidence = subparsers.add_parser("record-evidence", help="Record packet evidence path metadata.")
    record_evidence.add_argument("--packet", required=True)
    record_evidence.add_argument("--kind", choices=sorted(EVIDENCE_KINDS), required=True)
    record_evidence.add_argument("--path", required=True)
    record_evidence.add_argument("--summary")
    record_evidence.add_argument("--actor", default="agent")
    record_evidence.set_defaults(func=cmd_record_evidence)

    set_pr = subparsers.add_parser("set-pr", help="Record packet PR metadata.")
    set_pr.add_argument("--packet", required=True)
    set_pr.add_argument("--url")
    set_pr.add_argument("--number", type=int)
    set_pr.add_argument("--state")
    set_pr.add_argument("--head")
    set_pr.add_argument("--base")
    set_pr.set_defaults(func=cmd_set_pr)

    status = subparsers.add_parser("status", help="Summarize packet loop state for controllers.")
    status.add_argument("--format", choices=("text", "json"), default="text")
    status.set_defaults(func=cmd_status)
```

- [ ] **Step 8: Expand the trial test to assert controller status and evidence indexing**

In `test_three_packet_trial`, after the dashboard assertions, add:

```python
            self.assertEqual(
                self.run_cli(
                    repo,
                    "record-evidence",
                    "--packet",
                    "P001",
                    "--kind",
                    "worker-report",
                    "--path",
                    ".codex/packet-loop/evidence/P001/worker-report.md",
                ).returncode,
                0,
            )
            status_result = self.run_cli(repo, "status", "--format", "json")
            self.assertEqual(status_result.returncode, 0, status_result.stderr)
            status = json.loads(status_result.stdout)
            self.assertEqual(status["groups"]["reserved"], ["P001"])
            self.assertEqual(status["groups"]["ready"], ["P002", "P003"])
```

- [ ] **Step 9: Run core tests**

Run:

```bash
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py
```

Expected: both commands pass.

- [ ] **Step 10: Commit Task 2**

Run:

```bash
git add experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/scripts/packet_loop.py experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py
git commit -m "feat(packet-loop): add evidence and controller status helpers"
```

## Task 3: Build Shared Protocol References

**Files:**
- Modify: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/SKILL.md`
- Modify: `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/state-contract.md`
- Create: all reference files listed in the File Structure section.

**Interfaces:**
- Consumes: state model and CLI command names from Tasks 1 and 2.
- Produces: stable reference names that every stage skill can load: `workflow-protocol.md`, `state-machine.md`, `autonomy-policy.md`, `handoff-contracts.md`, `evidence-contract.md`, `overlap-policy.md`, `recovery-playbook.md`, and `behavioral-evals.md`.

- [ ] **Step 1: Create `workflow-protocol.md`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/workflow-protocol.md` with these sections and routing table:

```markdown
# Packet Loop Workflow Protocol

## Authority Order

1. Direct user instruction for the current turn.
2. Repo and nested `AGENTS.md` instructions.
3. Packet-loop JSON under `.codex/packet-loop/`.
4. Packet-loop evidence paths recorded in packet JSON.
5. Generated dashboard at `docs/codex/packet-loop.md`.

JSON state wins over generated Markdown when the two disagree.

## Stage Routing

| State or request | Next skill |
|---|---|
| No `.codex/packet-loop/manifest.json` exists | `$codex-packet-init` |
| Manifest exists but there are no packet records | `$codex-packet-slice` |
| Invalid packet-loop JSON or expired deterministic lease | `$codex-packet-maintain` |
| Dependency-ready packets fit monitoring and resource-lane capacity | `$codex-packet-dispatch` |
| Packet is leased to the current worker | `$codex-packet-worker` |
| Packet has PR state or status `pr-open` or `reviewing` | `$codex-packet-review` |
| Packet is `merge-eligible` | `$codex-packet-integrate` |
| Packet is `blocked` or `needs-reslice` | `$codex-packet-slice` or user decision |

## Controller Loop

The controller validates state, runs deterministic maintenance, reads status summary, chooses one safe next skill, and stops at human gates. It must supervise active worker lanes by checking thread status, worktree dirt, and diff shape before integration.
```

- [ ] **Step 2: Create `state-machine.md`**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references/state-machine.md`:

```markdown
# Packet Loop State Machine

## Statuses

`candidate`, `ready`, `reserved`, `in-progress`, `pr-open`, `reviewing`, `needs-fix`, `blocked`, `needs-reslice`, `merge-eligible`, `merged`, and `rejected`.

## Autonomous Transitions

| From | To |
|---|---|
| `candidate` | `ready`, `blocked`, `needs-reslice` |
| `ready` | `reserved` |
| `reserved` | `in-progress`, `ready` |
| `in-progress` | `pr-open`, `needs-fix`, `blocked`, `needs-reslice` |
| `pr-open` | `reviewing` |
| `reviewing` | `needs-fix`, `blocked`, `needs-reslice`, `merge-eligible` |
| `needs-fix` | `reserved`, `blocked` |
| `blocked` | `ready`, `needs-reslice` |
| `needs-reslice` | `candidate` |

## Human-Gated Transitions

`merge-eligible` to `merged` requires explicit human approval. Moving any live packet to `rejected` requires explicit human approval when useful work or an open PR would be discarded.

## Transition Event Requirements

Every transition records actor, prior status, new status, reason, timestamp, and evidence path when available. Use `packet_loop.py transition` rather than editing packet JSON directly.
```

- [ ] **Step 3: Create the remaining reference files with concrete rules**

Create the six remaining files with these top-level headings:

```markdown
# Packet Loop Autonomy Policy

## Safe Autonomous Actions

- Validate packet-loop state.
- Expire stale leases when the lease TTL has passed and no PR metadata exists.
- Regenerate generated dashboards through the CLI.
- Reserve ready packets when dependencies, monitoring capacity, serialized resource-lane constraints, and reserved-area checks pass.
- Record evidence paths and PR metadata through the CLI.
- Recommend merge order without performing the merge.

## Recommend-Only Actions

- Merge packet PRs.
- Close PRs.
- Delete branches or worktrees.
- Force-push packet branches.
- Change packet scope after useful work exists.

## Hard Stops

Stop for user input before destructive Git operations, default-branch writes, security-sensitive tradeoffs, external submissions not already authorized, or repeated failures with the same root cause.
```

```markdown
# Packet Loop Handoff Contracts

## Dispatch Handoff

Required fields: packet id, packet title, packet goal, branch, worktree, owner thread id, allowed scope, avoid scope, expected touched areas, reserved areas, validation commands, evidence directory, stop conditions, and next skill `$codex-packet-worker`.

## Worker Report

Required fields: packet id, summary of changed behavior, files touched, validation commands run, validation result, evidence paths, PR metadata, concerns, and requested next skill `$codex-packet-review`.

## Review Verdict

Required fields: packet id, PR URL or branch, checks performed, scope result, validation result, overlap result, verdict, exact reason, required fix or integration note, and next skill.

## Integration Recommendation

Required fields: candidate packets, PR metadata, stale status, conflict status, overlap categories, recommended serial order, and human-gated action requested.

## Maintenance Report

Required fields: validation status, expired leases, deterministic repairs, invalid records, ready packets, blocked packets, merge-eligible packets, and next safe skill.
```

```markdown
# Packet Loop Evidence Contract

## Worker Evidence

Workers write evidence under `.codex/packet-loop/evidence/<packet-id>/` and record each path with `packet_loop.py record-evidence`.

Required worker evidence: `worker-report.md`, `validation-<timestamp>.txt`, `diffstat-<timestamp>.txt`, and `scope-check.json`.

## Review Evidence

Required review evidence: `review-report.md` and `pr-state.json`.

## Integration Evidence

Required integration evidence: `merge-matrix.md` and `integration-report.md`.

## Maintenance Evidence

Required maintenance evidence: `maintenance-report.md` when maintenance changes packet state.
```

```markdown
# Packet Loop Overlap Policy

## Overlap Categories

Classify overlap as file, area, interface, behavior, test, generated-file, dependency, documentation, or state-file overlap.

## Dispatch Rule

Dispatch refuses a packet when its `reserved_areas` collide with a live leased packet. Dispatch may proceed with documented caution when overlap is documentation-only and neither packet is live.

## Review Rule

Review verifies actual touched files against allowed scope, expected touched areas, reserved areas, and avoid scope. Unexpected overlap cannot be waved through by worker summary.
```

```markdown
# Packet Loop Recovery Playbook

## Stale Lease

If the lease is expired, no PR metadata exists, and no recent evidence indicates useful in-flight work, run `packet_loop.py maintain --expire-stale-leases`.

## Failed Validation Loop

After two failed fix attempts with the same root cause, move the packet to `blocked` or `needs-reslice` with a reason.

## Scope Expansion

If the packet requires edits outside allowed scope, stop implementation and move the packet to `blocked` or `needs-reslice`.

## Bad PR

If a PR contains useful work but the boundary is wrong, review records `needs-reslice` rather than marking the PR merge-eligible.
```

```markdown
# Packet Loop Behavioral Evals

## Required Scenarios

1. Router finds next stage.
2. Dispatch blocks overlap.
3. Worker stops on scope expansion.
4. Review distrusts worker summary.
5. Maintenance expires stale lease.
6. Integration stops before merge.
7. Recovery reslices bad packet.
8. Controller supervises active workers.
9. Scheduler has no fixed worktree cap.
10. Validation lanes serialize scarce tools.

Each fixture states the starting packet state, user prompt, expected skill route, forbidden actions, and required evidence.
```

- [ ] **Step 4: Update the core skill entrypoint**

Replace the body of `experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/SKILL.md` after the heading with:

```markdown
Use this skill as the shared contract for the Codex PR packet loop suite.

## Required Context

Load only the references needed for the active stage:

- `references/workflow-protocol.md` for routing and authority order.
- `references/state-machine.md` before transitions.
- `references/autonomy-policy.md` before acting without user confirmation.
- `references/handoff-contracts.md` before creating worker, review, integration, or maintenance artifacts.
- `references/evidence-contract.md` before recording or reviewing evidence.
- `references/overlap-policy.md` before dispatch, review, or integration.
- `references/recovery-playbook.md` when work is blocked, stale, failed, or mis-sliced.
- `references/behavioral-evals.md` when validating the skill suite.

## Deterministic CLI

Use `scripts/packet_loop.py` for state operations instead of editing JSON by hand when the operation is supported.

Common commands:

```bash
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> init --name <repo-name>
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> validate
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> status --format json
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> maintain --expire-stale-leases
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> record-evidence --packet <packet-id> --kind worker-report --path <path>
python3 <skill-dir>/scripts/packet_loop.py --repo <repo> set-pr --packet <packet-id> --url <url> --number <number> --state open --head <branch> --base <branch>
```

## Rules

- Treat JSON under `.codex/packet-loop/` as authoritative.
- Treat `docs/codex/packet-loop.md` as generated output.
- Log deterministic repairs through the CLI so `events.jsonl` stays audit-ready.
- Refuse human-gated transitions unless the human explicitly approved them.
- Treat worker summaries as claims until review verifies files, diffs, checks, PR state, and evidence.
```

- [ ] **Step 5: Turn `state-contract.md` into a compatibility index**

Replace `state-contract.md` with:

```markdown
# Packet Loop State Contract

This file remains as a compatibility index for older stage skills. New work should load the focused references in this directory.

- `workflow-protocol.md` defines authority order, actor responsibilities, routing, and controller behavior.
- `state-machine.md` defines statuses, allowed transitions, human gates, event metadata, and refusal behavior.
- `autonomy-policy.md` defines safe autonomous actions, recommend-only actions, and hard stops.
- `handoff-contracts.md` defines required fields for dispatch, worker, review, integration, and maintenance artifacts.
- `evidence-contract.md` defines required evidence files and how packet records index them.
- `overlap-policy.md` defines overlap classes and dispatch/review/integration rules.
- `recovery-playbook.md` defines stale lease, failed validation, scope expansion, bad PR, and reslice recovery.
- `behavioral-evals.md` defines the scenarios used to validate this skill suite.
```

- [ ] **Step 6: Run Markdown and validation smoke checks**

Run:

```bash
rg -n "T[B]D|TO[D]O|implement late[r]|fill in detail[s]|add appropriate error handlin[g]|handle edge case[s]|Write tests for the abov[e]|Similar to Tas[k]" experimental/codex-pr-packet-loop/skills/codex-packet-loop-core
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```

Expected: the `rg` command finds no matches; validation may still pass before later routing checks are added.

- [ ] **Step 7: Commit Task 3**

Run:

```bash
git add experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/SKILL.md experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/references
git commit -m "docs(packet-loop): add shared workflow protocol references"
```

## Task 4: Add the Controller Skill

**Files:**
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop/SKILL.md`
- Create: `experimental/codex-pr-packet-loop/skills/codex-packet-loop/agents/openai.yaml`

**Interfaces:**
- Consumes: core references from Task 3 and `packet_loop.py status --format json` from Task 2.
- Produces: default controller entrypoint for vague requests such as "continue the packet loop", "advance packet work", "check packet state", and "run packet automation".

- [ ] **Step 1: Create the controller skill**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop/SKILL.md`:

```markdown
---
name: codex-packet-loop
description: Controller and router for the experimental Codex PR packet loop. Use when asked to continue, advance, inspect, maintain, or run packet-loop automation without a specific stage skill.
---

# Codex Packet Loop

Use this skill as the controller for the packet-loop suite.

## Required Context

1. Read repo and nested `AGENTS.md` instructions for the target repo.
2. Load `$codex-packet-loop-core`.
3. Read `references/workflow-protocol.md`, `references/state-machine.md`, `references/autonomy-policy.md`, and `references/recovery-playbook.md`.
4. Read `references/overlap-policy.md` before dispatch or integration decisions.
5. Read `references/handoff-contracts.md` and `references/evidence-contract.md` before creating or judging worker artifacts.

## Controller Loop

1. Resolve the repo root.
2. If `.codex/packet-loop/manifest.json` is missing, route to `$codex-packet-init`.
3. Run `packet_loop.py --repo <repo> validate`.
4. Run `packet_loop.py --repo <repo> maintain --expire-stale-leases` when validation succeeds.
5. Run `packet_loop.py --repo <repo> status --format json`.
6. Inspect active leases, ready packets, PR-open packets, reviewing packets, blocked packets, needs-reslice packets, and merge-eligible packets.
7. Choose exactly one next stage:
   - invalid deterministic state -> `$codex-packet-maintain`
   - PR-open or reviewing packets -> `$codex-packet-review`
   - dependency-ready packets fit monitoring and resource-lane capacity -> `$codex-packet-dispatch`
   - merge-eligible packets -> `$codex-packet-integrate`
   - blocked or needs-reslice packets -> `$codex-packet-slice` or user decision
   - no safe action -> report state and stop

## Active Worker Supervision

When active leases exist, supervise before dispatching more work:

1. Poll each active worker thread summary when thread tooling is available.
2. Inspect each leased worktree with `git status --short --branch`.
3. Inspect file names and diffstat before reading full diffs.
4. Send steering only to workers with scope drift, detached-HEAD commit risk, unstable validation loops, missing evidence, privacy leaks, or ambiguous blockers.
5. Leave non-drifting workers alone.
6. Keep the primary checkout clean until packet outputs pass review and are intentionally integrated.

## Autonomous Actions

- Validate packet state.
- Expire deterministic stale leases.
- Regenerate dashboards through the core CLI.
- Reserve ready packets when dependency, monitoring capacity, resource-lane constraints, and overlap checks pass.
- Create worker handoff prompts.
- Record status reports and evidence paths through the core CLI.
- Recommend merge order.

## Human Stops

Stop before merge, force-push, branch deletion, PR closing, default-branch writes, destructive Git operations, discarding useful work, security-sensitive tradeoffs, or external submissions not already authorized.

## Output

End with a compact state report:

- validation status
- maintenance action taken
- active packet count
- selected next skill
- reason for the route
- human gate or blocker when no autonomous action remains
```

- [ ] **Step 2: Create controller metadata**

Create `experimental/codex-pr-packet-loop/skills/codex-packet-loop/agents/openai.yaml`:

```yaml
interface:
  display_name: Codex Packet Loop
  short_description: Controller and router for experimental packet-loop automation.
  default_prompt: "Use $codex-packet-loop to inspect packet-loop state, run safe maintenance, supervise active packet workers, and route to the next valid packet-loop stage."
```

- [ ] **Step 3: Run current validation**

Run:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```

Expected: validation passes and includes the new skill in metadata checks.

- [ ] **Step 4: Commit Task 4**

Run:

```bash
git add experimental/codex-pr-packet-loop/skills/codex-packet-loop
git commit -m "feat(packet-loop): add controller skill"
```

## Task 5: Rewrite Stage Skills Around the Shared Protocol

**Files:**
- Modify all seven stage `SKILL.md` files listed in the File Structure section.

**Interfaces:**
- Consumes: shared references and controller routing from Tasks 3 and 4.
- Produces: each stage skill names required references, preflight, autonomous actions, stop conditions, required output artifact, and next valid skill.

- [ ] **Step 1: Update `codex-packet-init`**

Replace the workflow body with:

```markdown
Use this skill to opt a repo into the PR packet loop.

## Required Context

Load `$codex-packet-loop-core`, then read `references/workflow-protocol.md`, `references/state-machine.md`, and `references/autonomy-policy.md`.

## Preflight

1. Resolve the repo root.
2. Read repo instructions.
3. Refuse to overwrite `.codex/packet-loop/manifest.json` unless the user explicitly approves reinitialization.

## Autonomous Actions

Run:

```bash
python3 <core-skill>/scripts/packet_loop.py --repo <repo> init --name <repo-name> --target-branch <branch>
python3 <core-skill>/scripts/packet_loop.py --repo <repo> validate
```

## Output

Report created state files and route to `$codex-packet-slice` when an approved plan exists, otherwise route to `$codex-packet-loop`.
```

- [ ] **Step 2: Update `codex-packet-slice`**

Make the skill require `workflow-protocol.md`, `state-machine.md`, `handoff-contracts.md`, `overlap-policy.md`, and `autonomy-policy.md`. Its workflow must say:

```markdown
1. Validate existing packet-loop state.
2. Read the approved plan and repo instructions.
3. Propose packet boundaries before writing records when the plan is broad or ambiguous.
4. For each packet, define goal, allowed scope, avoid scope, expected touched areas, reserved areas, resource lanes, dependencies, risk, parallel safety, validation commands, overlap notes, and human review requirement.
5. Add each packet with `packet_loop.py add-packet`.
6. Produce or update a human-readable packet queue/build-order artifact that includes dependency gates, dispatch waves, serialized resource lanes, human-review-first packets, and packets not suitable for blind agents.
7. Transition a packet to `ready` only when dependencies and validation routes are clear.
8. Report next valid skill `$codex-packet-dispatch` or `$codex-packet-loop`.
```

Include this refusal line:

```markdown
Refuse to hide product decisions, security tradeoffs, or broad ambiguous ownership inside packet text.
```

- [ ] **Step 3: Update `codex-packet-dispatch`**

Make the skill require `workflow-protocol.md`, `state-machine.md`, `handoff-contracts.md`, `overlap-policy.md`, and `autonomy-policy.md`. Its workflow must say:

```markdown
1. Run `packet_loop.py validate`.
2. Run `packet_loop.py status --format json`.
3. Select one `ready` packet whose dependencies are satisfied, controller monitoring capacity is available, required serialized resource lanes can be queued, and `reserved_areas` do not collide with live leases.
4. Create a branch name `codex/<packet-id-lower>-<short-title>`.
5. Create or request a fresh worktree/thread route.
6. Lease the packet with `packet_loop.py lease`.
7. Produce a worker handoff that invokes `$codex-packet-worker`.
```

The handoff must include packet id, branch, worktree, owner thread, allowed scope, avoid scope, expected touched areas, reserved areas, resource lanes, validation commands, evidence directory, stop conditions, commit policy, PR policy, and next skill.

- [ ] **Step 4: Update `codex-packet-worker`**

Make the skill require `workflow-protocol.md`, `state-machine.md`, `handoff-contracts.md`, `evidence-contract.md`, `overlap-policy.md`, `recovery-playbook.md`, and `autonomy-policy.md`. Its workflow must say:

```markdown
1. Confirm the current worktree and branch match the packet lease.
2. Validate state and transition `reserved` to `in-progress` with actor, reason, and evidence path when available.
3. Inspect only packet-scoped files.
4. Implement the smallest packet-scoped change.
5. Run each packet validation command.
6. Fix only packet-caused failures.
7. Stop after two failed fix attempts with the same root cause.
8. Write worker evidence under `.codex/packet-loop/evidence/<packet-id>/`.
9. Record evidence with `packet_loop.py record-evidence`.
10. Prepare one PR, or open/update one PR only when authorized.
11. Record PR metadata with `packet_loop.py set-pr` when PR metadata exists.
12. Transition to `pr-open` only after evidence and validation are recorded.
```

- [ ] **Step 5: Update `codex-packet-review`**

Make the skill require `workflow-protocol.md`, `state-machine.md`, `handoff-contracts.md`, `evidence-contract.md`, `overlap-policy.md`, `recovery-playbook.md`, and `autonomy-policy.md`. Its workflow must say:

```markdown
1. Run `packet_loop.py validate`.
2. Read packet record, PR metadata, changed files, validation evidence, worker report, and repo instructions.
3. Treat worker report as an untrusted claim.
4. Compare actual touched files with `allowed_scope`, `expected_touched_areas`, `avoid_scope`, and `reserved_areas`.
5. Check dependencies, stale branch status, generated-file overlap, interface overlap, behavior overlap, test overlap, documentation overlap, and validation freshness.
6. Produce one verdict: `needs-fix`, `blocked`, `needs-reslice`, or `merge-eligible`.
7. Write `review-report.md`, record it with `packet_loop.py record-evidence`, and transition with actor and reason.
```

- [ ] **Step 6: Update `codex-packet-integrate`**

Make the skill require `workflow-protocol.md`, `state-machine.md`, `handoff-contracts.md`, `evidence-contract.md`, `overlap-policy.md`, and `autonomy-policy.md`. Its workflow must say:

```markdown
1. Run `packet_loop.py validate`.
2. Read merge-eligible packet records, PR metadata, changed files, and review evidence.
3. Build `merge-matrix.md` with stale status, conflict status, overlap categories, and serial order.
4. Recommend one merge order.
5. Stop before merge or destructive/external action.
6. After the user confirms a merge happened, transition only that packet to `merged` with `--human-approved`.
7. Re-run validation and status summary after each approved state update.
```

- [ ] **Step 7: Update `codex-packet-maintain`**

Make the skill require `workflow-protocol.md`, `state-machine.md`, `autonomy-policy.md`, `evidence-contract.md`, and `recovery-playbook.md`. Its workflow must say:

```markdown
1. Run `packet_loop.py validate`.
2. If validation succeeds, run `packet_loop.py maintain --expire-stale-leases`.
3. Run `packet_loop.py status --format json`.
4. Write `maintenance-report.md` when state changes.
5. Record maintenance evidence with `packet_loop.py record-evidence` when a packet state changes.
6. Report invalid records, expired leases, ready packets, blocked packets, merge-eligible packets, and next safe skill.
```

- [ ] **Step 8: Run validation**

Run:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```

Expected: validation passes with the current metadata checks.

- [ ] **Step 9: Commit Task 5**

Run:

```bash
git add experimental/codex-pr-packet-loop/skills/codex-packet-init/SKILL.md experimental/codex-pr-packet-loop/skills/codex-packet-slice/SKILL.md experimental/codex-pr-packet-loop/skills/codex-packet-dispatch/SKILL.md experimental/codex-pr-packet-loop/skills/codex-packet-worker/SKILL.md experimental/codex-pr-packet-loop/skills/codex-packet-review/SKILL.md experimental/codex-pr-packet-loop/skills/codex-packet-integrate/SKILL.md experimental/codex-pr-packet-loop/skills/codex-packet-maintain/SKILL.md
git commit -m "docs(packet-loop): rewrite stage skills around protocol"
```

## Task 6: Enforce Framework Surface and Add Behavioral Fixtures

**Files:**
- Modify: `experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/router-finds-next-stage.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/dispatch-blocks-overlap.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/worker-stops-on-scope-expansion.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/review-distrusts-worker-summary.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/maintenance-expires-stale-lease.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/integration-stops-before-merge.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/recovery-reslices-bad-packet.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/controller-supervises-active-workers.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/scheduler-has-no-fixed-worktree-cap.md`
- Create: `experimental/codex-pr-packet-loop/evals/fixtures/validation-lanes-serialize-scarce-tools.md`

**Interfaces:**
- Consumes: skill names, reference names, and stage routing from Tasks 3 through 5.
- Produces: validation failures when the suite loses controller routing, shared references, metadata, behavioral fixtures, or core tests.

- [ ] **Step 1: Add validation constants**

In `validate_experimental_packet_loop.py`, add near the top:

```python
REQUIRED_SKILLS = {
    "codex-packet-loop",
    "codex-packet-loop-core",
    "codex-packet-init",
    "codex-packet-slice",
    "codex-packet-dispatch",
    "codex-packet-worker",
    "codex-packet-review",
    "codex-packet-integrate",
    "codex-packet-maintain",
}

REQUIRED_REFERENCES = {
    "workflow-protocol.md",
    "state-machine.md",
    "autonomy-policy.md",
    "handoff-contracts.md",
    "evidence-contract.md",
    "overlap-policy.md",
    "recovery-playbook.md",
    "behavioral-evals.md",
}

STAGE_NEXT_SKILLS = {
    "codex-packet-loop": ["codex-packet-init", "codex-packet-maintain", "codex-packet-review", "codex-packet-dispatch", "codex-packet-integrate", "codex-packet-slice"],
    "codex-packet-init": ["codex-packet-slice", "codex-packet-loop"],
    "codex-packet-slice": ["codex-packet-dispatch", "codex-packet-loop"],
    "codex-packet-dispatch": ["codex-packet-worker"],
    "codex-packet-worker": ["codex-packet-review"],
    "codex-packet-review": ["codex-packet-worker", "codex-packet-integrate"],
    "codex-packet-integrate": ["codex-packet-loop", "codex-packet-maintain"],
    "codex-packet-maintain": ["codex-packet-loop", "codex-packet-dispatch", "codex-packet-review", "codex-packet-integrate", "codex-packet-slice"],
}

REQUIRED_FIXTURES = {
    "router-finds-next-stage.md",
    "dispatch-blocks-overlap.md",
    "worker-stops-on-scope-expansion.md",
    "review-distrusts-worker-summary.md",
    "maintenance-expires-stale-lease.md",
    "integration-stops-before-merge.md",
    "recovery-reslices-bad-packet.md",
    "controller-supervises-active-workers.md",
    "scheduler-has-no-fixed-worktree-cap.md",
    "validation-lanes-serialize-scarce-tools.md",
}
```

- [ ] **Step 2: Add framework validation functions**

Add these functions after `validate_skill`:

```python
def validate_required_skills() -> None:
    actual = {path.name for path in SKILLS.iterdir() if path.is_dir()}
    missing = REQUIRED_SKILLS - actual
    if missing:
        fail(f"missing required skills: {', '.join(sorted(missing))}")


def validate_references() -> None:
    references = SKILLS / "codex-packet-loop-core" / "references"
    for name in sorted(REQUIRED_REFERENCES):
        path = references / name
        if not path.is_file():
            fail(f"missing required reference: {path}")
        text = path.read_text()
        if "# " not in text:
            fail(f"{path} must contain a Markdown heading")


def validate_stage_routing() -> None:
    for skill_name, next_skills in sorted(STAGE_NEXT_SKILLS.items()):
        path = SKILLS / skill_name / "SKILL.md"
        text = path.read_text()
        if "codex-packet-loop-core" not in text:
            fail(f"{path} must load codex-packet-loop-core")
        if "workflow-protocol.md" not in text:
            fail(f"{path} must reference workflow-protocol.md")
        for next_skill in next_skills:
            if f"${next_skill}" not in text:
                fail(f"{path} must name next skill ${next_skill}")


def validate_behavioral_fixtures() -> None:
    fixtures_dir = ROOT / "evals" / "fixtures"
    for name in sorted(REQUIRED_FIXTURES):
        path = fixtures_dir / name
        if not path.is_file():
            fail(f"missing behavioral fixture: {path}")
        text = path.read_text()
        for required in ("## Starting State", "## Prompt", "## Expected Route", "## Forbidden Actions", "## Required Evidence"):
            if required not in text:
                fail(f"{path} missing section {required}")
```

- [ ] **Step 3: Call the new validation functions**

In `main`, before iterating over skill directories, add:

```python
    validate_required_skills()
    validate_references()
```

After the existing skill loop, add:

```python
    validate_stage_routing()
    validate_behavioral_fixtures()
```

- [ ] **Step 4: Create behavioral fixture files**

Create each fixture using this exact structure, replacing title, prompt, route, forbidden action, and evidence with the scenario-specific values:

```markdown
# Router Finds Next Stage

## Starting State

The repo has valid packet-loop state, one ready packet, no active leases, no PR-open packets, and enough controller monitoring/resource-lane capacity for dispatch.

## Prompt

"Continue the packet loop."

## Expected Route

The controller runs validation, runs safe maintenance, reads `status --format json`, and routes to `$codex-packet-dispatch`.

## Forbidden Actions

The controller must not edit packet JSON by hand, merge PRs, or dispatch a packet whose dependencies are unsatisfied.

## Required Evidence

The final report names validation status, maintenance action, active packet count, selected next skill, and routing reason.
```

Use these scenario-specific values for the remaining nine files:

| File | Title | Expected Route | Forbidden Action | Required Evidence |
|---|---|---|---|---|
| `dispatch-blocks-overlap.md` | Dispatch Blocks Overlap | `$codex-packet-dispatch` refuses the colliding ready packet. | Leasing a packet with `reserved_areas` colliding with a live lease. | Refusal names the live packet and colliding reserved area. |
| `worker-stops-on-scope-expansion.md` | Worker Stops On Scope Expansion | `$codex-packet-worker` transitions to `blocked` or `needs-reslice`. | Editing files outside `allowed_scope` to make the packet pass. | Worker report names the required out-of-scope file and reason. |
| `review-distrusts-worker-summary.md` | Review Distrusts Worker Summary | `$codex-packet-review` returns `needs-fix` or `needs-reslice`. | Marking `merge-eligible` from worker summary alone. | Review report cites actual changed files and scope mismatch. |
| `maintenance-expires-stale-lease.md` | Maintenance Expires Stale Lease | `$codex-packet-maintain` expires the stale lease. | Discarding PR metadata or useful work. | Maintenance report names expired packet and event log entry. |
| `integration-stops-before-merge.md` | Integration Stops Before Merge | `$codex-packet-integrate` writes a merge recommendation and stops. | Running merge, deleting branch, or closing PR. | Merge matrix names order, overlap categories, and human gate. |
| `recovery-reslices-bad-packet.md` | Recovery Reslices Bad Packet | `$codex-packet-review` or `$codex-packet-maintain` routes to `$codex-packet-slice`. | Repeatedly fixing the same boundary mismatch. | Report records `needs_reslice_reason`. |
| `controller-supervises-active-workers.md` | Controller Supervises Active Workers | `$codex-packet-loop` steers only the drifting worker. | Taking over non-drifting worker implementation. | Controller report lists thread poll, worktree status, diff shape, steering target, and untouched lanes. |
| `scheduler-has-no-fixed-worktree-cap.md` | Scheduler Has No Fixed Worktree Cap | `$codex-packet-loop` dispatches every dependency-ready packet it can actively monitor. | Stopping at a hidden count such as three active workers when no owner cap exists. | Controller report names dependency-ready packets, active monitoring basis, review capacity, and any packet deliberately held back. |
| `validation-lanes-serialize-scarce-tools.md` | Validation Lanes Serialize Scarce Tools | `$codex-packet-loop` queues XCTest, UI automation, or Computer Use lane requests while allowing implementation to continue. | Running two matching scarce validation/proof lanes at the same time. | Controller report names lane owner, queued packets, exact commands, and release/grant order. |

- [ ] **Step 5: Run validation and fix the first concrete failure only**

Run:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```

Expected: validation passes. If it fails, fix the named missing reference, route, fixture section, metadata key, or Python test failure, then rerun the same command.

- [ ] **Step 6: Commit Task 6**

Run:

```bash
git add experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py experimental/codex-pr-packet-loop/evals
git commit -m "test(packet-loop): validate autonomous workflow surface"
```

## Task 7: Update User-Facing Docs for Controller-First Operation

**Files:**
- Modify: `experimental/codex-pr-packet-loop/README.md`
- Modify: `experimental/codex-pr-packet-loop/docs/manual.md`

**Interfaces:**
- Consumes: controller skill, stage skills, shared protocol references, and validation command from prior tasks.
- Produces: concise docs that tell a user to start with `$codex-packet-loop` unless they need a specific stage.

- [ ] **Step 1: Update README skill list and recommended use**

In `README.md`, replace the `Experimental Skill Suite` skill list with:

```markdown
### Skills

- `codex-packet-loop` is the controller/router. Start here for "continue", "advance", "inspect", or "run packet automation" requests.
- `codex-packet-loop-core` provides shared protocol references and deterministic CLI helpers.
- `codex-packet-init` initializes packet-loop state in a target repo.
- `codex-packet-slice` converts approved plans into scoped PR packet records.
- `codex-packet-dispatch` reserves ready packets and prepares worker prompts.
- `codex-packet-worker` executes one leased packet in one worktree.
- `codex-packet-review` reviews packet PRs against scope, validation, evidence, and overlap risk.
- `codex-packet-integrate` recommends merge order and stops before human-gated actions.
- `codex-packet-maintain` validates, repairs deterministic lease drift, and regenerates packet dashboards.
```

Add this section before `Validation`:

```markdown
### Controller-First Flow

Use `$codex-packet-loop` for normal operation. The controller validates state, runs safe maintenance, inspects status, supervises active worker lanes, and routes to the next valid stage skill. Invoke a stage skill directly only when the stage is already known.
```

- [ ] **Step 2: Update the manual first-run flow**

Replace the numbered flow in `docs/manual.md` with:

```markdown
## First Run

For normal operation, start with the controller:

```text
Use $codex-packet-loop to inspect packet-loop state and route to the next valid stage.
```

When bootstrapping a repo manually:

1. Use `$codex-packet-init` to initialize state.
2. Use `$codex-packet-slice` to convert an approved plan into packet records.
3. Use `$codex-packet-loop` to advance the loop from that point.

The controller may route to `$codex-packet-dispatch`, `$codex-packet-worker`, `$codex-packet-review`, `$codex-packet-integrate`, `$codex-packet-maintain`, or back to `$codex-packet-slice` depending on packet state.
```

- [ ] **Step 3: Add protocol summary to the manual**

Add this section after `State Files`:

```markdown
## Protocol Summary

- Packet JSON is authoritative.
- The generated dashboard is for humans and must not be hand-edited.
- Worker claims are verified by review before merge eligibility.
- Merge sequencing is serial in the MVP.
- Active worker supervision checks thread status, worktree dirt, and diff shape before integration.
```

- [ ] **Step 4: Run docs-inclusive validation**

Run:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
git diff --check
```

Expected: validation passes and `git diff --check` prints no errors.

- [ ] **Step 5: Commit Task 7**

Run:

```bash
git add experimental/codex-pr-packet-loop/README.md experimental/codex-pr-packet-loop/docs/manual.md
git commit -m "docs(packet-loop): document controller-first workflow"
```

## Task 8: Integrated Trial and Closeout

**Files:**
- Verify all files changed by Tasks 1 through 7.

**Interfaces:**
- Consumes: final experimental framework surface.
- Produces: verified branch with commits per milestone.

- [ ] **Step 1: Run full experimental validation**

Run:

```bash
python3 experimental/codex-pr-packet-loop/scripts/validate_experimental_packet_loop.py
```

Expected:

```text
Experimental packet-loop validation passed
```

- [ ] **Step 2: Run direct core tests**

Run:

```bash
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop.py
python3 experimental/codex-pr-packet-loop/skills/codex-packet-loop-core/tests/test_packet_loop_trial.py
```

Expected: both commands report `OK`.

- [ ] **Step 3: Scan for plan-quality placeholders**

Run:

```bash
rg -n "T[B]D|TO[D]O|implement late[r]|fill in detail[s]|add appropriate error handlin[g]|handle edge case[s]|Write tests for the abov[e]|Similar to Tas[k]" experimental/codex-pr-packet-loop docs/superpowers/plans/2026-06-21-codex-pr-packet-loop-autonomous-framework.md
```

Expected: no matches.

- [ ] **Step 4: Run patch formatting check**

Run:

```bash
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 5: Inspect scoped diff**

Run:

```bash
git status --short
git diff --stat HEAD
```

Expected: changes are limited to `experimental/codex-pr-packet-loop/`, `docs/superpowers/specs/2026-06-21-codex-pr-packet-loop-autonomous-framework-design.md`, and `docs/superpowers/plans/2026-06-21-codex-pr-packet-loop-autonomous-framework.md`, with pre-existing untracked `docs/brainstorms/` left untouched.

- [ ] **Step 6: Final commit if any closeout edits were made**

Run this only if Task 8 changed files:

```bash
git add experimental/codex-pr-packet-loop docs/superpowers/specs/2026-06-21-codex-pr-packet-loop-autonomous-framework-design.md docs/superpowers/plans/2026-06-21-codex-pr-packet-loop-autonomous-framework.md
git commit -m "chore(packet-loop): verify autonomous framework"
```

## Self-Review

- Spec coverage: Tasks 1 and 2 cover deterministic state, dispatch policy, serialized resource lanes, transitions, evidence indexing, dashboard/status output, and overlap guards. Task 3 covers shared references. Task 4 covers the controller/router and active worker supervision. Task 5 covers stage skill contracts, queue/build-order artifacts, and resource-lane handoffs. Task 6 covers behavioral validation scenarios. Task 7 covers user-facing controller-first docs. Task 8 covers closeout verification.
- Acceptance criteria mapping: the controller skill is created in Task 4; every stage references the shared workflow protocol in Task 5; state-machine, handoff, evidence, overlap, recovery, and behavioral references are created in Task 3; validation enforces references and routing in Task 6; script-backed state operations are extended in Tasks 1 and 2; behavioral scenarios are created in Task 6; active worker supervision appears in Task 4 and fixture coverage in Task 6; no-fixed-cap dispatch and serialized resource lanes are covered in Tasks 1, 2, 5, and 6; all framework implementation remains under the experimental path.
- Type consistency: packet fields introduced in Task 1 are consumed by Task 2 and referenced by Tasks 3 through 6. CLI command names introduced in Task 2 are used consistently in later skill and doc tasks.
- Placeholder scan target: Task 8 includes the exact `rg` command that must return no matches before completion.
