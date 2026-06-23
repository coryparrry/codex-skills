import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_repository_health.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_repository_health", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AuditRepositoryHealthTests(unittest.TestCase):
    def run_git(self, *args, cwd):
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True,
        )

    def run_audit(self, repo, *args):
        return subprocess.run(
            ["python3", str(SCRIPT), "--repo", str(repo), *args],
            check=True,
            text=True,
            capture_output=True,
        )

    def init_repo(self, root):
        self.run_git("init", cwd=root)
        self.run_git("config", "user.email", "test@example.com", cwd=root)
        self.run_git("config", "user.name", "Test User", cwd=root)
        self.run_git("checkout", "-b", "main", cwd=root)

    def commit_all(self, root, message="fixture"):
        self.run_git("add", ".", cwd=root)
        self.run_git("commit", "-m", message, cwd=root)

    def test_json_report_flags_missing_operating_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nSee [missing](docs/missing.md).\n")
            (root / "AGENTS.md").write_text("# Instructions\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            self.assertEqual("conditional", report["verdict"]["ready_to_proceed"])
            self.assertIn("repository_shape", report["checks"])
            self.assertIn("documentation", report["checks"])
            self.assertIn("scripts", report["checks"])
            self.assertIn("validation", report["checks"])
            self.assertIn("hygiene", report["checks"])
            self.assertGreaterEqual(report["verdict"]["blocking_issues"], 0)
            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("no setup or bootstrap script", titles)
            self.assertIn("no test command or script", titles)
            self.assertIn("broken local Markdown link", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["setup"]["status"])
            self.assertEqual("missing", responsibilities["test"]["status"])
            self.assertTrue(report["commands_run"])
            self.assertTrue(report["not_checked"])

    def test_markdown_report_maps_scripts_and_required_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            scripts = root / "scripts"
            scripts.mkdir()
            (root / "README.md").write_text("# Example\n\nRun `bash scripts/validate.sh`.\n")
            (root / "CONTRIBUTING.md").write_text("# Contributing\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (scripts / "setup.sh").write_text("#!/usr/bin/env bash\n")
            (scripts / "test.sh").write_text("#!/usr/bin/env bash\n")
            (scripts / "validate.sh").write_text("#!/usr/bin/env bash\n")
            self.commit_all(root)

            result = self.run_audit(root)

            for section in [
                "## Verdict",
                "## Findings",
                "## Repository Shape",
                "## Documentation",
                "## Scripts",
                "## Validation",
                "## Hygiene",
                "## Commands Run",
                "## Not Checked",
            ]:
                self.assertIn(section, result.stdout)
            self.assertIn("setup: present", result.stdout)
            self.assertIn("test: present", result.stdout)
            self.assertIn("cibuild: present", result.stdout)
            self.assertIn("scripts/validate.sh", result.stdout)

    def test_detects_skill_plugin_mirror_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            source_skill = root / "skills" / "demo-skill"
            mirror_skill = root / "plugins" / "codex-skills" / "skills" / "demo-skill"
            (source_skill / "agents").mkdir(parents=True)
            (mirror_skill / "agents").mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (source_skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Use when testing\n---\n")
            (source_skill / "agents" / "openai.yaml").write_text("display_name: Demo\n")
            (mirror_skill / "SKILL.md").write_text("---\nname: demo-skill\ndescription: Drifted\n---\n")
            (mirror_skill / "agents" / "openai.yaml").write_text("display_name: Demo\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("skill plugin mirror drift", titles)
            packaging = report["checks"]["packaging"]
            self.assertEqual(["demo-skill"], packaging["drifted_skill_mirrors"])
            self.assertEqual([], packaging["missing_skill_mirrors"])

    def test_detects_stale_plugin_only_skill_mirror(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            source_skill = root / "skills" / "live-skill"
            mirror_skill = root / "plugins" / "codex-skills" / "skills" / "live-skill"
            stale_mirror = root / "plugins" / "codex-skills" / "skills" / "stale-skill"
            (source_skill / "agents").mkdir(parents=True)
            (mirror_skill / "agents").mkdir(parents=True)
            stale_mirror.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (source_skill / "SKILL.md").write_text("---\nname: live-skill\ndescription: Use when testing\n---\n")
            (source_skill / "agents" / "openai.yaml").write_text("display_name: Live\n")
            (mirror_skill / "SKILL.md").write_text("---\nname: live-skill\ndescription: Use when testing\n---\n")
            (mirror_skill / "agents" / "openai.yaml").write_text("display_name: Live\n")
            (stale_mirror / "SKILL.md").write_text("---\nname: stale-skill\ndescription: Use when stale\n---\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("skill plugin mirror drift", titles)
            packaging = report["checks"]["packaging"]
            self.assertEqual(["stale-skill"], packaging["extra_skill_mirrors"])

    def test_iter_files_prunes_skipped_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            skipped = root / "node_modules" / "package"
            docs.mkdir()
            skipped.mkdir(parents=True)
            (docs / "visible.md").write_text("# Visible\n")
            (skipped / "hidden.md").write_text("# Hidden\n")

            module = load_audit_module()
            files = sorted(str(path.relative_to(root)) for path in module.iter_files(root, "*.md"))

            self.assertEqual(["docs/visible.md"], files)

    def test_skill_mirror_reference_docs_are_not_duplicate_doc_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            source_ref = root / "skills" / "demo-skill" / "references"
            mirror_ref = root / "plugins" / "codex-skills" / "skills" / "demo-skill" / "references"
            source_ref.mkdir(parents=True)
            mirror_ref.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (source_ref / "demo.md").write_text("# Demo\n")
            (mirror_ref / "demo.md").write_text("# Demo\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("duplicate-looking documentation", titles)

    def test_private_and_internal_words_do_not_count_as_unresolved_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (docs / "security.md").write_text(
                "# Security\n\nUse private disclosure for internal routing context.\n"
            )
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            self.assertEqual([], report["checks"]["documentation"]["unresolved_markers"])

    def test_titlecase_todo_words_do_not_count_as_unresolved_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (docs / "workflow.md").write_text("# Workflow\n\nTodo/checklist items are part of the UI vocabulary.\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            self.assertEqual([], report["checks"]["documentation"]["unresolved_markers"])

    def test_uppercase_todo_marker_counts_as_unresolved_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (docs / "workflow.md").write_text("# Workflow\n\nTODO: finish setup docs.\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            self.assertEqual(["docs/workflow.md:3"], report["checks"]["documentation"]["unresolved_markers"])

    def test_quoted_todo_examples_do_not_count_as_unresolved_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (docs / "rubric.md").write_text(
                "# Rubric\n\nA plan containing `TODO`, `TBD`, or \"write tests\" should be rejected.\n"
            )
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            self.assertEqual([], report["checks"]["documentation"]["unresolved_markers"])

    def test_skill_references_do_not_make_public_docs_duplicate_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            public_docs = root / "docs"
            source_ref = root / "skills" / "demo-skill" / "references"
            mirror_ref = root / "plugins" / "codex-skills" / "skills" / "demo-skill" / "references"
            public_docs.mkdir()
            source_ref.mkdir(parents=True)
            mirror_ref.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (public_docs / "demo.md").write_text("# Demo\n")
            (source_ref / "demo.md").write_text("# Demo\n")
            (mirror_ref / "demo.md").write_text("# Demo\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("duplicate-looking documentation", titles)


if __name__ == "__main__":
    unittest.main()
