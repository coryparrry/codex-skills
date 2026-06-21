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
            timeout=10,
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
