import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "clean_merged_branch.sh"


class CleanMergedBranchTests(unittest.TestCase):
    def run_git(self, *args, cwd, check=True):
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=check,
            text=True,
            capture_output=True,
        )

    def test_verifies_squash_merge_by_diff_when_default_branch_advanced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            origin = root / "origin.git"
            work = root / "work"
            bin_dir = root / "bin"
            bin_dir.mkdir()

            subprocess.run(["git", "init", "--bare", str(origin)], check=True, capture_output=True)
            subprocess.run(
                ["git", f"--git-dir={origin}", "symbolic-ref", "HEAD", "refs/heads/main"],
                check=True,
                capture_output=True,
            )
            subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True)

            self.run_git("config", "user.email", "test@example.com", cwd=work)
            self.run_git("config", "user.name", "Test", cwd=work)

            (work / "file.txt").write_text("base\n")
            self.run_git("add", "file.txt", cwd=work)
            self.run_git("commit", "-m", "initial", cwd=work)
            self.run_git("push", "-u", "origin", "main", cwd=work)

            self.run_git("switch", "-c", "feature", cwd=work)
            (work / "file.txt").write_text("base\nfeature\n")
            self.run_git("commit", "-am", "feature", cwd=work)
            self.run_git("push", "origin", "feature", cwd=work)

            self.run_git("switch", "main", cwd=work)
            (work / "main.txt").write_text("main advanced\n")
            self.run_git("add", "main.txt", cwd=work)
            self.run_git("commit", "-m", "advance main", cwd=work)
            self.run_git("merge", "--squash", "feature", cwd=work)
            self.run_git("commit", "-m", "squash feature", cwd=work)
            merge_oid = self.run_git("rev-parse", "HEAD", cwd=work).stdout.strip()
            self.run_git("push", "origin", "main", cwd=work)
            self.run_git("switch", "feature", cwd=work)

            gh = bin_dir / "gh"
            gh.write_text(
                "#!/usr/bin/env bash\n"
                f"printf '1\\thttps://example.test/pr/1\\t2026-06-05T00:00:00Z\\t{merge_oid}\\t1\\n'\n"
            )
            gh.chmod(0o755)

            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
            result = subprocess.run(
                ["bash", str(SCRIPT)],
                cwd=work,
                env=env,
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertIn("diff matches merged PR #1", result.stdout)
            self.assertIn("Deletion used verified merge diff equality.", result.stdout)
            self.assertNotIn("feature", self.run_git("branch", "--list", cwd=work).stdout)
            self.assertEqual("", self.run_git("ls-remote", "--heads", "origin", "feature", cwd=work).stdout)

    def test_verifies_rebase_merge_range_for_multi_commit_pr(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            origin = root / "origin.git"
            work = root / "work"
            bin_dir = root / "bin"
            bin_dir.mkdir()

            subprocess.run(["git", "init", "--bare", str(origin)], check=True, capture_output=True)
            subprocess.run(
                ["git", f"--git-dir={origin}", "symbolic-ref", "HEAD", "refs/heads/main"],
                check=True,
                capture_output=True,
            )
            subprocess.run(["git", "clone", str(origin), str(work)], check=True, capture_output=True)

            self.run_git("config", "user.email", "test@example.com", cwd=work)
            self.run_git("config", "user.name", "Test", cwd=work)

            (work / "file.txt").write_text("base\n")
            self.run_git("add", "file.txt", cwd=work)
            self.run_git("commit", "-m", "initial", cwd=work)
            self.run_git("push", "-u", "origin", "main", cwd=work)

            self.run_git("switch", "-c", "feature", cwd=work)
            (work / "one.txt").write_text("one\n")
            self.run_git("add", "one.txt", cwd=work)
            self.run_git("commit", "-m", "feature one", cwd=work)
            (work / "two.txt").write_text("two\n")
            self.run_git("add", "two.txt", cwd=work)
            self.run_git("commit", "-m", "feature two", cwd=work)
            feature_commits = self.run_git("rev-list", "--reverse", "main..feature", cwd=work).stdout.splitlines()
            self.run_git("push", "origin", "feature", cwd=work)

            self.run_git("switch", "main", cwd=work)
            (work / "main.txt").write_text("main advanced\n")
            self.run_git("add", "main.txt", cwd=work)
            self.run_git("commit", "-m", "advance main", cwd=work)
            for commit in feature_commits:
                self.run_git("cherry-pick", commit, cwd=work)
            merge_oid = self.run_git("rev-parse", "HEAD", cwd=work).stdout.strip()
            self.run_git("push", "origin", "main", cwd=work)
            self.run_git("switch", "feature", cwd=work)

            gh = bin_dir / "gh"
            gh.write_text(
                "#!/usr/bin/env bash\n"
                f"printf '2\\thttps://example.test/pr/2\\t2026-06-05T00:00:00Z\\t{merge_oid}\\t2\\n'\n"
            )
            gh.chmod(0o755)

            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
            result = subprocess.run(
                ["bash", str(SCRIPT)],
                cwd=work,
                env=env,
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertIn("Verified rebase-merged branch", result.stdout)
            self.assertIn("diff matches merged PR #2", result.stdout)
            self.assertIn("Deletion used verified merge diff equality.", result.stdout)
            self.assertNotIn("feature", self.run_git("branch", "--list", cwd=work).stdout)
            self.assertEqual("", self.run_git("ls-remote", "--heads", "origin", "feature", cwd=work).stdout)


if __name__ == "__main__":
    unittest.main()
