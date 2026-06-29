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

    def audit_report(self, root):
        return json.loads(self.run_audit(root, "--format", "json").stdout)

    def init_repo(self, root):
        self.run_git("init", cwd=root)
        self.run_git("config", "user.email", "test@example.com", cwd=root)
        self.run_git("config", "user.name", "Test User", cwd=root)
        self.run_git("checkout", "-b", "main", cwd=root)

    def commit_all(self, root, message="fixture"):
        self.run_git("add", ".", cwd=root)
        self.run_git("commit", "-m", message, cwd=root)

    def write_npm_fixture(self, root, readme, root_package_json, packages):
        self.init_repo(root)
        (root / "README.md").write_text(readme)
        (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
        (root / "package.json").write_text(root_package_json)
        for rel_path, package_json in packages.items():
            package_dir = root / rel_path
            package_dir.mkdir(parents=True)
            (package_dir / "package.json").write_text(package_json)
            (package_dir / "index.js").write_text(f"console.log('{package_dir.name}')\n")
        self.commit_all(root)

    def test_json_report_flags_missing_operating_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nSee [missing](docs/missing.md).\n")
            (root / "AGENTS.md").write_text("# Instructions\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "requirements.txt").write_text("requests\n")
            (root / "app.py").write_text("print('hello')\n")
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

    def test_non_yaml_workflow_files_do_not_count_as_ci_workflows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "README.md").write_text("# Workflows\n")
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("no reusable closeout gate", titles)
            self.assertEqual([], report["checks"]["validation"]["ci_workflows"])

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

    def test_documented_custom_commands_satisfy_test_and_validation_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            tools = root / "tools"
            tools.mkdir()
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run project checks with `./tools/doit --fast`.\n"
                "Run the full release gate with `./tools/doit --all`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            doit = tools / "doit"
            doit.write_text("#!/usr/bin/env bash\n")
            doit.chmod(0o755)
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertEqual("documented", responsibilities["cibuild"]["status"])
            self.assertIn("README.md:./tools/doit --fast", responsibilities["test"]["candidates"])
            self.assertIn("README.md:./tools/doit --all", responsibilities["cibuild"]["candidates"])

    def test_nested_operating_docs_can_document_custom_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            tools = root / "tools"
            docs = root / "docs"
            tools.mkdir()
            docs.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            doit = tools / "doit"
            doit.write_text("#!/usr/bin/env bash\n")
            doit.chmod(0o755)
            (docs / "DEVELOPMENT.md").write_text(
                "# Development\n\n"
                "Run project checks with `./tools/doit --fast`.\n"
                "Run the full release gate with `./tools/doit --all`.\n"
            )
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertEqual("documented", responsibilities["cibuild"]["status"])
            self.assertIn("docs/DEVELOPMENT.md:./tools/doit --fast", responsibilities["test"]["candidates"])
            self.assertIn("docs/DEVELOPMENT.md:./tools/doit --all", responsibilities["cibuild"]["candidates"])

    def test_testing_and_validation_docs_can_document_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            (root / "package.json").write_text('{"scripts": {"release-gate": "echo ok"}}\n')
            (docs / "testing.md").write_text("# Testing\n\nRun tests with `pytest`.\n")
            (docs / "validation.md").write_text(
                "# Validation\n\nRun the full validation gate with `npm run release-gate`.\n"
            )
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertEqual("documented", responsibilities["cibuild"]["status"])
            self.assertIn("docs/testing.md:pytest", responsibilities["test"]["candidates"])
            self.assertIn("docs/validation.md:npm run release-gate", responsibilities["cibuild"]["candidates"])

    def test_agent_instruction_docs_can_document_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "AGENTS.md").write_text(
                "# Agent Instructions\n\n"
                "Run tests with `pytest`.\n"
                "Run the full validation gate with `pytest`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertEqual("documented", responsibilities["cibuild"]["status"])
            self.assertIn("AGENTS.md:pytest", responsibilities["test"]["candidates"])
            self.assertIn("AGENTS.md:pytest", responsibilities["cibuild"]["candidates"])

    def test_env_prefixed_documented_commands_satisfy_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `PYTHONPATH=. pytest`.\n"
                "Run the full validation gate with `CI=1 npm run release-gate`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"release-gate": "echo ok"}}\n')
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            self.assertNotIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertEqual("documented", responsibilities["cibuild"]["status"])
            self.assertIn("README.md:PYTHONPATH=. pytest", responsibilities["test"]["candidates"])
            self.assertIn("README.md:CI=1 npm run release-gate", responsibilities["cibuild"]["candidates"])

    def test_fenced_command_blocks_can_document_custom_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            tools = root / "tools"
            tools.mkdir()
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run project checks:\n\n"
                "```sh\n"
                "./tools/doit --fast\n"
                "```\n\n"
                "Run the full release gate:\n\n"
                "```bash\n"
                "./tools/doit --all\n"
                "```\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            doit = tools / "doit"
            doit.write_text("#!/usr/bin/env bash\n")
            doit.chmod(0o755)
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertIn("README.md:./tools/doit --fast", responsibilities["test"]["candidates"])
            self.assertIn("README.md:./tools/doit --all", responsibilities["cibuild"]["candidates"])

    def test_fenced_commands_after_cd_validate_from_changed_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests:\n\n"
                "```sh\n"
                "cd frontend\n"
                "npm test\n"
                "```\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            (frontend / "package.json").write_text('{"scripts": {"test": "node --test"}}\n')
            (frontend / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("frontend/package.json:test", responsibilities["test"]["candidates"])
            documented_commands = report["checks"]["scripts"]["documented_commands"]
            self.assertIn("README.md:npm test", documented_commands["test"])

    def test_fenced_reference_examples_do_not_create_stale_documented_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "For example, a repo might use:\n\n"
                "```sh\n"
                "./tools/doit --all\n"
                "```\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("not_applicable", responsibilities["cibuild"]["status"])

    def test_fenced_generic_example_without_responsibility_does_not_create_stale_documented_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "For example:\n\n"
                "```sh\n"
                "./tools/doit --all\n"
                "```\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("not_applicable", responsibilities["cibuild"]["status"])

    def test_fenced_real_commands_with_example_wording_still_document_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "For example, to run tests:\n\n"
                "```sh\n"
                "pytest\n"
                "```\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertIn("README.md:pytest", responsibilities["test"]["candidates"])

    def test_inline_real_commands_with_example_wording_still_document_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nFor example, to run tests, use `pytest`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertIn("README.md:pytest", responsibilities["test"]["candidates"])

    def test_inline_commands_are_classified_from_nearby_command_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `pytest`; run the full validation gate with `./tools/ci`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertEqual("missing", responsibilities["cibuild"]["status"])
            self.assertIn("README.md:pytest", responsibilities["test"]["candidates"])
            self.assertEqual([], responsibilities["cibuild"]["candidates"])

    def test_inline_reference_examples_do_not_create_stale_documented_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "For example, a repo might use `./tools/doit --all`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("not_applicable", responsibilities["cibuild"]["status"])

    def test_inline_generic_example_without_responsibility_does_not_create_stale_documented_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nFor example: `./tools/doit --all`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("not_applicable", responsibilities["cibuild"]["status"])

    def test_install_test_helpers_do_not_satisfy_bootstrap_responsibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts"
            self.init_repo(root)
            scripts.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "requirements.txt").write_text("requests\n")
            (root / "app.py").write_text("print('hello')\n")
            (scripts / "test_install.sh").write_text("#!/usr/bin/env bash\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("no setup or bootstrap script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["bootstrap"]["status"])
            self.assertEqual("missing", responsibilities["setup"]["status"])
            self.assertEqual("present", responsibilities["test"]["status"])

    def test_non_command_files_do_not_satisfy_script_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools = root / "tools"
            scripts = root / "scripts"
            self.init_repo(root)
            tools.mkdir()
            scripts.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            (tools / "release-notes.md").write_text("# Release notes\n")
            (tools / "ci-config.json").write_text('{"ci": true}\n')
            (scripts / "check.py.disabled").write_text("print('disabled')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("no test command or script", titles)
            self.assertIn("no CI or full validation entry point", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])
            self.assertEqual("missing", responsibilities["cibuild"]["status"])

    def test_nested_dependency_manifests_make_setup_applicable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (frontend / "package.json").write_text('{"scripts": {"test": "node --test"}}\n')
            (frontend / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("no setup or bootstrap script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["bootstrap"]["status"])
            self.assertEqual("missing", responsibilities["setup"]["status"])

    def test_pip_install_documentation_satisfies_setup_responsibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `pip install -r requirements.txt`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "requirements.txt").write_text("requests\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no setup or bootstrap script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["setup"]["status"])
            self.assertIn("README.md:pip install -r requirements.txt", responsibilities["setup"]["candidates"])

    def test_pip_install_missing_requirements_file_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nInstall dependencies with `pip install -r missing.txt`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "requirements.txt").write_text("requests\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_python_module_pip_missing_requirements_file_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `python -m pip install -r missing.txt`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "requirements.txt").write_text("requests\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_uv_pip_missing_requirements_file_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `uv pip install -r missing.txt`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "requirements.txt").write_text("requests\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_nested_package_scripts_satisfy_test_and_validation_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (frontend / "package.json").write_text('{"scripts": {"test": "node --test", "validate": "npm test"}}\n')
            (frontend / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("frontend/package.json:test", responsibilities["test"]["candidates"])
            self.assertIn("frontend/package.json:validate", responsibilities["cibuild"]["candidates"])

    def test_stale_documented_local_commands_do_not_satisfy_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run project checks with `./tools/doit --fast`.\n"
                "Run the full release gate with `./tools/doit --all`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])
            self.assertEqual("missing", responsibilities["cibuild"]["status"])

    def test_documented_non_command_paths_do_not_satisfy_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tools = root / "tools"
            self.init_repo(root)
            tools.mkdir()
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run the full release gate with `./tools/release-notes.md --all`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            (tools / "release-notes.md").write_text("# Release notes\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["cibuild"]["status"])

    def test_stale_interpreter_wrapped_local_commands_do_not_satisfy_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run project checks with `python scripts/test.py`.\n"
                "Run the full release gate with `bash scripts/validate.sh`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])
            self.assertEqual("missing", responsibilities["cibuild"]["status"])

    def test_stale_package_manager_commands_do_not_satisfy_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `npm test`.\n"
                "Run the full validation gate with `npm run validate`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])
            self.assertEqual("missing", responsibilities["cibuild"]["status"])

    def test_stale_optioned_package_manager_commands_do_not_satisfy_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `npm --prefix frontend test`.\n"
                "Run the full validation gate with `pnpm -C frontend validate`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (frontend / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (frontend / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])
            self.assertEqual("missing", responsibilities["cibuild"]["status"])

    def test_invalid_scoped_pnpm_documented_command_is_stale_not_lifecycle_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api_dir = root / "packages" / "api"
            self.init_repo(root)
            api_dir.mkdir(parents=True)
            command = "pnpm --foreground-scripts --filter api test"
            evidence = f"README.md:{command}"
            (root / "README.md").write_text(
                "# Example\n\n"
                f"Run API tests with `{command}`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (api_dir / "package.json").write_text(
                json.dumps({"name": "api", "private": True}) + "\n"
            )
            (api_dir / "index.js").write_text("console.log('api')\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            stale_evidence = [
                item
                for finding in report["findings"]
                if finding["title"] == "documented command target missing"
                for item in finding["evidence"]
            ]
            documented_tests = report["checks"]["scripts"]["documented_commands"].get("test", [])

            self.assertIn(evidence, stale_evidence)
            self.assertNotIn(evidence, documented_tests)
            self.assertEqual("missing", matrix["."]["focused_test"]["status"])
            self.assertEqual("missing", matrix["packages/api"]["focused_test"]["status"])
            self.assertNotIn(evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(evidence, matrix["packages/api"]["focused_test"]["evidence"])

    def test_value_option_scoped_npm_documented_command_counts_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api_dir = root / "packages" / "api"
            self.init_repo(root)
            api_dir.mkdir(parents=True)
            command = "npm --loglevel warn --workspace api test"
            evidence = f"README.md:{command}"
            (root / "README.md").write_text(
                "# Example\n\n"
                f"Run API tests with `{command}`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                        "workspaces": ["packages/*"],
                    }
                )
                + "\n"
            )
            (api_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "api",
                        "private": True,
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (api_dir / "index.js").write_text("console.log('api')\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            stale_evidence = [
                item
                for finding in report["findings"]
                if finding["title"] == "documented command target missing"
                for item in finding["evidence"]
            ]
            documented_tests = report["checks"]["scripts"]["documented_commands"].get("test", [])

            self.assertNotIn(evidence, stale_evidence)
            self.assertIn(evidence, documented_tests)
            self.assertEqual("present", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn(evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(evidence, matrix["."]["focused_test"]["evidence"])

    def test_external_directory_scoped_npm_documented_command_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            api_dir = root / "packages" / "api"
            self.init_repo(root)
            api_dir.mkdir(parents=True)
            command = "npm --prefix ../missing --workspace api test"
            evidence = f"README.md:{command}"
            (root / "README.md").write_text(
                "# Example\n\n"
                f"Run API tests with `{command}`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                        "workspaces": ["packages/*"],
                    }
                )
                + "\n"
            )
            (api_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "api",
                        "private": True,
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (api_dir / "index.js").write_text("console.log('api')\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            stale_evidence = [
                item
                for finding in report["findings"]
                if finding["title"] == "documented command target missing"
                for item in finding["evidence"]
            ]
            documented_tests = report["checks"]["scripts"]["documented_commands"].get("test", [])

            self.assertIn(evidence, stale_evidence)
            self.assertNotIn(evidence, documented_tests)
            self.assertNotIn(evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(evidence, matrix["packages/api"]["focused_test"]["evidence"])

    def test_post_subcommand_npm_prefix_options_select_package_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `npm run test --prefix=frontend`.\n"
                "Run direct tests with `npm test --prefix=frontend`.\n"
                "Run the full validation gate with `npm run validate --prefix frontend`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (frontend / "package.json").write_text('{"scripts": {"test": "vitest", "validate": "vitest --run"}}\n')
            (frontend / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("frontend/package.json:test", responsibilities["test"]["candidates"])
            self.assertIn("frontend/package.json:validate", responsibilities["cibuild"]["candidates"])

    def test_post_subcommand_npm_prefix_options_still_allow_workspace_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = root / "frontend" / "packages" / "app"
            self.init_repo(root)
            app.mkdir(parents=True)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `npm test --prefix frontend --workspaces`.\n"
                "Run validation with `npm run --prefix frontend validate --workspaces`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (root / "frontend" / "package.json").write_text('{"workspaces": ["packages/*"]}\n')
            (app / "package.json").write_text(
                '{"name": "app", "scripts": {"test": "vitest", "validate": "vitest --run"}}\n'
            )
            (app / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("frontend/packages/app/package.json:test", responsibilities["test"]["candidates"])
            self.assertIn("frontend/packages/app/package.json:validate", responsibilities["cibuild"]["candidates"])

    def test_builtin_package_manager_commands_can_document_setup_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Install dependencies with `npm ci`.\n"
                "Install all dependencies with `npm install`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            (root / "package-lock.json").write_text('{"lockfileVersion": 3}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)
            self.assertIn("no CI or full validation entry point", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["bootstrap"]["status"])
            self.assertEqual("missing", responsibilities["cibuild"]["status"])
            self.assertIn("README.md:npm ci", responsibilities["bootstrap"]["candidates"])

    def test_npm_ci_without_lockfile_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nInstall dependencies with `npm ci`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_npm_workspace_ci_uses_root_lockfile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            app = root / "packages" / "app"
            self.init_repo(root)
            app.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n\nInstall dependencies with `npm ci --workspace app`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"workspaces": ["packages/*"]}\n')
            (root / "package-lock.json").write_text('{"lockfileVersion": 3}\n')
            (app / "package.json").write_text('{"name": "app", "scripts": {"test": "vitest"}}\n')
            (app / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)

    def test_npm_ci_with_prefix_without_lockfile_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text("# Example\n\nInstall dependencies with `npm --prefix frontend ci`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (frontend / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            (frontend / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_npm_install_without_package_manifest_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text("# Example\n\nInstall dependencies with `npm --prefix frontend install`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            (root / "package-lock.json").write_text('{"lockfileVersion": 3}\n')
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_npm_install_explicit_package_without_manifest_documents_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install left-pad`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)

    def test_pnpm_install_argument_without_manifest_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `pnpm -C frontend install left-pad`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_npm_install_value_option_without_manifest_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --cache .npm-cache`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_npm_install_unknown_value_option_without_manifest_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --only prod`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_npm_install_release_filter_without_manifest_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --before 2024-01-01`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_npm_install_unknown_option_without_manifest_is_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --fetch-retry-maxtimeout 60000`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"dependencies": {"left-pad": "1.3.0"}}\n')
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no setup or bootstrap script", titles)

    def test_npm_install_boolean_option_with_package_without_manifest_documents_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --legacy-peer-deps left-pad`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)

    def test_npm_install_shorthand_boolean_option_with_package_without_manifest_documents_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install -D left-pad`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)

    def test_npm_install_no_prefixed_boolean_option_with_package_without_manifest_documents_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --no-package-lock left-pad`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)

    def test_npm_install_common_boolean_option_with_package_without_manifest_documents_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --production left-pad`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)

    def test_npm_install_boolean_assignment_with_package_without_manifest_documents_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --save=false left-pad`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)

    def test_npm_install_save_bundle_with_package_without_manifest_documents_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frontend = root / "frontend"
            self.init_repo(root)
            frontend.mkdir()
            (root / "README.md").write_text(
                "# Example\n\nInstall dependencies with `npm --prefix frontend install --save-bundle left-pad`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no setup or bootstrap script", titles)

    def test_npm_workspace_commands_document_workspace_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\n"
                "Run tests with `npm run --workspace app test`.\n"
                "Run tests with `npm --workspace app test`.\n"
                "Run tests with `npm -w app run test`.\n"
                "Run tests with `npm --workspace=app run test`.\n"
                "Run tests with `npm run test --workspace app`.\n"
                "Run tests with `npm test --workspace app`.\n"
                "Install dependencies with `npm install --workspace app`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {
                    "packages/app": (
                        '{"name": "app", "scripts": {"test": "vitest"}, '
                        '"dependencies": {"left-pad": "1.3.0"}}\n'
                    ),
                },
            )

            report = self.audit_report(root)
            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("documented", responsibilities["bootstrap"]["status"])
            expected = [
                "npm run --workspace app test",
                "npm --workspace app test",
                "npm -w app run test",
                "npm --workspace=app run test",
                "npm run test --workspace app",
                "npm test --workspace app",
            ]
            for command in expected:
                self.assertIn(f"README.md:{command}", responsibilities["test"]["candidates"])
            self.assertIn("README.md:npm install --workspace app", responsibilities["bootstrap"]["candidates"])

    def test_npm_script_arguments_after_separator_do_not_select_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\n"
                "Run tests with `npm run test -- --workspace app`.\n",
                '{"workspaces": ["packages/*"], "scripts": {"test": "vitest --run"}}\n',
                {"packages/app": '{"name": "app", "scripts": {"lint": "eslint ."}}\n'},
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn(
                "README.md:npm run test -- --workspace app",
                responsibilities["test"]["candidates"],
            )

    def test_unresolved_npm_workspace_options_report_stale_documented_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\n"
                "Run tests with `npm run --workspace missing test`.\n"
                "Install dependencies with `npm install --workspace missing`.\n",
                '{"scripts": {"test": "vitest"}}\n',
                {},
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])

    def test_npm_run_without_script_does_not_document_test_responsibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `npm run --workspace app`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {"packages/app": '{"name": "app", "scripts": {"lint": "eslint ."}}\n'},
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])

    def test_npm_run_alias_without_script_does_not_document_test_responsibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `npm rum`.\n",
                '{"scripts": {"test": "vitest"}}\n',
                {},
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual(["package.json:test"], responsibilities["test"]["candidates"])

    def test_npm_multi_workspace_commands_report_stale_when_any_workspace_lacks_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\n"
                "Run tests with `npm run --workspaces test`.\n"
                "Run tests with `npm run -w app -w api test`.\n",
                '{"workspaces": ["packages/*"], "scripts": {"test": "vitest"}}\n',
                {
                    "packages/app": '{"name": "app", "scripts": {"test": "vitest"}}\n',
                    "packages/api": '{"name": "api", "scripts": {"lint": "eslint ."}}\n',
                },
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])

    def test_npm_all_workspaces_if_present_ignores_missing_workspace_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `npm run test --workspaces --if-present`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {
                    "packages/app": '{"name": "app", "scripts": {"test": "vitest"}}\n',
                    "packages/api": '{"name": "api", "scripts": {"lint": "eslint ."}}\n',
                },
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn(
                "README.md:npm run test --workspaces --if-present",
                responsibilities["test"]["candidates"],
            )

    def test_pnpm_recursive_commands_report_stale_when_workspaces_lack_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\n"
                "Run tests with `pnpm --recursive run test`.\n"
                "Run tests with `pnpm -r test`.\n"
                "Run tests with `pnpm -r --include-workspace-root test`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {
                    "packages/app": '{"name": "app", "scripts": {"lint": "eslint ."}}\n',
                    "packages/api": '{"name": "api", "scripts": {"lint": "eslint ."}}\n',
                },
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])

    def test_pnpm_recursive_include_workspace_root_command_is_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `pnpm -r --include-workspace-root test`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {
                    "packages/app": '{"name": "app", "scripts": {"lint": "eslint ."}}\n',
                    "packages/api": '{"name": "api", "scripts": {"lint": "eslint ."}}\n',
                },
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])

    def test_pnpm_recursive_commands_use_pnpm_workspace_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `pnpm --recursive run test`.\n"
                "Run tests with `pnpm -r test`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"private": true}\n')
            (root / "pnpm-workspace.yaml").write_text("packages:\n  - 'packages/*'\n")
            for package_name in ("app", "api"):
                package_dir = root / "packages" / package_name
                package_dir.mkdir(parents=True)
                (package_dir / "package.json").write_text(
                    f'{{"name": "{package_name}", "scripts": {{"test": "vitest"}}}}\n'
                )
                (package_dir / "index.js").write_text(f"console.log('{package_name}')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:pnpm --recursive run test", responsibilities["test"]["candidates"])
            self.assertIn("README.md:pnpm -r test", responsibilities["test"]["candidates"])

    def test_pnpm_recursive_commands_without_workspace_yaml_discover_package_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `pnpm -r test`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {"packages/app": '{"name": "app", "scripts": {"test": "vitest"}}\n'},
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:pnpm -r test", responsibilities["test"]["candidates"])

    def test_pnpm_recursive_commands_skip_workspaces_without_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `pnpm -r test`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"private": true}\n')
            (root / "pnpm-workspace.yaml").write_text("packages:\n  - 'packages/*'\n")
            app = root / "packages" / "app"
            app.mkdir(parents=True)
            (app / "package.json").write_text('{"name": "app", "scripts": {"test": "vitest"}}\n')
            (app / "index.js").write_text("console.log('app')\n")
            api = root / "packages" / "api"
            api.mkdir(parents=True)
            (api / "package.json").write_text('{"name": "api", "scripts": {"lint": "eslint ."}}\n')
            (api / "index.js").write_text("console.log('api')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:pnpm -r test", responsibilities["test"]["candidates"])

    def test_pnpm_workspace_yaml_negated_patterns_exclude_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `pnpm -r test`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"private": true}\n')
            (root / "pnpm-workspace.yaml").write_text(
                "packages:\n"
                "  - 'packages/*'\n"
                "  - '!packages/legacy'\n"
            )
            app = root / "packages" / "app"
            app.mkdir(parents=True)
            (app / "package.json").write_text('{"name": "app", "scripts": {"test": "vitest"}}\n')
            (app / "index.js").write_text("console.log('app')\n")
            legacy = root / "packages" / "legacy"
            legacy.mkdir(parents=True)
            (legacy / "package.json").write_text('{"name": "legacy", "scripts": {"lint": "eslint ."}}\n')
            (legacy / "index.js").write_text("console.log('legacy')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:pnpm -r test", responsibilities["test"]["candidates"])

    def test_pnpm_workspace_yaml_inline_packages_list_is_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `pnpm -r test`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"private": true}\n')
            (root / "pnpm-workspace.yaml").write_text("packages: ['packages/*']\n")
            app = root / "packages" / "app"
            app.mkdir(parents=True)
            (app / "package.json").write_text('{"name": "app", "scripts": {"test": "vitest"}}\n')
            (app / "index.js").write_text("console.log('app')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:pnpm -r test", responsibilities["test"]["candidates"])

    def test_pnpm_workspace_yaml_packages_key_allows_inline_comment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `pnpm -r test`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"private": true}\n')
            (root / "pnpm-workspace.yaml").write_text("packages: # workspace packages\n  - 'packages/*'\n")
            app = root / "packages" / "app"
            app.mkdir(parents=True)
            (app / "package.json").write_text('{"name": "app", "scripts": {"test": "vitest"}}\n')
            (app / "index.js").write_text("console.log('app')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:pnpm -r test", responsibilities["test"]["candidates"])

    def test_pnpm_workspace_yaml_inline_plain_scalars_are_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `pnpm -r test`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"private": true}\n')
            (root / "pnpm-workspace.yaml").write_text("packages: [packages/*]\n")
            app = root / "packages" / "app"
            app.mkdir(parents=True)
            (app / "package.json").write_text('{"name": "app", "scripts": {"test": "vitest"}}\n')
            (app / "index.js").write_text("console.log('app')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:pnpm -r test", responsibilities["test"]["candidates"])

    def test_pnpm_workspace_yaml_brace_globs_are_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `pnpm -r test`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"private": true}\n')
            (root / "pnpm-workspace.yaml").write_text("packages:\n  - '{apps,packages}/*'\n")
            for base, name in (("apps", "web"), ("packages", "api")):
                package_dir = root / base / name
                package_dir.mkdir(parents=True)
                (package_dir / "package.json").write_text(
                    f'{{"name": "{name}", "scripts": {{"test": "vitest"}}}}\n'
                )
                (package_dir / "index.js").write_text(f"console.log('{name}')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:pnpm -r test", responsibilities["test"]["candidates"])

    def test_npm_all_workspaces_with_all_scripts_is_not_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `npm run --workspaces test`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {
                    "packages/app": '{"name": "app", "scripts": {"test": "vitest"}}\n',
                    "packages/api": '{"name": "api", "scripts": {"test": "vitest"}}\n',
                },
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:npm run --workspaces test", responsibilities["test"]["candidates"])

    def test_npm_workspace_resolution_ignores_packages_outside_declared_workspaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `npm run --workspace app test`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {
                    "packages/web": '{"name": "web", "scripts": {"test": "vitest"}}\n',
                    "examples/app": '{"name": "app", "scripts": {"test": "vitest"}}\n',
                },
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)

    def test_invalid_npm_direct_script_alias_is_reported_as_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun the full validation gate with `npm validate`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"validate": "echo ok"}}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("package.json:validate", responsibilities["cibuild"]["candidates"])

    def test_make_no_value_options_still_validate_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `make -j test`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "Makefile").write_text("lint:\n\t@echo lint\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)

    def test_make_multiple_goals_all_validate_before_accepting_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun validation with `make test validate`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "Makefile").write_text("test:\n\t@echo test\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no CI or full validation entry point", titles)

    def test_unknown_npm_subcommand_is_reported_as_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `npm e2e`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])

    def test_unknown_npm_check_subcommand_is_reported_as_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun checks with `npm check`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])

    def test_yarn_check_is_not_treated_as_missing_package_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun checks with `yarn check`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])

    def test_bun_test_uses_builtin_runner_without_package_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `bun test`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"devDependencies": {"bun-types": "latest"}}\n')
            (root / "app.test.ts").write_text("import { test } from 'bun:test';\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertIn("README.md:bun test", responsibilities["test"]["candidates"])

    def test_yarn_workspace_command_requires_selected_workspace_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `yarn workspace app test`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {"packages/app": '{"name": "app", "scripts": {"lint": "eslint ."}}\n'},
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])

    def test_yarn_workspace_command_documents_selected_workspace_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_npm_fixture(
                root,
                "# Example\n\nRun tests with `yarn workspace app test`.\n",
                '{"workspaces": ["packages/*"]}\n',
                {"packages/app": '{"name": "app", "scripts": {"test": "vitest"}}\n'},
            )

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("README.md:yarn workspace app test", responsibilities["test"]["candidates"])
            self.assertIn("packages/app/package.json:test", responsibilities["test"]["candidates"])

    def test_direct_local_documented_command_requires_executable_bit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            scripts = root / "scripts"
            scripts.mkdir()
            (root / "README.md").write_text("# Example\n\nRun tests with `./scripts/test.sh`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            test_script = scripts / "test.sh"
            test_script.write_text("#!/usr/bin/env bash\n")
            test_script.chmod(0o644)
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertNotIn("README.md:./scripts/test.sh", responsibilities["test"]["candidates"])

    def test_standard_npm_test_aliases_are_not_reported_as_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun tests with `npm t` or `npm tst`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"test": "vitest"}}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertIn("package.json:test", responsibilities["test"]["candidates"])

    def test_standard_npm_run_aliases_are_not_reported_as_stale_documentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `npm rum test`.\n"
                "Run the full validation gate with `npm urn validate`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"test": "vitest", "validate": "vitest --run"}}\n')
            (root / "index.js").write_text("console.log('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("package.json:test", responsibilities["test"]["candidates"])
            self.assertIn("package.json:validate", responsibilities["cibuild"]["candidates"])

    def test_documented_custom_make_target_can_satisfy_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run the full release gate with `make all-checks`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "Makefile").write_text("all-checks:\n\t@echo ok\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no CI or full validation entry point", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["cibuild"]["status"])
            self.assertIn("README.md:make all-checks", responsibilities["cibuild"]["candidates"])

    def test_documented_make_commands_with_option_values_can_satisfy_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs"
            self.init_repo(root)
            docs.mkdir()
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run the full validation gate with `make -C docs html`.\n"
                "Run release validation with `make -f ci.mk validate`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (docs / "Makefile").write_text("html:\n\t@echo docs\n")
            (root / "ci.mk").write_text("validate:\n\t@echo ci\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["cibuild"]["status"])
            self.assertIn("README.md:make -C docs html", responsibilities["cibuild"]["candidates"])
            self.assertIn("README.md:make -f ci.mk validate", responsibilities["cibuild"]["candidates"])

    def test_make_default_makefile_precedence_ignores_lower_priority_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n\nRun the full validation gate with `make validate`.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "GNUmakefile").write_text("test:\n\t@echo test\n")
            (root / "Makefile").write_text("validate:\n\t@echo validate\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("documented command target missing", titles)
            self.assertIn("no CI or full validation entry point", titles)
            self.assertIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["cibuild"]["status"])
            self.assertEqual(["GNUmakefile:test"], responsibilities["test"]["candidates"])
            self.assertEqual([], responsibilities["cibuild"]["candidates"])

    def test_make_targets_with_spaces_before_colon_and_multiple_targets_are_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "Makefile").write_text("test validate :\n\t@echo ok\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("Makefile:test", responsibilities["test"]["candidates"])
            self.assertIn("Makefile:validate", responsibilities["cibuild"]["candidates"])

    def test_make_variable_assignments_with_colon_values_are_not_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "Makefile").write_text(
                "test += http://localhost:3000\n"
                "validate = foo:bar\n"
            )
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("no test command or script", titles)
            self.assertIn("no CI or full validation entry point", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("missing", responsibilities["test"]["status"])
            self.assertEqual("missing", responsibilities["cibuild"]["status"])

    def test_gnumakefile_targets_satisfy_test_and_validation_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "GNUmakefile").write_text("test:\n\t@echo test\n\nvalidate:\n\t@echo validate\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("GNUmakefile:test", responsibilities["test"]["candidates"])
            self.assertIn("GNUmakefile:validate", responsibilities["cibuild"]["candidates"])

    def test_bare_make_command_can_satisfy_documented_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run tests with `make`.\n"
                "Run the full validation gate with `make`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "Makefile").write_text("all:\n\t@echo ok\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("documented command target missing", titles)
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("documented", responsibilities["test"]["status"])
            self.assertEqual("documented", responsibilities["cibuild"]["status"])
            self.assertIn("README.md:make", responsibilities["test"]["candidates"])
            self.assertIn("README.md:make", responsibilities["cibuild"]["candidates"])

    def test_justfile_targets_satisfy_test_and_validation_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "Justfile").write_text("test:\n\tpython -m unittest\n\nvalidate:\n\tjust test\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("Justfile:test", responsibilities["test"]["candidates"])
            self.assertIn("Justfile:validate", responsibilities["cibuild"]["candidates"])

    def test_parameterized_justfile_targets_satisfy_responsibilities(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "Justfile").write_text(
                "test *args:\n\tpython -m unittest {{args}}\n\n"
                "validate target='all':\n\tjust test {{target}}\n"
            )
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("present", responsibilities["test"]["status"])
            self.assertEqual("present", responsibilities["cibuild"]["status"])
            self.assertIn("Justfile:test", responsibilities["test"]["candidates"])
            self.assertIn("Justfile:validate", responsibilities["cibuild"]["candidates"])

    def test_docs_only_repo_marks_script_responsibilities_not_applicable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text("# Example Docs\n\nStatic documentation only.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (docs / "guide.md").write_text("# Guide\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no setup or bootstrap script", titles)
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("not_applicable", responsibilities["setup"]["status"])
            self.assertEqual("not_applicable", responsibilities["test"]["status"])
            self.assertEqual("not_applicable", responsibilities["cibuild"]["status"])

    def test_domain_skills_directory_without_codex_skills_does_not_require_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            domain_skill = root / "skills" / "fireball"
            domain_skill.mkdir(parents=True)
            (root / "README.md").write_text("# Example Docs\n\nStatic documentation only.\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (domain_skill / "data.json").write_text('{"damage": 8}\n')
            self.commit_all(root)

            report = self.audit_report(root)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no CI or full validation entry point", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("not_applicable", responsibilities["test"]["status"])
            self.assertEqual("not_applicable", responsibilities["cibuild"]["status"])

    def test_detects_tracked_generated_files_in_nested_package_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / "frontend" / "dist"
            self.init_repo(root)
            generated.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "frontend" / "package.json").write_text('{"scripts": {"build": "vite build"}}\n')
            (generated / "bundle.js").write_text("console.log('built')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("generated files are tracked", titles)
            self.assertIn("frontend/dist/bundle.js", report["checks"]["hygiene"]["tracked_generated"])

    def test_detects_tracked_next_output_at_repository_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            generated = root / ".next" / "server"
            self.init_repo(root)
            generated.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "package.json").write_text('{"scripts": {"build": "next build"}}\n')
            (generated / "app.js").write_text("console.log('built')\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("generated files are tracked", titles)
            self.assertIn(".next/server/app.js", report["checks"]["hygiene"]["tracked_generated"])

    def test_source_directories_named_build_or_coverage_are_not_generated_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool_build = root / "tools" / "build"
            docs_coverage = root / "docs" / "coverage"
            self.init_repo(root)
            tool_build.mkdir(parents=True)
            docs_coverage.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            (tool_build / "release.sh").write_text("#!/usr/bin/env bash\n")
            (docs_coverage / "guide.md").write_text("# Coverage guide\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("generated files are tracked", titles)
            self.assertEqual([], report["checks"]["hygiene"]["tracked_generated"])

    def test_reference_tables_do_not_document_repo_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text(
                "# Example\n\n"
                "| Responsibility | Common name |\n"
                "|---|---|\n"
                "| Open a project console | `script/console` |\n"
                "\nIf the repo uses `npm test`, `make validate`, or `./tools/doit --all`, respect it.\n"
                "Install this reusable skill with `npx skills add example/skills`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertEqual("not_applicable", responsibilities["console"]["status"])
            self.assertEqual([], responsibilities["console"]["candidates"])
            self.assertEqual("not_applicable", responsibilities["test"]["status"])
            self.assertEqual("not_applicable", responsibilities["cibuild"]["status"])

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

    def test_detects_stale_plugin_only_skill_mirror_without_source_skills_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            stale_mirror = root / "plugins" / "codex-skills" / "skills" / "stale-skill"
            stale_mirror.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            (stale_mirror / "SKILL.md").write_text("---\nname: stale-skill\ndescription: Use when stale\n---\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertIn("skill plugin mirror drift", titles)
            packaging = report["checks"]["packaging"]
            self.assertFalse(packaging["has_skills_dir"])
            self.assertTrue(packaging["has_plugin_skill_mirror"])
            self.assertEqual(["stale-skill"], packaging["extra_skill_mirrors"])

    def test_domain_skills_directory_without_codex_skill_evidence_skips_packaging_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            domain_skill = root / "skills" / "fireball"
            domain_skill.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
            (root / "app.py").write_text("print('hello')\n")
            (domain_skill / "data.json").write_text('{"damage": 10}\n')
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("skill metadata missing", titles)
            self.assertNotIn("skill plugin mirror drift", titles)
            packaging = report["checks"]["packaging"]
            self.assertEqual([], packaging["skills"])
            self.assertEqual([], packaging["missing_agents_openai_yaml"])
            self.assertEqual([], packaging["missing_skill_mirrors"])

    def test_polyglot_monorepo_inventory_detects_boundaries(self):
        fixture = Path(__file__).resolve().parent / "fixtures" / "polyglot-monorepo"

        report = self.audit_report(fixture)

        inventory = report["checks"]["repository_inventory"]
        self.assertEqual("monorepo", inventory["classification"])
        self.assertEqual(
            ["docker", "go", "node", "python"],
            sorted(inventory["ecosystems"]),
        )
        boundaries = {item["path"]: item for item in inventory["boundaries"]}
        self.assertEqual("node-workspace-root", boundaries["."]["kind"])
        self.assertEqual("go-package", boundaries["packages/api"]["kind"])
        self.assertEqual("python-package", boundaries["packages/worker"]["kind"])
        self.assertEqual("docs-site", boundaries["docs"]["kind"])
        self.assertEqual("docker-service", boundaries["Dockerfile"]["kind"])
        self.assertIn("references/ecosystems/node-typescript.md", inventory["suggested_overlays"])
        self.assertIn("references/ecosystems/go.md", inventory["suggested_overlays"])
        self.assertIn("references/ecosystems/python.md", inventory["suggested_overlays"])
        self.assertIn("references/ecosystems/docker-services.md", inventory["suggested_overlays"])

    def test_docs_site_package_json_outside_docs_is_not_test_required_node_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            website = root / "website"
            website.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (website / "docusaurus.config.js").write_text("module.exports = {};\n")
            (website / "package.json").write_text(
                json.dumps(
                    {
                        "name": "docs-site",
                        "private": True,
                        "scripts": {
                            "build": "docusaurus build",
                            "start": "docusaurus start",
                        },
                    }
                )
                + "\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            boundaries = [
                item
                for item in report["checks"]["repository_inventory"]["boundaries"]
                if item["path"] == "website"
            ]
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertTrue(boundaries)
            self.assertEqual(1, len(boundaries))
            self.assertEqual({"docs-site"}, {item["kind"] for item in boundaries})
            self.assertEqual("single-repository", report["checks"]["repository_inventory"]["classification"])
            self.assertEqual("docs", report["checks"]["repository_inventory"]["purpose"])
            self.assertEqual(
                ["website/docusaurus.config.js", "website/package.json"],
                boundaries[0]["evidence"],
            )
            self.assertNotIn("website", [item["path"] for item in findings])

    def test_workspace_package_named_docs_without_docs_markers_requires_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            docs_package = root / "packages" / "docs"
            docs_package.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                        "workspaces": ["packages/*"],
                    }
                )
                + "\n"
            )
            (docs_package / "package.json").write_text(
                json.dumps({"name": "docs", "private": True}) + "\n"
            )
            (docs_package / "src").mkdir()
            (docs_package / "src" / "index.js").write_text("export const docs = true;\n")
            self.commit_all(root)

            report = self.audit_report(root)
            boundaries = {
                item["path"]: item
                for item in report["checks"]["repository_inventory"]["boundaries"]
            }
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("node-workspace-root", boundaries["packages/docs"]["kind"])
            self.assertNotEqual("docs-site", boundaries["packages/docs"]["kind"])
            self.assertEqual("missing", matrix["packages/docs"]["focused_test"]["status"])
            self.assertIn("packages/docs", missing_focused_paths)

    def test_nested_docs_site_readme_commands_use_docs_site_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            web = root / "packages" / "web"
            docs = web / "docs"
            docs.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (web / "package.json").write_text(json.dumps({"name": "web"}) + "\n")
            (docs / "README.md").write_text("# Docs\n\nBuild docs with `npm run build`.\n")
            (docs / "package.json").write_text(
                json.dumps(
                    {
                        "name": "web-docs",
                        "private": True,
                        "scripts": {"build": "docusaurus build"},
                    }
                )
                + "\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            stale_evidence = [
                evidence
                for finding in report["findings"]
                if finding["title"] == "documented command target missing"
                for evidence in finding["evidence"]
            ]

            self.assertEqual("present", matrix["packages/web/docs"]["build_package"]["status"])
            self.assertNotIn("packages/web/docs/README.md:npm run build", stale_evidence)

    def test_root_package_and_nested_go_package_classifies_as_monorepo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            api_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "web-app", "private": True}) + "\n"
            )
            (api_dir / "go.mod").write_text("module example.com/api\n")
            self.commit_all(root)

            report = self.audit_report(root)

            inventory = report["checks"]["repository_inventory"]
            boundaries = {item["path"]: item for item in inventory["boundaries"]}
            self.assertEqual("monorepo", inventory["classification"])
            self.assertEqual("node-workspace-root", boundaries["."]["kind"])
            self.assertEqual("go-package", boundaries["packages/api"]["kind"])

    def test_single_root_mixed_repository_remains_single_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "mixed-root", "scripts": {"test": "node index.js"}}) + "\n"
            )
            (root / "pyproject.toml").write_text("[project]\nname = \"mixed-root\"\n")
            (root / "Dockerfile").write_text("FROM python:3.12-slim\n")
            (root / "index.js").write_text("console.log('hello')\n")
            (root / "app.py").write_text("print('hello')\n")
            self.commit_all(root)

            report = self.audit_report(root)
            inventory = report["checks"]["repository_inventory"]

            self.assertEqual("single-repository", inventory["classification"])
            self.assertIn(inventory["purpose"], {"mixed", "service"})
            self.assertEqual({"docker", "node", "python"}, set(inventory["ecosystems"]))

    def test_single_root_static_site_remains_single_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example Docs\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "docusaurus.config.js").write_text("module.exports = {};\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "docs-site",
                        "private": True,
                        "scripts": {
                            "build": "docusaurus build",
                            "start": "docusaurus start",
                        },
                    }
                )
                + "\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)

            inventory = report["checks"]["repository_inventory"]
            self.assertEqual("single-repository", inventory["classification"])
            self.assertEqual("docs", inventory["purpose"])

    def test_polyglot_lifecycle_gate_matrix_scopes_gates(self):
        fixture = Path(__file__).resolve().parent / "fixtures" / "polyglot-monorepo"

        report = self.audit_report(fixture)

        matrix = {
            row["path"]: row
            for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
        }
        self.assertEqual("present", matrix["."]["focused_test"]["status"])
        self.assertEqual("present", matrix["."]["full_validation"]["status"])
        self.assertEqual("present", matrix["packages/api"]["focused_test"]["status"])
        self.assertEqual("missing", matrix["packages/api"]["setup"]["status"])
        self.assertEqual("missing", matrix["packages/api"]["full_validation"]["status"])
        self.assertEqual("present", matrix["packages/api"]["ci_coverage"]["status"])
        self.assertEqual("missing", matrix["packages/worker"]["focused_test"]["status"])
        self.assertEqual("not_applicable", matrix["docs"]["server"]["status"])
        self.assertIn("package.json:test", matrix["."]["focused_test"]["evidence"])
        self.assertIn(".github/workflows/ci.yml:go test ./...", matrix["packages/api"]["focused_test"]["evidence"])

    def test_markdown_report_includes_inventory_sections(self):
        fixture = Path(__file__).resolve().parent / "fixtures" / "polyglot-monorepo"

        result = self.run_audit(fixture)

        self.assertIn("## Repository Inventory", result.stdout)
        self.assertIn("## Lifecycle Gate Matrix", result.stdout)
        self.assertIn("packages/worker", result.stdout)
        self.assertIn("python-package", result.stdout)

    def test_nested_package_path_still_audits_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / "AGENTS.md").write_text("# Instructions\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts":{"test":"echo ok"}}\n')
            (workflows / "ci.yml").write_text("name: ci\n")
            (package_dir / "README.md").write_text("# API\n")
            (package_dir / "go.mod").write_text("module example.com/api\n")
            self.commit_all(root)

            report = self.audit_report(package_dir)

            self.assertEqual(str(root.resolve()), report["repo"])
            self.assertIn(".github/workflows/ci.yml", report["checks"]["validation"]["ci_workflows"])

    def test_nested_package_with_local_workflow_signals_still_audits_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "api"
            root_workflows = root / ".github" / "workflows"
            package_workflows = package_dir / ".github" / "workflows"
            root_workflows.mkdir(parents=True)
            package_workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / "AGENTS.md").write_text("# Instructions\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts":{"test":"echo ok"}}\n')
            (root_workflows / "ci.yml").write_text("name: root-ci\n")
            (package_dir / "README.md").write_text("# API\n")
            (package_dir / "go.mod").write_text("module example.com/api\n")
            (package_workflows / "pkg-ci.yml").write_text("name: package-ci\n")
            self.commit_all(root)

            report = self.audit_report(package_dir)

            self.assertEqual(str(root.resolve()), report["repo"])
            self.assertIn(".github/workflows/ci.yml", report["checks"]["validation"]["ci_workflows"])

    def test_nested_standalone_project_path_audits_itself_inside_larger_worktree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            project_dir = root / "third_party" / "service"
            root_workflows = root / ".github" / "workflows"
            project_workflows = project_dir / ".github" / "workflows"
            root_workflows.mkdir(parents=True)
            project_workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts":{"test":"echo ok"}}\n')
            (root_workflows / "ci.yml").write_text("name: root-ci\n")
            (project_dir / "README.md").write_text("# Service\n")
            (project_dir / "package.json").write_text('{"scripts":{"test":"echo service"}}\n')
            (project_workflows / "service-ci.yml").write_text("name: service-ci\n")
            self.commit_all(root)

            report = self.audit_report(project_dir)

            self.assertEqual(str(project_dir.resolve()), report["repo"])
            self.assertIn(".github/workflows/service-ci.yml", report["checks"]["validation"]["ci_workflows"])

    def test_nested_standalone_project_hygiene_ignores_parent_worktree_dirt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            project_dir = root / "projects" / "service"
            project_workflows = project_dir / ".github" / "workflows"
            project_workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Parent\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (project_dir / "README.md").write_text("# Service\n")
            (project_dir / "package.json").write_text('{"scripts":{"test":"echo service"}}\n')
            (project_workflows / "service-ci.yml").write_text("name: service-ci\n")
            self.commit_all(root)
            (root / "outside.txt").write_text("outside\n")
            (project_dir / "inside.txt").write_text("inside\n")

            report = self.audit_report(project_dir)
            hygiene = report["checks"]["hygiene"]
            dirty_findings = [
                finding
                for finding in report["findings"]
                if finding["title"] == "worktree has uncommitted changes"
            ]

            self.assertEqual(str(project_dir.resolve()), report["repo"])
            self.assertIn("?? inside.txt", hygiene["dirty_entries"])
            self.assertNotIn("?? ../../outside.txt", hygiene["dirty_entries"])
            self.assertEqual(["?? inside.txt"], dirty_findings[0]["evidence"])

    def test_workflow_direct_tools_count_for_matching_lifecycle_cells(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts":{"lint":"echo ok"}}\n')
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pytest\n"
                "        working-directory: packages/worker\n"
                "      - run: ruff check .\n"
                "        working-directory: packages/worker\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/worker"]["lint_format"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])
            self.assertIn(
                ".github/workflows/ci.yml:ruff check .",
                matrix["packages/worker"]["lint_format"]["evidence"],
            )

    def test_workflow_working_directory_before_run_counts_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts":{"lint":"echo ok"}}\n')
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - working-directory: packages/worker\n"
                "        run: pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])

    def test_workflow_working_directory_is_normalized_for_lifecycle_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts":{"lint":"echo ok"}}\n')
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - working-directory: ./packages/worker/\n"
                "        run: pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])

    def test_package_local_package_json_scripts_only_cover_package_lifecycle_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"private": true, "scripts": {"lint": "eslint ."}}\n')
            (package_dir / "package.json").write_text(
                '{"name": "@example/worker", "scripts": {"test": "vitest run", "build": "tsc -p tsconfig.json"}}\n'
            )
            (package_dir / "index.ts").write_text("export const worker = true;\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("missing", matrix["."]["focused_test"]["status"])
            self.assertEqual("missing", matrix["."]["build_package"]["status"])
            self.assertNotIn("packages/worker/package.json:test", matrix["."]["focused_test"]["evidence"])
            self.assertNotIn("packages/worker/package.json:build", matrix["."]["build_package"]["evidence"])
            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/worker"]["build_package"]["status"])
            self.assertIn("packages/worker/package.json:test", matrix["packages/worker"]["focused_test"]["evidence"])
            self.assertIn("packages/worker/package.json:build", matrix["packages/worker"]["build_package"]["evidence"])

    def test_invalid_make_workflow_command_does_not_credit_root_or_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            package_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (package_dir / "go.mod").write_text("module example.com/api\n")
            (package_dir / "Makefile").write_text("build:\n\tgo build ./...\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: make -C packages/api test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]
            invalid_evidence = ".github/workflows/ci.yml:make -C packages/api test"

            self.assertNotIn(invalid_evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["."]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn("packages/api", missing_focused_paths)

    def test_missing_package_makefile_workflow_command_does_not_credit_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            package_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts": {"lint": "eslint ."}}\n')
            (package_dir / "go.mod").write_text("module example.com/api\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - working-directory: packages/api\n"
                "        run: make test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]
            invalid_evidence = ".github/workflows/ci.yml:make test"

            self.assertNotIn(invalid_evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn("packages/api", missing_focused_paths)

    def test_workflow_job_defaults_run_working_directory_counts_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    defaults:\n"
                "      run:\n"
                "        working-directory: packages/worker\n"
                "    steps:\n"
                "      - run: pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])

    def test_workflow_global_defaults_run_working_directory_counts_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "defaults:\n"
                "  run:\n"
                "    working-directory: packages/worker\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])

    def test_workflow_matrix_include_run_keys_do_not_count_as_step_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"scripts":{"lint":"echo ok"}}\n')
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    strategy:\n"
                "      matrix:\n"
                "        include:\n"
                "          - name: worker\n"
                "            run: pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("missing", matrix["."]["ci_coverage"]["status"])
            self.assertEqual([], matrix["."]["ci_coverage"]["evidence"])
            self.assertEqual("missing", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual([], matrix["packages/worker"]["focused_test"]["evidence"])

    def test_workflow_parser_accepts_valid_non_two_space_indentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "    test:\n"
                "        runs-on: ubuntu-latest\n"
                "        steps:\n"
                "            - working-directory: packages/worker\n"
                "              run: pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])

    def test_docker_service_ci_coverage_matches_workflow_directory_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "Dockerfile").write_text("FROM python:3.12-slim\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  docker:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: docker build .\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["Dockerfile"]["ci_coverage"]["status"])
            self.assertIn(".github/workflows/ci.yml:docker build .", matrix["Dockerfile"]["ci_coverage"]["evidence"])

    def test_root_validation_does_not_cover_docker_service_rows_without_docker_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "test": "pnpm test",
                            "ci": "pnpm test",
                        }
                    }
                )
                + "\n"
            )
            (root / "Dockerfile").write_text("FROM python:3.12-slim\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["."]["focused_test"]["status"])
            self.assertEqual("present", matrix["."]["full_validation"]["status"])
            self.assertEqual("missing", matrix["Dockerfile"]["focused_test"]["status"])
            self.assertEqual("missing", matrix["Dockerfile"]["full_validation"]["status"])
            self.assertEqual("missing", matrix["Dockerfile"]["ci_coverage"]["status"])
            self.assertEqual([], matrix["Dockerfile"]["focused_test"]["evidence"])
            self.assertEqual([], matrix["Dockerfile"]["full_validation"]["evidence"])
            self.assertEqual([], matrix["Dockerfile"]["ci_coverage"]["evidence"])

    def test_docker_service_rows_keep_dedicated_repo_owned_docker_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "scripts": {
                            "test:docker": "docker build .",
                            "validate:docker": "docker build .",
                        }
                    }
                )
                + "\n"
            )
            (root / "Dockerfile").write_text("FROM python:3.12-slim\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["Dockerfile"]["focused_test"]["status"])
            self.assertEqual("present", matrix["Dockerfile"]["full_validation"]["status"])
            self.assertIn("package.json:test:docker", matrix["Dockerfile"]["focused_test"]["evidence"])
            self.assertIn("package.json:validate:docker", matrix["Dockerfile"]["full_validation"]["evidence"])

    def test_docker_service_rows_keep_dedicated_docker_workflow_wrappers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "Dockerfile").write_text("FROM python:3.12-slim\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  docker:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: make docker-test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["Dockerfile"]["focused_test"]["status"])
            self.assertEqual("present", matrix["Dockerfile"]["ci_coverage"]["status"])
            self.assertIn(".github/workflows/ci.yml:make docker-test", matrix["Dockerfile"]["focused_test"]["evidence"])
            self.assertIn(".github/workflows/ci.yml:make docker-test", matrix["Dockerfile"]["ci_coverage"]["evidence"])

    def test_workflow_multiline_run_block_counts_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - name: worker checks\n"
                "        working-directory: packages/worker\n"
                "        run: |\n"
                "          pytest\n"
                "          ruff check .\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/worker"]["lint_format"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])
            self.assertIn(
                ".github/workflows/ci.yml:ruff check .",
                matrix["packages/worker"]["lint_format"]["evidence"],
            )

    def test_workflow_literal_run_block_cd_scopes_following_commands_to_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - name: worker tests\n"
                "        run: |\n"
                "          cd packages/worker\n"
                "          pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_workflow_literal_run_block_nested_cd_does_not_scope_later_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - name: conditional worker tests\n"
                "        run: |\n"
                "          if false; then\n"
                "            cd packages/worker\n"
                "          fi\n"
                "          pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("missing", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual([], matrix["packages/worker"]["focused_test"]["evidence"])
            self.assertIn("packages/worker", [item["path"] for item in findings])

    def test_workflow_folded_run_block_does_not_split_into_independent_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - name: worker checks\n"
                "        working-directory: packages/worker\n"
                "        run: >\n"
                "          pytest\n"
                "          ruff check .\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual("missing", matrix["packages/worker"]["lint_format"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pytest ruff check .",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn(
                ".github/workflows/ci.yml:pytest",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertEqual([], matrix["packages/worker"]["lint_format"]["evidence"])

    def test_action_inputs_do_not_count_as_top_level_workflow_run_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - uses: example/action@v1\n"
                "        with:\n"
                "          run: pytest\n"
                "          working-directory: packages/worker\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("missing", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual([], matrix["packages/worker"]["focused_test"]["evidence"])
            self.assertIn("packages/worker", [item["path"] for item in findings])

    def test_indented_top_level_workflow_step_keys_still_count_as_run_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      -   working-directory: packages/worker\n"
                "          run: pytest\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pytest",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )

    def test_polyglot_monorepo_reports_scoped_missing_focused_test_finding(self):
        fixture = Path(__file__).resolve().parent / "fixtures" / "polyglot-monorepo"

        report = self.audit_report(fixture)

        finding = next(
            (
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
                and item["path"] == "packages/worker"
            ),
            None,
        )

        self.assertIsNotNone(finding)
        self.assertEqual("package-specific", finding["scope_type"])
        self.assertEqual("proven", finding["evidence_state"])
        self.assertIn("packages/worker", finding["evidence"])

    def test_findings_render_scope_and_evidence_state(self):
        fixture = Path(__file__).resolve().parent / "fixtures" / "polyglot-monorepo"

        result = self.run_audit(fixture)

        self.assertIn("Scope: packages/worker (package-specific)", result.stdout)
        self.assertIn("Evidence state: proven", result.stdout)

    def test_nested_fixture_manifests_do_not_create_inventory_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            fixture_package = (
                root
                / "skills"
                / "auditing-repository-health"
                / "tests"
                / "fixtures"
                / "polyglot-monorepo"
                / "packages"
                / "worker"
            )
            top_level_example = root / "examples" / "real-package"
            fixture_package.mkdir(parents=True)
            top_level_example.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (fixture_package / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (top_level_example / "package.json").write_text(json.dumps({"name": "real-package"}) + "\n")
            self.commit_all(root)

            report = self.audit_report(root)
            boundary_paths = {
                boundary["path"]
                for boundary in report["checks"]["repository_inventory"]["boundaries"]
            }
            matrix_paths = {
                row["path"]
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            missing_focused_paths = {
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            }

            self.assertIn("examples/real-package", boundary_paths)
            self.assertNotIn(
                "skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/packages/worker",
                boundary_paths,
            )
            self.assertNotIn(
                "skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/packages/worker",
                matrix_paths,
            )
            self.assertNotIn(
                "skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/packages/worker",
                missing_focused_paths,
            )

    def test_nested_fixture_package_scripts_do_not_satisfy_repo_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            fixture_package = root / "tests" / "fixtures" / "demo"
            fixture_package.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("print('hello')\n")
            (fixture_package / "package.json").write_text(
                json.dumps({"scripts": {"test": "vitest run", "ci": "vitest run && tsc"}}) + "\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            scripts = report["checks"]["scripts"]
            validation = report["checks"]["validation"]
            titles = {finding["title"] for finding in report["findings"]}

            self.assertNotIn("test", scripts["package_script_sources"])
            self.assertNotIn("ci", scripts["package_script_sources"])
            self.assertEqual("missing", scripts["responsibilities"]["test"]["status"])
            self.assertEqual("missing", scripts["responsibilities"]["cibuild"]["status"])
            self.assertFalse(validation["has_focused_tests"])
            self.assertFalse(validation["has_full_gate"])
            self.assertIn("no test command or script", titles)
            self.assertIn("no CI or full validation entry point", titles)
            self.assertIn("no reusable closeout gate", titles)

    def test_source_plugin_mirror_inventory_classification_wins_over_generic_monorepo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            skill_name = "example-skill"
            source_skill = root / "skills" / skill_name
            mirror_skill = root / "plugins" / "codex-skills" / "skills" / skill_name
            source_skill.mkdir(parents=True)
            mirror_skill.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (source_skill / "SKILL.md").write_text("# Example Skill\n")
            (mirror_skill / "SKILL.md").write_text("# Example Skill\n")
            self.commit_all(root)

            report = self.audit_report(root)

            self.assertEqual(
                "source-plugin-mirror",
                report["checks"]["repository_inventory"]["classification"],
            )

    def test_single_skill_repository_reports_skill_plugin_purpose(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            (root / "README.md").write_text("# Example Skill\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "SKILL.md").write_text("# Example Skill\n")
            self.commit_all(root)

            report = self.audit_report(root)
            inventory = report["checks"]["repository_inventory"]

            self.assertEqual("single-repository", inventory["classification"])
            self.assertEqual("skill/plugin", inventory["purpose"])

    def test_root_only_repository_lifecycle_matrix_includes_shared_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            scripts_dir = root / "scripts"
            src_dir = root / "src"
            scripts_dir.mkdir()
            src_dir.mkdir()
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (src_dir / "app.py").write_text("print('hello')\n")
            (scripts_dir / "test.sh").write_text("#!/usr/bin/env bash\npython3 src/app.py\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertIn(".", matrix)
            self.assertEqual("repository-root", matrix["."]["kind"])
            self.assertEqual("generic", matrix["."]["ecosystem"])
            self.assertEqual("root/shared", matrix["."]["scope_type"])
            self.assertEqual("present", matrix["."]["focused_test"]["status"])
            self.assertIn("scripts/test.sh", matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(".", missing_focused_paths)

    def test_package_only_monorepo_includes_root_shared_lifecycle_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            scripts_dir = root / "scripts"
            api_dir = root / "packages" / "api"
            worker_dir = root / "packages" / "worker"
            scripts_dir.mkdir()
            api_dir.mkdir(parents=True)
            worker_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (scripts_dir / "validate.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
            (api_dir / "go.mod").write_text("module example.com/api\n")
            (worker_dir / "pyproject.toml").write_text("[project]\nname = \"worker\"\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("monorepo", report["checks"]["repository_inventory"]["classification"])
            self.assertIn(".", matrix)
            self.assertEqual("repository-root", matrix["."]["kind"])
            self.assertEqual("root/shared", matrix["."]["scope_type"])
            self.assertEqual("present", matrix["."]["full_validation"]["status"])
            self.assertIn("scripts/validate.sh", matrix["."]["full_validation"]["evidence"])
            self.assertNotIn(".", missing_focused_paths)

    def test_workspace_targeted_root_ci_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                        "workspaces": ["packages/*"],
                    }
                )
                + "\n"
            )
            (package_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "worker",
                        "private": True,
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter worker test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter worker test",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_pnpm_recursive_filter_ci_credits_only_selected_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            worker_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            api_dir.mkdir(parents=True)
            worker_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                    }
                )
                + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            for package_dir, package_name in ((api_dir, "api"), (worker_dir, "worker")):
                (package_dir / "package.json").write_text(
                    json.dumps(
                        {
                            "name": package_name,
                            "private": True,
                            "scripts": {"test": "vitest run"},
                        }
                    )
                    + "\n"
                )
                (package_dir / "index.js").write_text(f"console.log('{package_name}')\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm -r --filter worker test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["ci_coverage"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm -r --filter worker test",
                matrix["packages/worker"]["ci_coverage"]["evidence"],
            )
            self.assertEqual("missing", matrix["packages/api"]["ci_coverage"]["status"])
            self.assertEqual([], matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertNotIn(
                ".github/workflows/ci.yml:pnpm -r --filter worker test",
                matrix["packages/api"]["focused_test"]["evidence"],
            )

    def test_unresolved_pnpm_filter_workflow_command_does_not_credit_root_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            api_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (api_dir / "package.json").write_text(
                json.dumps({"name": "api", "private": True}) + "\n"
            )
            (api_dir / "index.js").write_text("console.log('api')\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter ./packages/missing test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]
            invalid_evidence = ".github/workflows/ci.yml:pnpm --filter ./packages/missing test"

            self.assertNotIn(invalid_evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["."]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn("packages/api", missing_focused_paths)

    def test_unresolved_yarn_workspace_workflow_command_does_not_credit_root_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            api_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                        "workspaces": ["packages/*"],
                    }
                )
                + "\n"
            )
            (api_dir / "package.json").write_text(
                json.dumps({"name": "api", "private": True}) + "\n"
            )
            (api_dir / "index.js").write_text("console.log('api')\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: yarn workspace missing test\n"
                "      - run: yarn --silent workspace missing test\n"
                "      - run: yarn --verbose workspace missing test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]
            invalid_evidence = ".github/workflows/ci.yml:yarn workspace missing test"
            invalid_optioned_evidence = ".github/workflows/ci.yml:yarn --silent workspace missing test"
            invalid_verbose_evidence = ".github/workflows/ci.yml:yarn --verbose workspace missing test"

            self.assertNotIn(invalid_evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["."]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_optioned_evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(invalid_optioned_evidence, matrix["."]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_optioned_evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_optioned_evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_verbose_evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(invalid_verbose_evidence, matrix["."]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_verbose_evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_verbose_evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn("packages/api", missing_focused_paths)

    def test_yarn_option_value_named_workspace_keeps_root_scope_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: yarn --cache-folder workspace test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            evidence = ".github/workflows/ci.yml:yarn --cache-folder workspace test"

            self.assertEqual("present", matrix["."]["ci_coverage"]["status"])
            self.assertIn(evidence, matrix["."]["ci_coverage"]["evidence"])

    def test_unresolved_npm_workspace_after_leading_option_does_not_credit_root_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            api_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                        "workspaces": ["packages/*"],
                    }
                )
                + "\n"
            )
            (api_dir / "package.json").write_text(
                json.dumps({"name": "api", "private": True}) + "\n"
            )
            (api_dir / "index.js").write_text("console.log('api')\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: npm --foreground-scripts --workspace missing test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]
            invalid_evidence = ".github/workflows/ci.yml:npm --foreground-scripts --workspace missing test"

            self.assertNotIn(invalid_evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["."]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn("packages/api", missing_focused_paths)

    def test_pnpm_foreground_scripts_before_filter_does_not_credit_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            api_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (api_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "api",
                        "private": True,
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (api_dir / "index.js").write_text("console.log('api')\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --foreground-scripts --filter api test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            invalid_evidence = ".github/workflows/ci.yml:pnpm --foreground-scripts --filter api test"

            self.assertNotIn(invalid_evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["."]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["ci_coverage"]["status"])

    def test_npm_foreground_scripts_before_workspace_counts_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            api_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                        "workspaces": ["packages/*"],
                    }
                )
                + "\n"
            )
            (api_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "api",
                        "private": True,
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (api_dir / "index.js").write_text("console.log('api')\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: npm --foreground-scripts --workspace api test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            evidence = ".github/workflows/ci.yml:npm --foreground-scripts --workspace api test"

            self.assertEqual("present", matrix["packages/api"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/api"]["ci_coverage"]["status"])
            self.assertIn(evidence, matrix["packages/api"]["focused_test"]["evidence"])
            self.assertIn(evidence, matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertNotIn(evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(evidence, matrix["."]["ci_coverage"]["evidence"])

    def test_npm_all_workspaces_with_workspace_selector_ci_credits_only_selected_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            worker_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            api_dir.mkdir(parents=True)
            worker_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                        "workspaces": ["packages/*"],
                    }
                )
                + "\n"
            )
            for package_dir, package_name in ((api_dir, "api"), (worker_dir, "worker")):
                (package_dir / "package.json").write_text(
                    json.dumps(
                        {
                            "name": package_name,
                            "private": True,
                            "scripts": {"test": "vitest run"},
                        }
                    )
                    + "\n"
                )
                (package_dir / "index.js").write_text(f"console.log('{package_name}')\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: npm --workspaces --workspace worker test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["ci_coverage"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:npm --workspaces --workspace worker test",
                matrix["packages/worker"]["ci_coverage"]["evidence"],
            )
            self.assertEqual("missing", matrix["packages/api"]["ci_coverage"]["status"])
            self.assertEqual([], matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertNotIn(
                ".github/workflows/ci.yml:npm --workspaces --workspace worker test",
                matrix["packages/api"]["focused_test"]["evidence"],
            )

    def test_recursive_pnpm_if_present_workflow_only_credits_packages_declaring_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            has_test = root / "packages" / "has-test"
            no_test = root / "packages" / "no-test"
            workflows = root / ".github" / "workflows"
            has_test.mkdir(parents=True)
            no_test.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text('{"private": true}\n')
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (has_test / "package.json").write_text(
                '{"name": "has-test", "scripts": {"test": "vitest run"}}\n'
            )
            (has_test / "index.js").write_text("console.log('has-test')\n")
            (no_test / "package.json").write_text('{"name": "no-test", "scripts": {"lint": "eslint ."}}\n')
            (no_test / "index.js").write_text("console.log('no-test')\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm -r test --if-present\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/has-test"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm -r test --if-present",
                matrix["packages/has-test"]["focused_test"]["evidence"],
            )
            self.assertEqual("missing", matrix["packages/no-test"]["focused_test"]["status"])
            self.assertEqual([], matrix["packages/no-test"]["focused_test"]["evidence"])
            self.assertIn("packages/no-test", [item["path"] for item in findings])

    def test_pnpm_path_glob_filter_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                    }
                )
                + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (package_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "worker",
                        "private": True,
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter ./packages/* test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter ./packages/* test",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_pnpm_relation_adorned_path_glob_filter_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "workspace-root",
                        "private": True,
                    }
                )
                + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (package_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "worker",
                        "private": True,
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter ...^./packages/** test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter ...^./packages/** test",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_pnpm_leading_relation_package_filter_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (package_dir / "package.json").write_text(
                json.dumps(
                    {"name": "worker", "private": True, "scripts": {"test": "vitest run"}}
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter ...worker test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter ...worker test",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_pnpm_trailing_relation_package_filter_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (package_dir / "package.json").write_text(
                json.dumps(
                    {"name": "worker", "private": True, "scripts": {"test": "vitest run"}}
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter worker... test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter worker... test",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_pnpm_leading_relation_package_filter_counts_dependent_package_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            app_dir = root / "packages" / "app"
            worker_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            app_dir.mkdir(parents=True)
            worker_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (worker_dir / "package.json").write_text(
                json.dumps(
                    {"name": "worker", "private": True, "scripts": {"test": "vitest run"}}
                )
                + "\n"
            )
            (app_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "app",
                        "private": True,
                        "dependencies": {"worker": "workspace:*"},
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter ...worker test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/app"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter ...worker test",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter ...worker test",
                matrix["packages/app"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])
            self.assertNotIn("packages/app", [item["path"] for item in findings])

    def test_pnpm_trailing_relation_package_filter_counts_dependency_package_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            core_dir = root / "packages" / "core"
            worker_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            core_dir.mkdir(parents=True)
            worker_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (core_dir / "package.json").write_text(
                json.dumps(
                    {"name": "core", "private": True, "scripts": {"test": "vitest run"}}
                )
                + "\n"
            )
            (worker_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "worker",
                        "private": True,
                        "dependencies": {"core": "workspace:*"},
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter worker... test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/core"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter worker... test",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter worker... test",
                matrix["packages/core"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])
            self.assertNotIn("packages/core", [item["path"] for item in findings])

    def test_pnpm_trailing_relation_package_filter_counts_workspace_alias_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            core_dir = root / "packages" / "core"
            worker_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            core_dir.mkdir(parents=True)
            worker_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (core_dir / "package.json").write_text(
                json.dumps(
                    {"name": "core", "private": True, "scripts": {"test": "vitest run"}}
                )
                + "\n"
            )
            (worker_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "worker",
                        "private": True,
                        "dependencies": {"aliased-core": "workspace:core@*"},
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter worker... test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}

            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter worker... test",
                matrix["packages/core"]["focused_test"]["evidence"],
            )

    def test_pnpm_trailing_caret_relation_package_filter_excludes_base_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            core_dir = root / "packages" / "core"
            worker_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            core_dir.mkdir(parents=True)
            worker_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (root / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/*"\n')
            (core_dir / "package.json").write_text(
                json.dumps(
                    {"name": "core", "private": True, "scripts": {"test": "vitest run"}}
                )
                + "\n"
            )
            (worker_dir / "package.json").write_text(
                json.dumps(
                    {
                        "name": "worker",
                        "private": True,
                        "dependencies": {"core": "workspace:*"},
                        "scripts": {"test": "vitest run"},
                    }
                )
                + "\n"
            )
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pnpm --filter worker^... test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}

            self.assertIn(
                ".github/workflows/ci.yml:pnpm --filter worker^... test",
                matrix["packages/core"]["focused_test"]["evidence"],
            )
            self.assertNotIn(
                ".github/workflows/ci.yml:pnpm --filter worker^... test",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )

    def test_documented_go_package_command_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            api_dir.mkdir(parents=True)
            (root / "README.md").write_text(
                "# Example\n\nRun API tests with `go test ./packages/api/...`.\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n")
            (api_dir / "go.mod").write_text("module example.com/api\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("documented", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn(
                "README.md:go test ./packages/api/...",
                matrix["packages/api"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/api", [item["path"] for item in findings])

    def test_documented_cd_go_package_command_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            api_dir.mkdir(parents=True)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Run API tests:\n\n"
                "```sh\n"
                "cd packages/api\n"
                "go test ./...\n"
                "```\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n")
            (api_dir / "go.mod").write_text("module example.com/api\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("documented", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn(
                "README.md:go test ./...",
                matrix["packages/api"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/api", [item["path"] for item in findings])

    def test_package_readme_go_command_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            api_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (api_dir / "README.md").write_text(
                "# API\n\nRun focused tests with `go test ./...`.\n"
            )
            (api_dir / "go.mod").write_text("module example.com/api\n")
            (api_dir / "api.go").write_text("package api\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("documented", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn(
                "packages/api/README.md:go test ./...",
                matrix["packages/api"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/api", [item["path"] for item in findings])

    def test_repeated_documented_command_contexts_do_not_share_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            api_dir.mkdir(parents=True)
            (root / "README.md").write_text(
                "# Example\n\n"
                "Validate the root package:\n\n"
                "```sh\n"
                "make\n"
                "```\n\n"
                "Run API tests:\n\n"
                "```sh\n"
                "cd packages/api\n"
                "make\n"
                "```\n"
            )
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "Makefile").write_text("build:\n\t@echo build\n")
            (api_dir / "Makefile").write_text("test:\n\t@echo test\n")
            (api_dir / "go.mod").write_text("module example.com/api\n")
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertIn("README.md:make", responsibilities["cibuild"]["candidates"])
            self.assertIn("README.md:make", responsibilities["test"]["candidates"])
            self.assertEqual("documented", matrix["packages/api"]["focused_test"]["status"])
            self.assertIn("README.md:make", matrix["packages/api"]["focused_test"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["full_validation"]["status"])
            self.assertEqual([], matrix["packages/api"]["full_validation"]["evidence"])
            self.assertNotIn("packages/api", [item["path"] for item in findings])

    def test_workflow_folded_run_block_counts_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - name: worker checks\n"
                "        working-directory: packages/worker\n"
                "        run: >\n"
                "          pytest\n"
                "          ruff check .\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual("missing", matrix["packages/worker"]["lint_format"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pytest ruff check .",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertEqual([], matrix["packages/worker"]["lint_format"]["evidence"])

    def test_workflow_make_directory_counts_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            api_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (api_dir / "go.mod").write_text("module example.com/api\n")
            (api_dir / "Makefile").write_text("test:\n\t@go test ./...\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: make -C packages/api test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/api"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/api"]["ci_coverage"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:make -C packages/api test",
                matrix["packages/api"]["focused_test"]["evidence"],
            )
            self.assertIn(
                ".github/workflows/ci.yml:make -C packages/api test",
                matrix["packages/api"]["ci_coverage"]["evidence"],
            )
            self.assertNotIn("packages/api", [item["path"] for item in findings])

    def test_workflow_make_directory_missing_target_does_not_count_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            api_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (api_dir / "go.mod").write_text("module example.com/api\n")
            (api_dir / "Makefile").write_text("build:\n\t@go build ./...\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: make -C packages/api test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("missing", matrix["packages/api"]["focused_test"]["status"])
            self.assertEqual([], matrix["packages/api"]["focused_test"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["ci_coverage"]["status"])
            self.assertEqual([], matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertIn("packages/api", [item["path"] for item in findings])

    def test_workflow_make_working_directory_missing_target_does_not_count_for_package_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            workflows = root / ".github" / "workflows"
            api_dir.mkdir(parents=True)
            workflows.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (api_dir / "go.mod").write_text("module example.com/api\n")
            (api_dir / "Makefile").write_text("build:\n\t@go build ./...\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - working-directory: packages/api\n"
                "        run: make test\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("missing", matrix["packages/api"]["focused_test"]["status"])
            self.assertEqual([], matrix["packages/api"]["focused_test"]["evidence"])
            self.assertEqual("missing", matrix["packages/api"]["ci_coverage"]["status"])
            self.assertEqual([], matrix["packages/api"]["ci_coverage"]["evidence"])
            self.assertIn("packages/api", [item["path"] for item in findings])

    def test_root_go_test_explicit_package_paths_count_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            api_dir = root / "packages" / "api"
            worker_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            api_dir.mkdir(parents=True)
            worker_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (api_dir / "go.mod").write_text("module example.com/api\n")
            (worker_dir / "go.mod").write_text("module example.com/worker\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: go test ./packages/api/... packages/worker/...\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/api"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:go test ./packages/api/... packages/worker/...",
                matrix["packages/api"]["focused_test"]["evidence"],
            )
            self.assertIn(
                ".github/workflows/ci.yml:go test ./packages/api/... packages/worker/...",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/api", [item["path"] for item in findings])
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_root_pytest_explicit_package_path_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            tests_dir = package_dir / "tests"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            tests_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (tests_dir / "test_worker.py").write_text("def test_worker():\n    assert True\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pytest packages/worker/tests\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pytest packages/worker/tests",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_missing_pytest_workflow_path_does_not_credit_root_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (root / "package.json").write_text(
                json.dumps({"name": "workspace-root", "private": True}) + "\n"
            )
            (package_dir / "pyproject.toml").write_text(
                "[project]\nname = 'worker'\nversion = '0.1.0'\n"
            )
            (package_dir / "src").mkdir()
            (package_dir / "src" / "worker.py").write_text("VALUE = 1\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pytest packages/missing/tests\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}
            missing_focused_paths = [
                item["path"]
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]
            invalid_evidence = ".github/workflows/ci.yml:pytest packages/missing/tests"

            self.assertNotIn(invalid_evidence, matrix["."]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["."]["ci_coverage"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/worker"]["focused_test"]["evidence"])
            self.assertNotIn(invalid_evidence, matrix["packages/worker"]["ci_coverage"]["evidence"])
            self.assertEqual("missing", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn("packages/worker", missing_focused_paths)

    def test_root_pytest_node_id_path_counts_for_package_focused_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            tests_dir = package_dir / "tests"
            test_file = tests_dir / "test_worker.py"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            tests_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            test_file.write_text("def test_worker():\n    assert True\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - run: pytest packages/worker/tests/test_worker.py::test_worker\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }
            findings = [
                item
                for item in report["findings"]
                if item["title"] == "missing focused test coverage"
            ]

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:pytest packages/worker/tests/test_worker.py::test_worker",
                matrix["packages/worker"]["focused_test"]["evidence"],
            )
            self.assertNotIn("packages/worker", [item["path"] for item in findings])

    def test_workflow_folded_run_block_preserves_blank_line_command_breaks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - name: worker checks\n"
                "        working-directory: packages/worker\n"
                "        run: >\n"
                "          pytest\n"
                "\n"
                "          ruff check .\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["focused_test"]["status"])
            self.assertEqual("present", matrix["packages/worker"]["lint_format"]["status"])
            self.assertIn(".github/workflows/ci.yml:pytest", matrix["packages/worker"]["focused_test"]["evidence"])
            self.assertIn(
                ".github/workflows/ci.yml:ruff check .",
                matrix["packages/worker"]["lint_format"]["evidence"],
            )

    def test_workflow_folded_run_block_preserves_more_indented_shell_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.init_repo(root)
            package_dir = root / "packages" / "worker"
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            package_dir.mkdir(parents=True)
            (root / "README.md").write_text("# Example\n")
            (root / ".gitignore").write_text("__pycache__/\n")
            (package_dir / "pyproject.toml").write_text("[project]\nname = 'worker'\nversion = '0.1.0'\n")
            (workflows / "ci.yml").write_text(
                "name: ci\n"
                "jobs:\n"
                "  test:\n"
                "    runs-on: ubuntu-latest\n"
                "    steps:\n"
                "      - name: worker checks\n"
                "        working-directory: packages/worker\n"
                "        run: >\n"
                "          if [ -n \"$CI\" ]; then\n"
                "            ruff check .\n"
                "          fi\n"
            )
            self.commit_all(root)

            report = self.audit_report(root)
            matrix = {
                row["path"]: row
                for row in report["checks"]["lifecycle_gate_matrix"]["rows"]
            }

            self.assertEqual("present", matrix["packages/worker"]["lint_format"]["status"])
            self.assertIn(
                ".github/workflows/ci.yml:ruff check .",
                matrix["packages/worker"]["lint_format"]["evidence"],
            )

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

    def test_skill_requires_classification_before_recommendations(self):
        root = Path(__file__).resolve().parents[1]
        skill = (root / "SKILL.md").read_text()

        for phrase in [
            "Run the bundled auditor first",
            "Classify the repository before writing findings",
            "references/report-contract.md",
            "references/repo-foundation-rubric.md",
            "references/ecosystem-index.md",
            "Do not prescribe generic boilerplate",
            "Every finding must name the affected path or scope",
        ]:
            self.assertIn(phrase, skill)

    def test_skill_reference_docs_define_report_contract_and_overlays(self):
        root = Path(__file__).resolve().parents[1]
        report_contract = (root / "references" / "report-contract.md").read_text()
        foundation = (root / "references" / "repo-foundation-rubric.md").read_text()
        ecosystem_index = (root / "references" / "ecosystem-index.md").read_text()

        for heading in [
            "## Repository Classification",
            "## Topology Inventory",
            "## Lifecycle Gate Matrix",
            "## Ecosystem Assessment",
            "## Recommended Foundation",
        ]:
            self.assertIn(heading, report_contract)

        for phrase in [
            "Root health does not prove package health",
            "Responsibilities, Not Filenames",
            "Evidence Before Prescription",
            "Missing Best-Practice Files Are Usually Not Blockers",
        ]:
            self.assertIn(phrase, foundation)

        for mapping in [
            "package.json -> references/ecosystems/node-typescript.md",
            "pyproject.toml -> references/ecosystems/python.md",
            "go.mod -> references/ecosystems/go.md",
            "Cargo.toml -> references/ecosystems/rust.md",
            "Package.swift -> references/ecosystems/swift-apple.md",
            "SKILL.md -> references/ecosystems/codex-skill-plugin.md",
        ]:
            self.assertIn(mapping, ecosystem_index)

    def test_ecosystem_overlays_include_required_sections(self):
        root = Path(__file__).resolve().parents[1]
        overlays = sorted((root / "references" / "ecosystems").glob("*.md"))
        self.assertGreaterEqual(len(overlays), 10)
        required = [
            "## Detection Artifacts",
            "## Common Repo Shapes",
            "## Required Lifecycle Gates",
            "## Native Commands",
            "## CI Expectations",
            "## Common False Positives",
            "## Severity Guidance",
            "## Good Finding Examples",
            "## Bad Finding Examples",
        ]
        for path in overlays:
            text = path.read_text()
            for heading in required:
                self.assertIn(heading, text, path.name)

    def test_source_and_plugin_mirror_are_identical(self):
        repo = next(
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "scripts" / "check_skill_mirror.py").exists()
        )
        result = subprocess.run(
            ["python3", "scripts/check_skill_mirror.py", "auditing-repository-health"],
            cwd=repo,
            text=True,
            capture_output=True,
        )
        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("mirror ok: auditing-repository-health", result.stdout)


if __name__ == "__main__":
    unittest.main()
