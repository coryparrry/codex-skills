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
            (tools / "doit").write_text("#!/usr/bin/env bash\n")
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
            (tools / "doit").write_text("#!/usr/bin/env bash\n")
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
            (tools / "doit").write_text("#!/usr/bin/env bash\n")
            self.commit_all(root)

            result = self.run_audit(root, "--format", "json")
            report = json.loads(result.stdout)

            titles = {finding["title"] for finding in report["findings"]}
            self.assertNotIn("no test command or script", titles)
            self.assertNotIn("no reusable closeout gate", titles)
            responsibilities = report["checks"]["scripts"]["responsibilities"]
            self.assertIn("README.md:./tools/doit --fast", responsibilities["test"]["candidates"])
            self.assertIn("README.md:./tools/doit --all", responsibilities["cibuild"]["candidates"])

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
