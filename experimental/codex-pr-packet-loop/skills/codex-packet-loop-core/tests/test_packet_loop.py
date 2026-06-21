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
            timeout=10,
        )

    def add_basic_packet(self, repo: Path, packet_id: str = "P001") -> subprocess.CompletedProcess[str]:
        return self.run_cli(
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
            "--validation-command",
            "python3 -m unittest",
        )

    def test_init_creates_manifest_events_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = self.run_cli(repo, "init", "--name", "demo")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((repo / ".codex/packet-loop/manifest.json").is_file())
            self.assertTrue((repo / ".codex/packet-loop/events.jsonl").is_file())
            self.assertTrue((repo / "docs/codex/packet-loop.md").is_file())

            manifest = json.loads((repo / ".codex/packet-loop/manifest.json").read_text())
            self.assertEqual(manifest["schema_version"], "0.1.0")
            self.assertEqual(manifest["repo"]["name"], "demo")
            self.assertEqual(manifest["repo"]["default_branch"], "main")
            self.assertEqual(manifest["repo"]["target_branch"], "main")
            self.assertEqual(manifest["mode"], "planning")
            self.assertNotIn("active_packet_limit", manifest)
            self.assertEqual(manifest["dispatch_policy"], {"mode": "no_fixed_limit", "max_active_worktrees": None})
            self.assertEqual(manifest["packet_order"], [])

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
            self.assertEqual(packet["schema_version"], "0.1.0")
            self.assertEqual(packet["status"], "candidate")
            self.assertEqual(packet["risk"], "medium")
            self.assertEqual(packet["parallel_safe"], "maybe")
            self.assertEqual(
                packet["expected_touched_areas"],
                ["experimental/codex-pr-packet-loop/skills/codex-packet-loop-core"],
            )
            self.assertNotIn("expected_area", packet)
            self.assertEqual(
                packet["validation"],
                {
                    "commands": [
                        "python3 -m unittest experimental/codex-pr-packet-loop/skills/"
                        "codex-packet-loop-core/tests/test_packet_loop.py"
                    ]
                },
            )
            self.assertNotIn("validation_command", packet)
            self.assertEqual(packet["evidence_paths"], [])
            self.assertEqual(packet["blockers"], [])

            validate = self.run_cli(repo, "validate")
            self.assertEqual(validate.returncode, 0, validate.stderr)

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
                "--parent-plan-path",
                "docs/superpowers/plans/main-plan.md",
                "--child-plan-path",
                "docs/superpowers/plans/packet-loop/P001-packet.md",
                "--source-plan-ref",
                "Task 1",
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
            self.assertEqual(packet["parent_plan_path"], "docs/superpowers/plans/main-plan.md")
            self.assertEqual(packet["child_plan_path"], "docs/superpowers/plans/packet-loop/P001-packet.md")
            self.assertEqual(packet["source_plan_refs"], ["Task 1"])
            self.assertEqual(packet["plan_format_status"], "pending")
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

    def test_rejects_packet_ids_that_can_escape_packet_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            escaped = repo / ".codex" / "leaked.json"

            for unsafe_id in ("", "../../../leaked", "/tmp/leaked", "P/001", "P\\001", "P..001", ".hidden", "P 001"):
                with self.subTest(packet_id=unsafe_id):
                    result = self.run_cli(
                        repo,
                        "add-packet",
                        "--id",
                        unsafe_id,
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
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("invalid packet id", result.stderr)
            self.assertFalse(escaped.exists())
            self.assertEqual(list((repo / ".codex/packet-loop/packets").iterdir()), [])

            transition = self.run_cli(repo, "transition", "--packet", "../../../leaked", "--status", "ready")
            self.assertNotEqual(transition.returncode, 0)
            self.assertIn("invalid packet id", transition.stderr)
            self.assertFalse(escaped.exists())

            lease = self.run_cli(
                repo,
                "lease",
                "--packet",
                "../../../leaked",
                "--owner-thread",
                "thread-123",
                "--branch",
                "codex/leaked",
                "--worktree",
                "/tmp/leaked-worktree",
            )
            self.assertNotEqual(lease.returncode, 0)
            self.assertIn("invalid packet id", lease.stderr)
            self.assertFalse(escaped.exists())

            manifest_path = repo / ".codex/packet-loop/manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["packet_order"] = ["../../../leaked"]
            manifest_path.write_text(json.dumps(manifest) + "\n")
            maintain = self.run_cli(repo, "maintain", "--expire-stale-leases")
            self.assertNotEqual(maintain.returncode, 0)
            self.assertIn("invalid packet id", maintain.stderr)
            self.assertFalse(escaped.exists())

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

    def test_init_refuses_to_overwrite_existing_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)

            result = self.run_cli(repo, "init", "--name", "replacement")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already initialized", result.stderr)
            manifest = json.loads((repo / ".codex/packet-loop/manifest.json").read_text())
            self.assertEqual(manifest["repo"]["name"], "demo")
            self.assertEqual(manifest["packet_order"], ["P001"])
            self.assertTrue((repo / ".codex/packet-loop/packets/P001.json").is_file())

    def test_transition_cannot_reserve_packet_without_lease(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "ready").returncode, 0)

            result = self.run_cli(repo, "transition", "--packet", "P001", "--status", "reserved")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid transition", result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["status"], "ready")
            self.assertIsNone(packet["lease"])

    def test_validate_rejects_reserved_packet_without_lease(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "ready").returncode, 0)

            packet_path = repo / ".codex/packet-loop/packets/P001.json"
            packet = json.loads(packet_path.read_text())
            packet["status"] = "reserved"
            packet["lease"] = None
            packet_path.write_text(json.dumps(packet) + "\n")

            result = self.run_cli(repo, "validate")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("reserved packet requires lease", result.stderr)

    def test_validate_accepts_packet_without_optional_out_of_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)

            packet_path = repo / ".codex/packet-loop/packets/P001.json"
            packet = json.loads(packet_path.read_text())
            del packet["out_of_scope"]
            packet_path.write_text(json.dumps(packet) + "\n")

            result = self.run_cli(repo, "validate")

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_lease_ready_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)
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

    def test_lease_respects_max_active_worktrees(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(
                self.run_cli(repo, "init", "--name", "demo", "--max-active-worktrees", "1").returncode,
                0,
            )
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
                    "/tmp/demo-p001",
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
                "/tmp/demo-p002",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("active packet limit", result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P002.json").read_text())
            self.assertEqual(packet["status"], "ready")
            self.assertIsNone(packet["lease"])

    def test_max_active_worktrees_counts_open_packet_with_live_lease(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(
                self.run_cli(repo, "init", "--name", "demo", "--max-active-worktrees", "1").returncode,
                0,
            )
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
                    "/tmp/demo-p001",
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "in-progress").returncode, 0)
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "pr-open").returncode, 0)

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
                "/tmp/demo-p002",
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("active packet limit", result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P002.json").read_text())
            self.assertEqual(packet["status"], "ready")
            self.assertIsNone(packet["lease"])

    def test_maintenance_expires_reserved_packet_without_pr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)
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

    def test_maintenance_rejects_invalid_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)

            packet_path = repo / ".codex/packet-loop/packets/P001.json"
            packet = json.loads(packet_path.read_text())
            packet["risk"] = "critical"
            packet_path.write_text(json.dumps(packet) + "\n")

            result = self.run_cli(repo, "maintain", "--expire-stale-leases")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("risk is invalid", result.stderr)

    def test_rejected_packet_cannot_be_reopened_automatically(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)
            self.assertEqual(
                self.run_cli(
                    repo,
                    "transition",
                    "--packet",
                    "P001",
                    "--status",
                    "rejected",
                    "--human-approved",
                ).returncode,
                0,
            )

            result = self.run_cli(repo, "transition", "--packet", "P001", "--status", "candidate")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("invalid transition", result.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["status"], "rejected")

    def test_reviewed_packet_must_be_marked_merge_eligible_before_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.assertEqual(self.run_cli(repo, "init", "--name", "demo").returncode, 0)
            self.assertEqual(self.add_basic_packet(repo).returncode, 0)
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
                ).returncode,
                0,
            )
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "in-progress").returncode, 0)
            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "pr-open").returncode, 0)
            pr_open_merge = self.run_cli(
                repo,
                "transition",
                "--packet",
                "P001",
                "--status",
                "merged",
                "--human-approved",
            )
            self.assertNotEqual(pr_open_merge.returncode, 0)
            self.assertIn("invalid transition", pr_open_merge.stderr)

            self.assertEqual(self.run_cli(repo, "transition", "--packet", "P001", "--status", "reviewing").returncode, 0)

            direct_merge = self.run_cli(
                repo,
                "transition",
                "--packet",
                "P001",
                "--status",
                "merged",
                "--human-approved",
            )
            self.assertNotEqual(direct_merge.returncode, 0)
            self.assertIn("invalid transition", direct_merge.stderr)

            self.assertEqual(
                self.run_cli(repo, "transition", "--packet", "P001", "--status", "merge-eligible").returncode,
                0,
            )
            ungated_merge = self.run_cli(repo, "transition", "--packet", "P001", "--status", "merged")
            self.assertNotEqual(ungated_merge.returncode, 0)
            self.assertIn("human-gated", ungated_merge.stderr)

            gated_merge = self.run_cli(
                repo,
                "transition",
                "--packet",
                "P001",
                "--status",
                "merged",
                "--human-approved",
            )
            self.assertEqual(gated_merge.returncode, 0, gated_merge.stderr)
            packet = json.loads((repo / ".codex/packet-loop/packets/P001.json").read_text())
            self.assertEqual(packet["status"], "merged")


if __name__ == "__main__":
    unittest.main()
