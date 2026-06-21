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


if __name__ == "__main__":
    unittest.main()
