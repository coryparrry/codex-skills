#!/usr/bin/env python3
"""Read-only repository health audit."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import os
import posixpath
import re
import shlex
import subprocess
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".next",
    "dist",
    "build",
    "coverage",
}

GENERATED_PATTERNS = [
    "__pycache__/*",
    "*.pyc",
    ".DS_Store",
    "node_modules/*",
    ".next/*",
    "dist/*",
    "build/*",
    "coverage/*",
    ".pytest_cache/*",
    ".mypy_cache/*",
    ".ruff_cache/*",
    "*.zip",
    "*.tar.gz",
    "*.tgz",
    "*.log",
]

NESTED_GENERATED_DIRS = {"dist", "build", "coverage", ".next"}
TEST_ASSET_PARENT_DIRS = {"test", "tests", "spec"}
TEST_ASSET_FIXTURE_DIRS = {"fixtures", "test-data", "testdata"}
TEST_ASSET_EXAMPLE_DIRS = {"examples"}
WORKSPACE_PACKAGE_CONTAINER_DIRS = {"apps", "crates", "libs", "modules", "packages", "services"}
PACKAGE_DOCUMENTATION_BOUNDARY_KINDS = {
    "docs-site",
    "go-package",
    "jvm-build",
    "node-workspace-root",
    "python-package",
    "ruby-package",
    "rust-crate",
    "swift-package",
}

RESPONSIBILITY_PATHS = {
    "bootstrap": [
        "script/bootstrap",
        "scripts/bootstrap",
        "scripts/bootstrap.sh",
        "scripts/install",
        "scripts/install.sh",
        "install.sh",
    ],
    "setup": [
        "script/setup",
        "scripts/setup",
        "scripts/setup.sh",
        "setup.sh",
    ],
    "update": [
        "script/update",
        "scripts/update",
        "scripts/update.sh",
        "update.sh",
    ],
    "server": [
        "script/server",
        "scripts/server",
        "scripts/server.sh",
        "scripts/dev",
        "scripts/dev.sh",
        "dev.sh",
    ],
    "test": [
        "script/test",
        "scripts/test",
        "scripts/test.sh",
        "scripts/test_install.sh",
        "test.sh",
    ],
    "cibuild": [
        "script/cibuild",
        "scripts/cibuild",
        "scripts/cibuild.sh",
        "scripts/ci",
        "scripts/ci.sh",
        "scripts/validate",
        "scripts/validate.sh",
        "scripts/preflight",
        "scripts/preflight.sh",
    ],
    "console": [
        "script/console",
        "scripts/console",
        "scripts/console.sh",
        "console.sh",
    ],
}

PACKAGE_SCRIPT_MAP = {
    "bootstrap": {"bootstrap", "install"},
    "setup": {"setup"},
    "update": {"update"},
    "server": {"server", "start", "dev"},
    "test": {"test", "test:unit", "test:ci"},
    "cibuild": {"ci", "cibuild", "validate", "preflight", "build"},
    "console": {"console", "repl"},
}

PACKAGE_MANAGER_DIRECT_SCRIPTS = {"build", "cibuild", "dev", "e2e", "lint", "preflight", "start", "test", "validate"}
NPM_UNSUPPORTED_DIRECT_SCRIPTS = {"check"}

PACKAGE_MANAGER_DIRECT_SCRIPT_ALIASES = {
    "npm": {"start", "test"},
    "pnpm": PACKAGE_MANAGER_DIRECT_SCRIPTS,
    "yarn": PACKAGE_MANAGER_DIRECT_SCRIPTS,
    "bun": PACKAGE_MANAGER_DIRECT_SCRIPTS - {"test"},
}

PACKAGE_MANAGER_COMMAND_ALIASES = {
    "npm": {
        "i": "install",
        "it": "install-test",
        "rum": "run",
        "t": "test",
        "tst": "test",
        "urn": "run",
    },
}

UNSUPPORTED_DIRECT_SCRIPT = "__unsupported_direct_package_script__"

PACKAGE_MANAGER_BUILTIN_COMMANDS = {
    "npm": {
        "access", "adduser", "audit", "bugs", "cache", "ci", "completion", "config", "dedupe",
        "deprecate", "diff", "dist-tag", "docs", "doctor", "edit", "exec", "explain", "explore",
        "find-dupes", "fund", "get", "help", "help-search", "init", "install", "install-ci-test",
        "install-test", "link", "ll", "login", "logout", "ls", "org", "outdated", "owner", "pack",
        "ping", "pkg", "prefix", "profile", "prune", "publish", "query", "rebuild", "repo",
        "restart", "root", "run", "sbom", "search", "set", "shrinkwrap", "star", "stars",
        "start", "stop", "team", "test", "token", "trust", "undeprecate", "uninstall",
        "unpublish", "unstar", "update", "version", "view", "whoami",
    },
    "pnpm": {
        "add", "audit", "dedupe", "deploy", "dlx", "exec", "fetch", "import", "install", "outdated",
        "pack", "publish", "update",
    },
    "yarn": {
        "add", "audit", "dedupe", "dlx", "exec", "import", "info", "init", "install", "outdated",
        "pack", "publish", "remove", "set", "up", "upgrade",
    },
    "bun": {"add", "audit", "create", "install", "outdated", "pm", "publish", "remove", "test", "update", "upgrade"},
}

PACKAGE_MANAGER_DIRECTORY_OPTIONS = {
    "npm": {"--prefix"},
    "pnpm": {"-C", "--dir"},
    "yarn": {"--cwd"},
    "bun": {"--cwd"},
}

PACKAGE_MANAGER_WORKSPACE_OPTIONS = {
    "npm": {"-w", "--workspace"},
    "pnpm": {"-F", "--filter", "--filter-prod"},
}

PACKAGE_MANAGER_ALL_WORKSPACES_OPTIONS = {
    "npm": {"--workspaces"},
    "pnpm": {"-r", "--recursive"},
}

PACKAGE_MANAGER_INCLUDE_WORKSPACE_ROOT_OPTIONS = {
    "npm": {"--include-workspace-root"},
    "pnpm": {"--include-workspace-root"},
}

PACKAGE_MANAGER_NO_VALUE_OPTIONS = {
    "--frozen-lockfile",
    "--if-present",
    "--ignore-scripts",
    "--immutable",
    "--offline",
    "--prefer-offline",
    "--silent",
    "--verbose",
}

PACKAGE_MANAGER_TOOL_NO_VALUE_OPTIONS = {
    "npm": {"--foreground-scripts"},
}

PACKAGE_MANAGER_VALUE_OPTIONS = {
    "--loglevel",
}

PACKAGE_MANAGER_INVALID_SCOPED_OPTIONS = {
    "pnpm": {"--foreground-scripts"},
}

PACKAGE_MANAGER_INSTALL_VALUE_OPTIONS = {
    "--allow-git",
    "--before",
    "--cache",
    "--cpu",
    "--install-strategy",
    "--include",
    "--libc",
    "--min-release-age",
    "--omit",
    "--only",
    "--os",
    "--registry",
    "--save-prefix",
    "--tag",
    "--userconfig",
}

PACKAGE_MANAGER_INSTALL_NO_VALUE_OPTIONS = {
    "--audit",
    "-B",
    "-D",
    "-E",
    "--fund",
    "-O",
    "-P",
    "--bin-links",
    "--dry-run",
    "--force",
    "--foreground-scripts",
    "-g",
    "--global",
    "--global-style",
    "--ignore-scripts",
    "--install-links",
    "--legacy-bundling",
    "--legacy-peer-deps",
    "--no-save",
    "--package-lock",
    "--package-lock-only",
    "--prefer-dedupe",
    "--production",
    "--save",
    "--save-bundle",
    "--save-dev",
    "--save-exact",
    "--save-optional",
    "--save-peer",
    "--save-prod",
    "--strict-peer-deps",
}

GO_TEST_VALUE_OPTIONS = {
    "-bench",
    "-benchtime",
    "-blockprofile",
    "-blockprofilerate",
    "-covermode",
    "-coverpkg",
    "-coverprofile",
    "-count",
    "-cpu",
    "-exec",
    "-gcflags",
    "-ldflags",
    "-list",
    "-memprofile",
    "-memprofilerate",
    "-mutexprofile",
    "-mutexprofilefraction",
    "-o",
    "-parallel",
    "-run",
    "-tags",
    "-timeout",
    "-trace",
    "-vet",
}

DIRECT_TEST_PATH_TOOLS = {"pytest"}

DIRECT_TEST_VALUE_OPTIONS = {
    "pytest": {
        "-c",
        "-k",
        "-m",
        "-o",
        "--basetemp",
        "--confcutdir",
        "--deselect",
        "--ignore",
        "--ignore-glob",
        "--junit-xml",
        "--junitxml",
        "--rootdir",
    },
}

PACKAGE_DEPENDENCY_FIELDS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
)

CUSTOM_COMMAND_WORDS = {
    "bootstrap": {"bootstrap", "install"},
    "setup": {"setup", "doctor"},
    "update": {"update", "upgrade", "sync"},
    "server": {"server", "serve", "start", "dev"},
    "test": {"test", "tests", "spec", "check", "checks", "verify", "prove"},
    "cibuild": {"ci", "cibuild", "validate", "validation", "preflight", "release", "gate", "all"},
    "console": {"console", "repl", "shell"},
}


@dataclass
class WorkspaceSelection:
    names: List[str]
    all_workspaces: bool = False
    include_root: bool = False

    def extend(self, other: "WorkspaceSelection") -> None:
        self.names.extend(other.names)
        self.all_workspaces = self.all_workspaces or other.all_workspaces
        self.include_root = self.include_root or other.include_root

    def enabled(self) -> bool:
        return bool(self.names) or self.all_workspaces


@dataclass(frozen=True)
class PnpmRelationSelector:
    base: str
    direction: str
    include_base: bool


@dataclass
class PackageManagerCommand:
    package_dirs: Optional[List[Path]]
    script: Optional[str]
    if_present: bool = False
    allow_missing_scripts: bool = False

EXPLICIT_TEST_WORDS = {"test", "tests", "spec"}

CI_WORKFLOW_EXTENSIONS = {".yaml", ".yml"}

SHELL_PREDICATE_COMMANDS = {"test", "[", "[["}

COMMAND_FILE_EXTENSIONS = {
    ".bash",
    ".cjs",
    ".command",
    ".fish",
    ".js",
    ".mjs",
    ".php",
    ".pl",
    ".ps1",
    ".py",
    ".rb",
    ".sh",
    ".swift",
    ".ts",
    ".zsh",
}

NON_COMMAND_FILE_SUFFIXES = {
    ".cfg",
    ".conf",
    ".disabled",
    ".example",
    ".ini",
    ".json",
    ".jsonl",
    ".lock",
    ".markdown",
    ".md",
    ".rst",
    ".sample",
    ".template",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

DOC_RESPONSIBILITY_KEYWORDS = {
    "bootstrap": ("bootstrap", "install", "dependencies", "dependency"),
    "setup": ("setup", "set up", "fresh clone", "working state", "doctor"),
    "update": ("update", "upgrade", "sync", "after pulling"),
    "server": ("server", "serve", "start", "dev", "run locally", "local app"),
    "test": ("test", "tests", "check", "checks", "verify", "prove", "spec"),
    "cibuild": ("ci", "validate", "validation", "preflight", "release gate", "full gate", "closeout"),
    "console": ("console", "repl", "shell"),
}

COMMAND_PREFIXES = (
    "./",
    "bash ",
    "sh ",
    "python ",
    "python3 ",
    "pip ",
    "pip3 ",
    "npm ",
    "pnpm ",
    "yarn ",
    "bun ",
    "npx ",
    "make ",
    "just ",
    "go ",
    "cargo ",
    "swift ",
    "bundle ",
    "rails ",
    "rake ",
    "docker ",
    "uv ",
    "pytest",
    "tox ",
    "script/",
    "scripts/",
    "bin/",
    "tools/",
)

SINGLE_WORD_COMMANDS = {"make", "pytest", "tox"}

INTERPRETER_COMMANDS = {
    "bash",
    "sh",
    "python",
    "python3",
    "ruby",
    "node",
    "bun",
}

DEPENDENCY_MANIFESTS = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "Package.swift",
    "pom.xml",
    "build.gradle",
}

CODE_EXTENSIONS = {
    ".bash",
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".m",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".swift",
    ".ts",
    ".tsx",
}

SERVER_MARKERS = {
    "Dockerfile",
    "docker-compose.yml",
    "compose.yml",
    "Procfile",
}

ECOSYSTEM_OVERLAYS = {
    "node": "references/ecosystems/node-typescript.md",
    "python": "references/ecosystems/python.md",
    "go": "references/ecosystems/go.md",
    "rust": "references/ecosystems/rust.md",
    "swift": "references/ecosystems/swift-apple.md",
    "jvm": "references/ecosystems/jvm-gradle-maven.md",
    "ruby": "references/ecosystems/ruby.md",
    "docker": "references/ecosystems/docker-services.md",
    "docs": "references/ecosystems/docs-static-sites.md",
    "codex-skill": "references/ecosystems/codex-skill-plugin.md",
    "infra": "references/ecosystems/infra-iac.md",
}

BOUNDARY_MANIFESTS = {
    "package.json": ("node-workspace-root", "node"),
    "pyproject.toml": ("python-package", "python"),
    "setup.cfg": ("python-package", "python"),
    "setup.py": ("python-package", "python"),
    "requirements.txt": ("python-package", "python"),
    "go.mod": ("go-package", "go"),
    "Cargo.toml": ("rust-crate", "rust"),
    "Package.swift": ("swift-package", "swift"),
    "settings.gradle": ("jvm-build", "jvm"),
    "settings.gradle.kts": ("jvm-build", "jvm"),
    "build.gradle": ("jvm-build", "jvm"),
    "build.gradle.kts": ("jvm-build", "jvm"),
    "pom.xml": ("jvm-build", "jvm"),
    "Gemfile": ("ruby-package", "ruby"),
    "Rakefile": ("ruby-package", "ruby"),
    "Dockerfile": ("docker-service", "docker"),
    "docker-compose.yml": ("docker-service", "docker"),
    "compose.yml": ("docker-service", "docker"),
    "SKILL.md": ("codex-skill", "codex-skill"),
    "main.tf": ("infra-iac", "infra"),
    "Chart.yaml": ("infra-iac", "infra"),
}

DOCS_SITE_FILES = {
    "mkdocs.yml",
    "docusaurus.config.js",
    "docusaurus.config.ts",
    "vitepress.config.ts",
    "netlify.toml",
}

DOCS_SITE_PACKAGE_FILES = {
    "mkdocs.yml",
    "docusaurus.config.js",
    "docusaurus.config.ts",
    "vitepress.config.ts",
}


@dataclass
class Finding:
    severity: str
    title: str
    path: str
    scope_type: str
    evidence_state: str
    evidence: List[str]
    impact: str
    fix_shape: str


DocumentedCommandDirectories = Dict[str, Dict[str, List[str]]]


class Audit:
    def __init__(self, repo: Path) -> None:
        self.requested_repo = repo.resolve()
        self.commands_run: List[Dict[str, str]] = []
        self.not_checked: List[Dict[str, str]] = []
        self.findings: List[Finding] = []
        self.documented_command_directories: DocumentedCommandDirectories = {}

    def run(self) -> Dict[str, Any]:
        root = self.find_repo_root()
        checks: Dict[str, Any] = {}
        checks["repository_shape"] = self.check_repository_shape(root)
        checks["repository_inventory"] = self.check_repository_inventory(root)
        checks["documentation"] = self.check_documentation(root)
        checks["scripts"] = self.check_scripts(root)
        checks["validation"] = self.check_validation(root, checks["scripts"])
        checks["lifecycle_gate_matrix"] = self.check_lifecycle_gate_matrix(
            root,
            checks["repository_inventory"],
            checks["scripts"],
            checks["validation"],
        )
        checks["packaging"] = self.check_packaging(root)
        checks["hygiene"] = self.check_hygiene(root)

        verdict = self.build_verdict()
        return {
            "repo": str(root),
            "verdict": verdict,
            "findings": [asdict(finding) for finding in self.findings],
            "checks": checks,
            "commands_run": self.commands_run,
            "not_checked": self.not_checked,
        }

    def find_repo_root(self) -> Path:
        result = self.git(["rev-parse", "--show-toplevel"], self.requested_repo)
        if result.returncode == 0:
            git_root = Path(result.stdout.strip()).resolve()
            if should_prefer_requested_audit_root(self.requested_repo, git_root):
                return self.requested_repo
            return git_root
        if looks_like_audit_root(self.requested_repo):
            return self.requested_repo
        self.add_not_checked("git metadata", "path is not inside a Git worktree")
        return self.requested_repo

    def add_finding(
        self,
        severity: str,
        title: str,
        evidence: Iterable[str],
        impact: str,
        fix_shape: str,
        *,
        path: str = ".",
        scope_type: str = "root/shared",
        evidence_state: str = "proven",
    ) -> None:
        evidence_list = [item for item in evidence if item]
        for finding in self.findings:
            if (
                finding.title == title
                and finding.path == path
                and finding.scope_type == scope_type
            ):
                finding.evidence.extend(item for item in evidence_list if item not in finding.evidence)
                return
        self.findings.append(
            Finding(
                severity,
                title,
                path,
                scope_type,
                evidence_state,
                evidence_list,
                impact,
                fix_shape,
            )
        )

    def add_not_checked(self, area: str, reason: str) -> None:
        item = {"area": area, "reason": reason}
        if item not in self.not_checked:
            self.not_checked.append(item)

    def git(self, args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        command = ["git", *args]
        env = os.environ.copy()
        env["GIT_OPTIONAL_LOCKS"] = "0"
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, env=env)
        self.commands_run.append(
            {
                "command": shlex.join(command),
                "result": "ok" if result.returncode == 0 else f"exit {result.returncode}",
            }
        )
        return result

    def check_repository_shape(self, root: Path) -> Dict[str, Any]:
        readmes = sorted(path.name for path in root.glob("README*") if path.is_file())
        instructions = sorted(
            str(path.relative_to(root))
            for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md")
            for path in iter_files(root, name)
        )
        docs_dir = root / "docs"
        workflows_dir = root / ".github" / "workflows"
        manifests = sorted(
            name
            for name in (
                "package.json",
                "pyproject.toml",
                "Cargo.toml",
                "go.mod",
                "Gemfile",
                "requirements.txt",
                "Package.swift",
                "Makefile",
            )
            if (root / name).exists()
        )
        shape = {
            "readmes": readmes,
            "instructions": instructions,
            "has_docs_dir": docs_dir.is_dir(),
            "has_scripts_dir": (root / "scripts").is_dir(),
            "has_script_dir": (root / "script").is_dir(),
            "has_gitignore": (root / ".gitignore").is_file(),
            "has_license": any(root.glob("LICENSE*")),
            "has_contributing": any(root.glob("CONTRIBUTING*")),
            "has_security": any(root.glob("SECURITY*")),
            "has_ci_workflows": workflows_dir.is_dir()
            and any(
                path.is_file() and path.suffix.lower() in CI_WORKFLOW_EXTENSIONS
                for path in workflows_dir.iterdir()
            ),
            "manifests": manifests,
        }

        if not readmes:
            self.add_finding(
                "P1",
                "missing README",
                ["README* not found"],
                "New contributors and agents lack the first routing surface for setup and validation.",
                "Add a concise README with purpose, setup, validation, and ownership links.",
            )
        if not shape["has_gitignore"]:
            self.add_finding(
                "P2",
                "missing gitignore",
                [".gitignore not found"],
                "Generated files and local caches are more likely to be committed.",
                "Add a repo-specific .gitignore covering dependency, build, cache, and local proof outputs.",
            )
        if not instructions:
            self.add_finding(
                "P3",
                "missing agent instructions",
                ["AGENTS.md, CLAUDE.md, and GEMINI.md not found"],
                "Repeated agent work has no repo-local operating rules.",
                "Add AGENTS.md or the repo's preferred instruction file with hard rules and validation expectations.",
            )
        if not shape["has_contributing"]:
            self.add_finding(
                "P3",
                "missing contribution guide",
                ["CONTRIBUTING* not found"],
                "Onboarding and review expectations are forced into memory or chat.",
                "Add CONTRIBUTING.md or document contribution expectations in README.",
            )
        return shape

    def check_repository_inventory(self, root: Path) -> Dict[str, Any]:
        boundaries: List[Dict[str, Any]] = []
        ecosystems: set[str] = set()

        for path in iter_files(root):
            rel = relative_path(root, path)
            if is_nested_test_asset_boundary_manifest(root, path):
                continue
            kind_and_ecosystem = inventory_boundary_kind(root, path)
            if kind_and_ecosystem is None:
                continue

            kind, ecosystem = kind_and_ecosystem
            boundary_path = path.parent if kind != "docker-service" else path
            boundary_rel = relative_path(root, boundary_path)
            boundary = {
                "path": boundary_rel,
                "kind": kind,
                "ecosystem": ecosystem,
                "scope_type": scope_type_for_path(boundary_rel),
                "evidence": [rel],
            }
            boundaries.append(boundary)
            ecosystems.add(ecosystem)

        boundaries = merge_boundaries(boundaries)
        classification = classify_repository_inventory(boundaries)
        purpose = classify_repository_purpose(boundaries)
        overlays = sorted(
            ECOSYSTEM_OVERLAYS[ecosystem]
            for ecosystem in ecosystems
            if ecosystem in ECOSYSTEM_OVERLAYS
        )
        if any(boundary["kind"] == "docs-site" for boundary in boundaries):
            overlays = sorted({*overlays, ECOSYSTEM_OVERLAYS["docs"]})

        return {
            "classification": classification,
            "purpose": purpose,
            "ecosystems": sorted(ecosystems),
            "boundaries": boundaries,
            "suggested_overlays": overlays,
        }

    def check_documentation(self, root: Path) -> Dict[str, Any]:
        markdown_files = sorted(iter_files(root, "*.md"))
        broken_links: List[str] = []
        private_markers: List[str] = []
        normalized_names: Dict[str, List[str]] = {}

        for path in markdown_files:
            rel = str(path.relative_to(root))
            if is_public_doc_path(rel):
                normalized_names.setdefault(normalize_doc_name(path.stem), []).append(rel)
            text = safe_read_text(path, limit=300_000)
            broken_links.extend(find_broken_markdown_links(root, path, text))
            for line_number, line in enumerate(text.splitlines(), start=1):
                if has_unresolved_marker(line):
                    private_markers.append(f"{rel}:{line_number}")
                    if len(private_markers) >= 25:
                        break

        duplicate_docs = sorted(
            files for files in normalized_names.values() if len(files) > 1 and files[0].startswith("docs/")
        )

        if broken_links:
            self.add_finding(
                "P2",
                "broken local Markdown link",
                broken_links[:10],
                "Docs point agents or contributors at files that are missing or moved.",
                "Fix or remove the broken local Markdown links.",
            )
        if duplicate_docs:
            self.add_finding(
                "P3",
                "duplicate-looking documentation",
                [", ".join(files) for files in duplicate_docs[:10]],
                "Near-duplicate docs make source-of-truth decisions harder.",
                "Merge or mark the canonical source document.",
            )
        if private_markers:
            self.add_finding(
                "P3",
                "public docs contain unresolved markers",
                private_markers[:10],
                "Public or onboarding docs may expose unfinished notes or stale verification prompts.",
                "Resolve the markers or move private notes out of public docs.",
            )

        docs_check = {
            "markdown_files": [str(path.relative_to(root)) for path in markdown_files],
            "broken_local_links": broken_links,
            "duplicate_doc_groups": duplicate_docs,
            "unresolved_markers": private_markers,
        }
        self.add_not_checked(
            "Markdown render or lint",
            "no repo-owned Markdown render/lint command is executed by this read-only auditor",
        )
        return docs_check

    def check_scripts(self, root: Path) -> Dict[str, Any]:
        package_scripts = read_package_scripts(root / "package.json")
        package_script_sources = read_package_script_sources(root)
        make_targets_by_file = read_root_make_targets(root)
        make_targets = flatten_target_sources(make_targets_by_file)
        just_targets = read_just_targets(root)
        (
            documented_commands,
            stale_documented_commands,
            documented_command_directories,
        ) = discover_documented_commands(
            root,
            package_scripts,
            make_targets,
            just_targets,
        )
        self.documented_command_directories = documented_command_directories
        custom_commands = discover_custom_command_files(root)
        needs = infer_responsibility_needs(root, package_scripts, make_targets, just_targets)
        responsibilities: Dict[str, Dict[str, Any]] = {}

        if stale_documented_commands:
            self.add_finding(
                "P2",
                "documented command target missing",
                stale_documented_commands[:10],
                "Docs name repo-local commands that do not exist, so the audit cannot treat them as coverage.",
                "Fix the documented command path or add the missing repo-local command.",
            )

        for responsibility, candidates in RESPONSIBILITY_PATHS.items():
            found = [path for path in candidates if (root / path).exists()]
            found.extend(custom_commands[responsibility])
            found.extend(
                source
                for script in sorted(package_script_sources)
                if script in PACKAGE_SCRIPT_MAP[responsibility]
                for source in package_script_sources[script]
            )
            found.extend(
                source
                for target in sorted(make_targets_by_file)
                if target in PACKAGE_SCRIPT_MAP[responsibility] or target == responsibility
                for source in make_targets_by_file[target]
            )
            found.extend(
                f"Justfile:{target}"
                for target in sorted(just_targets)
                if target in PACKAGE_SCRIPT_MAP[responsibility] or target == responsibility
            )
            documented = documented_commands[responsibility]
            status = classify_responsibility_status(found, documented, needs[responsibility])
            responsibilities[responsibility] = {
                "status": status,
                "candidates": sorted(set(found + documented)),
                "reason": not_applicable_reason(responsibility) if status == "not_applicable" else "",
            }

        setup_missing = responsibilities["setup"]["status"] == "missing"
        bootstrap_missing = responsibilities["bootstrap"]["status"] == "missing"
        if setup_missing and bootstrap_missing:
            self.add_finding(
                "P2",
                "no setup or bootstrap script",
                ["setup/bootstrap responsibility is missing"],
                "A fresh clone has no single repo-owned path to become workable.",
                "Add or document a setup/bootstrap equivalent such as scripts/setup.sh or script/bootstrap.",
            )
        if responsibilities["test"]["status"] == "missing":
            self.add_finding(
                "P1",
                "no test command or script",
                ["test responsibility is missing"],
                "Agents can make changes without a clear focused validation path.",
                "Add or document a test equivalent such as scripts/test.sh, script/test, "
                "package.json:test, or Makefile:test.",
            )
        if responsibilities["cibuild"]["status"] == "missing":
            self.add_finding(
                "P2",
                "no CI or full validation entry point",
                ["cibuild/ci/validate responsibility is missing"],
                "Closeout can drift into one-off command bundles that prove only part of the repo.",
                "Add or document a full local gate such as scripts/validate.sh, scripts/ci.sh, or script/cibuild.",
            )

        return {
            "responsibilities": responsibilities,
            "package_json_scripts": sorted(package_scripts),
            "package_script_sources": dict(sorted(package_script_sources.items())),
            "make_targets": sorted(make_targets),
            "just_targets": sorted(just_targets),
            "documented_commands": dict(documented_commands),
        }

    def check_validation(self, root: Path, scripts_check: Dict[str, Any]) -> Dict[str, Any]:
        workflows_dir = root / ".github" / "workflows"
        python_tests = sorted(str(path.relative_to(root)) for path in iter_files(root, "test_*.py"))
        shell_scripts = []
        if (root / "scripts").is_dir():
            shell_scripts = sorted(str(path.relative_to(root)) for path in (root / "scripts").glob("*.sh"))
        workflows = []
        if workflows_dir.is_dir():
            workflows = sorted(
                str(path.relative_to(root))
                for path in workflows_dir.glob("*")
                if path.is_file() and path.suffix.lower() in CI_WORKFLOW_EXTENSIONS
            )
        cibuild = scripts_check["responsibilities"]["cibuild"]
        validation_candidates = cibuild["candidates"]

        if cibuild["status"] == "missing" and not workflows:
            self.add_finding(
                "P2",
                "no reusable closeout gate",
                ["no cibuild/validate script or CI workflow found"],
                "Different agents will run different partial checks before calling work done.",
                "Add a repo-level validate/preflight/ci script or document the exact full gate.",
            )

        return {
            "python_tests": python_tests,
            "shell_scripts": shell_scripts,
            "ci_workflows": workflows,
            "validation_candidates": validation_candidates,
            "has_focused_tests": bool(python_tests or scripts_check["responsibilities"]["test"]["candidates"]),
            "has_full_gate": cibuild["status"] in {"present", "documented"} or bool(workflows),
        }

    def check_lifecycle_gate_matrix(
        self,
        root: Path,
        inventory: Dict[str, Any],
        scripts_check: Dict[str, Any],
        validation_check: Dict[str, Any],
    ) -> Dict[str, Any]:
        del validation_check
        rows = []
        workflow_commands = workflow_command_evidence(root)
        documented_command_directories = self.documented_command_directories
        include_root_shared = should_include_root_shared_lifecycle_boundary(
            inventory,
            scripts_check,
            workflow_commands,
        )
        for boundary in lifecycle_boundaries(inventory, include_root_shared):
            path = boundary["path"]
            scope_path = lifecycle_scope_path(boundary)
            row = {
                "path": path,
                "kind": boundary["kind"],
                "ecosystem": boundary["ecosystem"],
                "scope_type": boundary["scope_type"],
                "setup": lifecycle_cell(
                    root,
                    scope_path,
                    "setup",
                    scripts_check,
                    workflow_commands,
                    documented_command_directories,
                    boundary,
                ),
                "focused_test": lifecycle_cell(
                    root,
                    scope_path,
                    "test",
                    scripts_check,
                    workflow_commands,
                    documented_command_directories,
                    boundary,
                ),
                "full_validation": lifecycle_cell(
                    root,
                    scope_path,
                    "cibuild",
                    scripts_check,
                    workflow_commands,
                    documented_command_directories,
                    boundary,
                ),
                "lint_format": lifecycle_cell(
                    root,
                    scope_path,
                    "lint",
                    scripts_check,
                    workflow_commands,
                    documented_command_directories,
                    boundary,
                ),
                "typecheck_static": lifecycle_cell(
                    root,
                    scope_path,
                    "typecheck",
                    scripts_check,
                    workflow_commands,
                    documented_command_directories,
                    boundary,
                ),
                "build_package": lifecycle_cell(
                    root,
                    scope_path,
                    "build",
                    scripts_check,
                    workflow_commands,
                    documented_command_directories,
                    boundary,
                ),
                "server": lifecycle_server_cell(
                    root,
                    boundary,
                    scripts_check,
                    workflow_commands,
                    documented_command_directories,
                ),
                "docs_release": lifecycle_cell(
                    root,
                    scope_path,
                    "docs",
                    scripts_check,
                    workflow_commands,
                    documented_command_directories,
                    boundary,
                ),
                "ci_coverage": ci_coverage_cell(scope_path, workflow_commands, boundary),
            }
            rows.append(row)
            if expects_package_focused_tests(boundary) and row["focused_test"]["status"] == "missing":
                self.add_finding(
                    "P2",
                    "missing focused test coverage",
                    [path],
                    "Package-specific changes have no dedicated focused validation path.",
                    "Add or document a package-native focused test command or CI step for this package.",
                    path=path,
                    scope_type=boundary["scope_type"],
                    evidence_state="proven",
                )
        return {"rows": rows}

    def check_packaging(self, root: Path) -> Dict[str, Any]:
        skills_dir = root / "skills"
        mirror_dir = root / "plugins" / "codex-skills" / "skills"
        result = {
            "has_skills_dir": skills_dir.is_dir(),
            "has_plugin_skill_mirror": mirror_dir.is_dir(),
            "skills": [],
            "missing_agents_openai_yaml": [],
            "missing_skill_mirrors": [],
            "extra_skill_mirrors": [],
            "drifted_skill_mirrors": [],
        }
        source_skills = []
        if skills_dir.is_dir():
            source_skills = sorted(path.name for path in skills_dir.iterdir() if is_codex_skill_dir(path))
        mirror_skills = []
        if mirror_dir.is_dir():
            mirror_skills = sorted(path.name for path in mirror_dir.iterdir() if is_codex_skill_dir(path))
        result["skills"] = source_skills
        result["missing_agents_openai_yaml"] = [
            name for name in source_skills if not (skills_dir / name / "agents" / "openai.yaml").is_file()
        ]
        result["missing_skill_mirrors"] = [name for name in source_skills if name not in mirror_skills]
        result["extra_skill_mirrors"] = [name for name in mirror_skills if name not in source_skills]

        if mirror_dir.is_dir():
            result["drifted_skill_mirrors"] = [
                name
                for name in source_skills
                if name in mirror_skills
                and directory_fingerprint(skills_dir / name) != directory_fingerprint(mirror_dir / name)
            ]

        if result["missing_agents_openai_yaml"]:
            self.add_finding(
                "P2",
                "skill metadata missing",
                [f"skills/{name}/agents/openai.yaml" for name in result["missing_agents_openai_yaml"]],
                "Installed or browsed skills may lack the UI metadata expected by this repo.",
                "Add or regenerate agents/openai.yaml for each shipped skill.",
            )
        if result["missing_skill_mirrors"] or result["drifted_skill_mirrors"] or result["extra_skill_mirrors"]:
            evidence = [
                f"missing mirror: {name}" for name in result["missing_skill_mirrors"]
            ] + [f"drifted mirror: {name}" for name in result["drifted_skill_mirrors"]]
            evidence.extend(f"extra mirror: {name}" for name in result["extra_skill_mirrors"])
            self.add_finding(
                "P1",
                "skill plugin mirror drift",
                evidence,
                "The source skill and installable plugin package can ship different behavior.",
                "Synchronize plugins/codex-skills/skills with skills/ and add the parity check to closeout.",
            )
        return result

    def check_hygiene(self, root: Path) -> Dict[str, Any]:
        branch_result = self.git(["rev-parse", "--abbrev-ref", "HEAD"], root)
        status_result = self.git(["status", "--short", "--branch", "--untracked-files=all", "--", "."], root)
        count_result = self.git(["count-objects", "-vH"], root)
        tracked_result = self.git(["ls-files", "-z", "--", "."], root)
        ignored_result = self.git(["status", "--ignored", "--short", "--", "."], root)

        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
        status_lines = status_result.stdout.splitlines() if status_result.returncode == 0 else []
        tracked_paths = tracked_result.stdout.split("\0") if tracked_result.returncode == 0 else []
        tracked_paths = [path for path in tracked_paths if path]
        dirty_lines = [line for line in status_lines if not line.startswith("##")]
        tracked_generated = sorted(path for path in tracked_paths if is_generated_path(path, root))
        largest_files = largest_tracked_files(root, tracked_paths, limit=10)
        ignored_lines = ignored_result.stdout.splitlines() if ignored_result.returncode == 0 else []

        if dirty_lines:
            self.add_finding(
                "P1",
                "worktree has uncommitted changes",
                dirty_lines[:20],
                "Audit results and follow-on work can mix with unrelated local changes.",
                "Commit, stash, or explicitly scope the dirty files before using audit output as a closeout signal.",
            )
        if tracked_generated:
            self.add_finding(
                "P2",
                "generated files are tracked",
                tracked_generated[:20],
                "Build products or caches can create noisy diffs and stale generated state.",
                "Remove generated files from version control and update .gitignore, unless they are "
                "intentional release artifacts.",
            )
        big_files = [item for item in largest_files if item["bytes"] >= 10 * 1024 * 1024]
        if big_files:
            self.add_finding(
                "P3",
                "large tracked files",
                [f"{item['path']} ({format_bytes(item['bytes'])})" for item in big_files],
                "Large tracked files can slow clone, diff, and agent scans.",
                "Move bulky generated assets to releases or document why they belong in Git.",
            )

        self.add_not_checked(
            "remote freshness",
            "the audit does not fetch remotes or contact GitHub/network services",
        )
        self.add_not_checked(
            "dependency installation",
            "the audit does not install packages or run commands that can write dependency caches",
        )

        return {
            "branch": branch,
            "status": status_lines,
            "dirty_entries": dirty_lines,
            "git_object_summary": count_result.stdout.splitlines() if count_result.returncode == 0 else [],
            "tracked_generated": tracked_generated,
            "largest_tracked_files": largest_files,
            "ignored_entries_sample": ignored_lines[:50],
            "ignored_entries_count": len(ignored_lines),
        }

    def build_verdict(self) -> Dict[str, Any]:
        severity_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        ordered = sorted(self.findings, key=lambda finding: severity_rank.get(finding.severity, 9))
        has_p0 = any(finding.severity == "P0" for finding in self.findings)
        ready = "no" if has_p0 else "conditional" if self.findings else "yes"
        recommended = ordered[0].title if ordered else "none"
        return {
            "ready_to_proceed": ready,
            "blocking_issues": sum(1 for finding in self.findings if finding.severity in {"P0", "P1"}),
            "recommended_first_fix": recommended,
            "finding_counts": {
                severity: sum(1 for finding in self.findings if finding.severity == severity)
                for severity in ("P0", "P1", "P2", "P3")
            },
        }


def is_scannable(path: Path) -> bool:
    return not any(part in SKIP_DIRS for part in path.parts)


def looks_like_audit_root(path: Path) -> bool:
    if not path.is_dir():
        return False
    git_dir = path / ".git"
    if git_dir.is_dir() or git_dir.is_file():
        return True
    if not (path / ".github" / "workflows").is_dir():
        return False
    standalone_signals = 0
    if any((path / name).is_file() for name in ("README.md", "README")):
        standalone_signals += 1
    if any((path / name).exists() for name in (*BOUNDARY_MANIFESTS, "pnpm-workspace.yaml")):
        standalone_signals += 1
    if (path / "docs").is_dir():
        standalone_signals += 1
    if (path / "packages").is_dir():
        standalone_signals += 1
    return standalone_signals >= 2


def should_prefer_requested_audit_root(requested_repo: Path, git_root: Path) -> bool:
    if requested_repo == git_root or not looks_like_audit_root(requested_repo):
        return False
    try:
        relative_parts = requested_repo.relative_to(git_root).parts
    except ValueError:
        return False
    workspace_container_dirs = {"apps", "crates", "libs", "modules", "packages", "services"}
    return not relative_parts or relative_parts[0] not in workspace_container_dirs


def iter_files(root: Path, pattern: str = "*") -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        current_path = Path(current)
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                yield current_path / name


def relative_path(root: Path, path: Path) -> str:
    rel = str(path.relative_to(root))
    return "." if rel == "." else rel


def is_nested_test_asset_boundary_manifest(root: Path, path: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    for index, part in enumerate(parts[:-1]):
        if part in TEST_ASSET_FIXTURE_DIRS:
            return index == 0 or any(parent in TEST_ASSET_PARENT_DIRS for parent in parts[:index])
        if part in TEST_ASSET_EXAMPLE_DIRS and any(parent in TEST_ASSET_PARENT_DIRS for parent in parts[:index]):
            return True
    return False


def inventory_boundary_kind(root: Path, path: Path) -> Optional[Tuple[str, str]]:
    if path.name == "package.json" and docs_site_package_manifest(root, path):
        return ("docs-site", "node")
    kind_and_ecosystem = BOUNDARY_MANIFESTS.get(path.name)
    if kind_and_ecosystem is not None:
        return kind_and_ecosystem
    if path.name in DOCS_SITE_FILES:
        return ("docs-site", "docs")
    return None


def docs_site_package_manifest(root: Path, path: Path) -> bool:
    if any((path.parent / name).is_file() for name in DOCS_SITE_PACKAGE_FILES):
        return True
    try:
        rel_parent = path.parent.relative_to(root)
    except ValueError:
        return False
    if not rel_parent.parts:
        return False
    return path.parent.name == "docs" and path.parent.parent.name not in WORKSPACE_PACKAGE_CONTAINER_DIRS


def merge_boundaries(boundaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_key: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for boundary in boundaries:
        key = boundary_merge_key(boundary)
        existing = by_key.setdefault(
            key,
            {
                "path": boundary["path"],
                "kind": boundary["kind"],
                "ecosystem": boundary["ecosystem"],
                "scope_type": boundary["scope_type"],
                "evidence": [],
            },
        )
        existing["evidence"].extend(boundary["evidence"])
        existing["ecosystem"] = merge_boundary_ecosystem(existing, boundary)
    merged = []
    for item in by_key.values():
        item["evidence"] = sorted(set(item["evidence"]))
        merged.append(item)
    return sorted(merged, key=lambda item: (item["path"], item["kind"]))


def boundary_merge_key(boundary: Dict[str, Any]) -> Tuple[str, str, str]:
    if boundary["kind"] == "docs-site":
        return (boundary["path"], boundary["kind"], "docs-site")
    return (boundary["path"], boundary["kind"], boundary["ecosystem"])


def merge_boundary_ecosystem(existing: Dict[str, Any], boundary: Dict[str, Any]) -> str:
    if existing["kind"] == "docs-site":
        ecosystems = {existing["ecosystem"], boundary["ecosystem"]}
        if "node" in ecosystems:
            return "node"
    return existing["ecosystem"]


def classify_repository_inventory(boundaries: List[Dict[str, Any]]) -> str:
    if has_source_plugin_mirror(boundaries):
        return "source-plugin-mirror"
    boundary_roots = {
        classification_boundary_scope(boundary)
        for boundary in boundaries
        if counts_toward_repository_classification(boundary)
    }
    if len(boundary_roots) >= 2:
        return "monorepo"
    return "single-repository"


def counts_toward_repository_classification(boundary: Dict[str, Any]) -> bool:
    return boundary["path"] != "Dockerfile"


def classification_boundary_scope(boundary: Dict[str, Any]) -> str:
    if boundary["kind"] != "docker-service":
        return boundary["path"]
    parent = posixpath.dirname(boundary["path"])
    return "." if parent in {"", "."} else parent


def has_source_plugin_mirror(boundaries: List[Dict[str, Any]]) -> bool:
    source_skills = {
        posixpath.basename(boundary["path"])
        for boundary in boundaries
        if boundary["kind"] == "codex-skill" and boundary["path"].startswith("skills/")
    }
    mirror_skills = {
        posixpath.basename(boundary["path"])
        for boundary in boundaries
        if boundary["kind"] == "codex-skill"
        and boundary["path"].startswith("plugins/codex-skills/skills/")
    }
    return bool(source_skills & mirror_skills)


def scope_type_for_path(path: str) -> str:
    return "root/shared" if path == "." else "package-specific"


def classify_repository_purpose(boundaries: List[Dict[str, Any]]) -> str:
    kinds = {boundary["kind"] for boundary in boundaries}
    if "codex-skill" in kinds:
        return "skill/plugin"
    if kinds and kinds <= {"docs-site"}:
        return "docs"
    if "docker-service" in kinds:
        return "service"
    package_kinds = {
        "go-package",
        "jvm-build",
        "node-workspace-root",
        "python-package",
        "ruby-package",
        "rust-crate",
        "swift-package",
    }
    if kinds & package_kinds:
        return "mixed" if len(kinds) > 1 else "library"
    if "infra-iac" in kinds:
        return "infra"
    return "mixed"


def expects_package_focused_tests(boundary: Dict[str, Any]) -> bool:
    return boundary["path"] != "." and boundary["kind"] not in {
        "docker-service",
        "docs-site",
        "infra-iac",
    }


def lifecycle_boundaries(
    inventory: Dict[str, Any],
    include_root_shared: bool = False,
) -> List[Dict[str, Any]]:
    boundaries = list(inventory["boundaries"])
    if include_root_shared and not any(boundary["path"] == "." for boundary in boundaries):
        boundaries.insert(0, root_shared_lifecycle_boundary())
    if boundaries:
        return boundaries
    return [root_shared_lifecycle_boundary()]


def root_shared_lifecycle_boundary() -> Dict[str, Any]:
    return {
        "path": ".",
        "kind": "repository-root",
        "ecosystem": "generic",
        "scope_type": "root/shared",
        "evidence": [],
    }


def should_include_root_shared_lifecycle_boundary(
    inventory: Dict[str, Any],
    scripts_check: Dict[str, Any],
    workflow_commands: Dict[str, List[str]],
) -> bool:
    boundaries = inventory["boundaries"]
    if any(boundary["path"] == "." for boundary in boundaries):
        return False
    if inventory["classification"] in {"monorepo", "source-plugin-mirror"}:
        return True
    if workflow_commands.get("."):
        return True
    return scripts_check_has_root_owned_lifecycle_candidate(scripts_check)


def scripts_check_has_root_owned_lifecycle_candidate(scripts_check: Dict[str, Any]) -> bool:
    documented_candidates = {
        candidate
        for candidates in scripts_check.get("documented_commands", {}).values()
        for candidate in candidates
    }
    for responsibility_info in scripts_check.get("responsibilities", {}).values():
        for candidate in responsibility_info.get("candidates", []):
            if candidate in documented_candidates:
                continue
            if lifecycle_candidate_scope_path(candidate) == ".":
                return True
    return False


def safe_read_text(path: Path, limit: int = 100_000) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except OSError:
        return ""


def read_package_scripts(path: Path) -> Dict[str, str]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    scripts = data.get("scripts", {})
    return scripts if isinstance(scripts, dict) else {}


def read_package_script_sources(root: Path) -> Dict[str, List[str]]:
    sources: Dict[str, List[str]] = defaultdict(list)
    for path in iter_files(root, "package.json"):
        if is_nested_test_asset_boundary_manifest(root, path):
            continue
        scripts = read_package_scripts(path)
        if not scripts:
            continue
        rel = str(path.relative_to(root))
        for script in sorted(scripts):
            sources[script].append(f"{rel}:{script}")
    return sources


def read_root_make_targets(root: Path) -> Dict[str, List[str]]:
    sources: Dict[str, List[str]] = defaultdict(list)
    path = default_makefile(root)
    for target in read_make_targets(path):
        sources[target].append(f"{path.name}:{target}")
    return sources


def default_makefile(directory: Path) -> Path:
    for name in ("GNUmakefile", "makefile", "Makefile"):
        path = exact_child_file(directory, name)
        if path is not None:
            return path
    return directory / "Makefile"


def exact_child_file(directory: Path, name: str) -> Optional[Path]:
    if not directory.is_dir():
        return None
    try:
        for child in directory.iterdir():
            if child.name == name and child.is_file():
                return child
    except OSError:
        return None
    return None


def flatten_target_sources(target_sources: Dict[str, List[str]]) -> List[str]:
    return sorted(target_sources)


def read_make_targets(path: Path) -> List[str]:
    if not path.is_file():
        return []
    targets: List[str] = []
    for line in safe_read_text(path).splitlines():
        if not line or line[:1].isspace() or line.lstrip().startswith("#"):
            continue
        target_list, separator, remainder = line.partition(":")
        if not separator or make_assignment_before_colon(line) or remainder.lstrip().startswith("="):
            continue
        for target in target_list.split():
            if re.match(r"^[A-Za-z0-9_.-]+$", target) and not target.startswith("."):
                targets.append(target)
    return targets


def make_assignment_before_colon(line: str) -> bool:
    colon_index = line.find(":")
    if colon_index == -1:
        return False
    assignment_indexes = [line.find(operator) for operator in ("+=", "?=", "!=", "=")]
    return any(0 <= index < colon_index for index in assignment_indexes)


def read_just_targets(root: Path) -> List[str]:
    for name in ("justfile", "Justfile", ".justfile"):
        path = root / name
        if path.is_file():
            return read_colon_targets(path)
    return []


def read_colon_targets(path: Path) -> List[str]:
    targets: List[str] = []
    for line in safe_read_text(path).splitlines():
        stripped = line.strip()
        if not stripped or line[:1].isspace() or stripped.startswith("#") or ":=" in stripped:
            continue
        prefix = stripped.split(":", 1)[0].strip()
        name = prefix.split()[0] if prefix else ""
        if re.match(r"^[A-Za-z0-9_.-]+$", name) and not name.startswith("."):
            targets.append(name)
    return targets


def discover_custom_command_files(root: Path) -> Dict[str, List[str]]:
    commands: Dict[str, List[str]] = defaultdict(list)
    for directory in ("script", "scripts", "bin", "tools"):
        base = root / directory
        if not base.is_dir():
            continue
        for path in iter_files(base):
            if not path.is_file() or not is_command_file(path):
                continue
            rel = str(path.relative_to(root))
            for responsibility in classify_command_name(path.name):
                commands[responsibility].append(rel)
    return commands


def classify_command_name(name: str) -> List[str]:
    words = set(re.split(r"[^a-z0-9]+", name.lower()))
    words.discard("")
    matches = []
    for responsibility, markers in CUSTOM_COMMAND_WORDS.items():
        if words & markers:
            matches.append(responsibility)
    if words & EXPLICIT_TEST_WORDS:
        return [responsibility for responsibility in matches if responsibility == "test"]
    return matches


def is_command_file(path: Path) -> bool:
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if not suffixes:
        return True
    if suffixes[-1] in NON_COMMAND_FILE_SUFFIXES:
        return False
    return suffixes[-1] in COMMAND_FILE_EXTENSIONS


def discover_documented_commands(
    root: Path,
    package_scripts: Dict[str, str],
    make_targets: List[str],
    just_targets: List[str],
) -> Tuple[Dict[str, List[str]], List[str], DocumentedCommandDirectories]:
    documented: Dict[str, List[str]] = defaultdict(list)
    documented_command_directories: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    stale: List[str] = []
    package_doc_boundaries = package_documentation_boundaries(root)
    for path in documented_command_files(root, package_doc_boundaries):
        rel = str(path.relative_to(root))
        default_command_base = documented_command_file_base(root, path, package_doc_boundaries)
        in_fence = False
        fence_context = ""
        fence_command_base = default_command_base
        previous_text = ""
        for line in safe_read_text(path, limit=300_000).splitlines():
            stripped = line.strip()
            if stripped.startswith(("```", "~~~")):
                in_fence = not in_fence
                fence_context = previous_text if in_fence else ""
                fence_command_base = default_command_base
                continue
            if in_fence:
                if is_fenced_reference_context(fence_context):
                    continue
                command = stripped.lstrip("$ ").strip()
                is_split_chain = len(split_simple_shell_chain(command)) > 1
                fence_command_base, command_records = documented_shell_command_records(root, fence_command_base, command)
                for command_base, recorded_command in command_records:
                    if not looks_like_command(recorded_command):
                        continue
                    command_context = documented_command_segment_context(
                        fence_context,
                        recorded_command,
                        is_split_chain,
                    )
                    record_documented_command(
                        root,
                        command_base,
                        documented,
                        stale,
                        documented_command_directories,
                        rel,
                        command_context,
                        recorded_command,
                        package_scripts,
                        make_targets,
                        just_targets,
                    )
                continue
            if is_reference_command_line(line):
                if stripped:
                    previous_text = stripped
                continue
            inline_records: List[Tuple[Path, str, str, bool]] = []
            for command, context in extract_inline_command_contexts(line):
                is_split_chain = len(split_simple_shell_chain(command)) > 1
                _, command_records = documented_shell_command_records(root, default_command_base, command)
                for command_base, recorded_command in command_records:
                    if looks_like_command(recorded_command):
                        inline_records.append((command_base, recorded_command, context, is_split_chain))
            if not inline_records:
                if stripped:
                    previous_text = stripped
                continue
            for command_base, command, context, is_split_chain in inline_records:
                command_context = documented_command_segment_context(context, command, is_split_chain)
                record_documented_command(
                    root,
                    command_base,
                    documented,
                    stale,
                    documented_command_directories,
                    rel,
                    command_context,
                    command,
                    package_scripts,
                    make_targets,
                    just_targets,
                )
            if stripped:
                previous_text = stripped
    return documented, stale, {
        evidence: dict(by_responsibility)
        for evidence, by_responsibility in documented_command_directories.items()
    }


def documented_command_files(root: Path, package_doc_boundaries: List[Path]) -> Iterable[Path]:
    root_prefixes = ("README", "CONTRIBUTING", "DEVELOPMENT", "SETUP", "INSTALL")
    root_instruction_docs = {"AGENTS.MD", "CLAUDE.MD", "GEMINI.MD"}
    nested_prefixes = (
        "README", "CONTRIBUTING", "DEVELOPMENT", "SETUP", "INSTALL", "INSTALLATION", "TEST", "USAGE",
        "VALIDATION",
    )
    for path in iter_files(root, "*.md"):
        rel = path.relative_to(root)
        upper_name = path.name.upper()
        if len(rel.parts) == 1 and (upper_name.startswith(root_prefixes) or upper_name in root_instruction_docs):
            yield path
            continue
        if rel.parts[0] == "docs" and upper_name.startswith(nested_prefixes):
            yield path
            continue
        if package_documented_command_file(root, path, package_doc_boundaries, nested_prefixes):
            yield path


def package_documentation_boundaries(root: Path) -> List[Path]:
    boundaries = []
    for path in iter_files(root):
        kind_and_ecosystem = inventory_boundary_kind(root, path)
        if kind_and_ecosystem is None or is_nested_test_asset_boundary_manifest(root, path):
            continue
        kind, _ = kind_and_ecosystem
        if kind not in PACKAGE_DOCUMENTATION_BOUNDARY_KINDS or path.parent == root:
            continue
        boundaries.append(path.parent)
    return sorted(unique_paths(boundaries), key=lambda item: len(item.relative_to(root).parts), reverse=True)


def package_documented_command_file(
    root: Path,
    path: Path,
    package_doc_boundaries: List[Path],
    nested_prefixes: Tuple[str, ...],
) -> bool:
    if not path.is_file() or path.suffix.lower() != ".md":
        return False
    if not path.name.upper().startswith(nested_prefixes):
        return False
    return documented_command_file_base(root, path, package_doc_boundaries) != root


def documented_command_file_base(root: Path, path: Path, package_doc_boundaries: List[Path]) -> Path:
    resolved_path = path.resolve()
    for boundary in package_doc_boundaries:
        try:
            resolved_path.relative_to(boundary.resolve())
        except ValueError:
            continue
        return boundary
    return root


def public_markdown_files(root: Path) -> Iterable[Path]:
    for path in iter_files(root, "*.md"):
        if is_public_doc_path(str(path.relative_to(root))):
            yield path


def extract_inline_commands(line: str) -> List[str]:
    return [match.strip().lstrip("$ ").strip() for match in re.findall(r"`([^`\n]+)`", line)]


def extract_inline_command_contexts(line: str) -> List[Tuple[str, str]]:
    matches = list(re.finditer(r"`([^`\n]+)`", line))
    contexts: List[Tuple[str, str]] = []
    for match in matches:
        command = match.group(1).strip().lstrip("$ ").strip()
        context_start = max(line.rfind(separator, 0, match.start()) for separator in (";", ".", "!", "?")) + 1
        next_separators = [
            position
            for separator in (";", ".", "!", "?")
            if (position := line.find(separator, match.end())) != -1
        ]
        context_end = min(next_separators) + 1 if next_separators else len(line)
        contexts.append((command, line[context_start:context_end].strip()))
    return contexts


def record_documented_command(
    root: Path,
    command_base: Path,
    documented: Dict[str, List[str]],
    stale: List[str],
    documented_command_directories: DocumentedCommandDirectories,
    rel: str,
    context: str,
    command: str,
    package_scripts: Dict[str, str],
    make_targets: List[str],
    just_targets: List[str],
) -> None:
    responsibilities = classify_documented_command(context, command)
    if not responsibilities and is_generic_reference_context(context):
        return
    if package_manager_run_without_script(command):
        return
    if documented_command_target_missing(root, command_base, command, package_scripts, make_targets, just_targets):
        stale.append(f"{rel}:{command}")
        return
    evidence = f"{rel}:{command}"
    command_directory = documented_command_directory(root, command_base)
    for responsibility in responsibilities:
        documented[responsibility].append(evidence)
        directories = documented_command_directories.setdefault(evidence, {}).setdefault(responsibility, [])
        if command_directory not in directories:
            directories.append(command_directory)


def documented_command_directory(root: Path, command_base: Path) -> str:
    try:
        return relative_path(root, command_base)
    except ValueError:
        return "."


def is_reference_command_line(line: str) -> bool:
    stripped = line.lstrip()
    if stripped.startswith("|"):
        return True
    lower = stripped.lower()
    reference_phrases = (
        "if the repo uses",
        "if a repo uses",
        "a repo might use",
        "repo might use",
        "such as",
        "common script",
        "common name",
        "install this reusable skill",
        "install the skill",
        "marketplace install",
        "npx skills add",
    )
    return any(phrase in lower for phrase in reference_phrases)


def is_fenced_reference_context(line: str) -> bool:
    stripped = line.lstrip()
    if stripped.startswith("|"):
        return True
    lower = stripped.lower()
    reference_phrases = (
        "if the repo uses",
        "if a repo uses",
        "a repo might use",
        "repo might use",
        "such as",
        "common script",
        "common name",
        "install this reusable skill",
        "install the skill",
        "marketplace install",
        "npx skills add",
    )
    return any(phrase in lower for phrase in reference_phrases)


def is_generic_reference_context(line: str) -> bool:
    return line.lstrip().lower().startswith("for example")


def command_without_leading_env_assignments(command: str) -> str:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    while tokens and is_env_assignment(tokens[0]):
        tokens = tokens[1:]
    return shlex.join(tokens) if tokens else ""


def is_env_assignment(token: str) -> bool:
    return re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", token) is not None


def looks_like_command(command: str) -> bool:
    command = command_without_leading_env_assignments(command).strip()
    lower = command.lower()
    if "codex_home" in lower or "$home/.codex" in lower:
        return False
    if not command or " " not in command and "/" not in command and lower not in SINGLE_WORD_COMMANDS:
        return False
    return lower in SINGLE_WORD_COMMANDS or lower.startswith(COMMAND_PREFIXES)


def command_changed_directory(root: Path, command_base: Path, command: str) -> Optional[Path]:
    target = simple_cd_command_target(command)
    if target is None or not target:
        return None
    directory = resolve_repo_path(root, command_base, target)
    if directory is None or not directory.is_dir():
        return None
    return directory


def simple_cd_command_target(command: str) -> Optional[str]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens or tokens[0] != "cd":
        return None
    if len(tokens) != 2:
        return ""
    return tokens[1]


def documented_shell_command_records(
    root: Path,
    command_base: Optional[Path],
    command: str,
) -> Tuple[Optional[Path], List[Tuple[Path, str]]]:
    parts = split_simple_shell_chain(command)
    current_base = command_base
    records: List[Tuple[Path, str]] = []
    for part in parts:
        if current_base is None:
            break
        changed_directory = command_changed_directory(root, current_base, part)
        if changed_directory is not None:
            current_base = changed_directory
            continue
        if simple_cd_command_target(part) is not None:
            current_base = None
            break
        records.append((current_base, part))
    return current_base, records


def split_simple_shell_chain(command: str) -> List[str]:
    parts: List[str] = []
    current: List[str] = []
    quote = ""
    escaped = False
    index = 0
    while index < len(command):
        char = command[index]
        if escaped:
            current.append(char)
            escaped = False
            index += 1
            continue
        if char == "\\":
            current.append(char)
            escaped = True
            index += 1
            continue
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            index += 1
            continue
        if char in {"'", '"'}:
            current.append(char)
            quote = char
            index += 1
            continue
        if command.startswith("&&", index):
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            index += 2
            continue
        if char == ";":
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            index += 1
            continue
        if char in {"|", "<", ">", "(", ")"}:
            stripped = command.strip()
            return [stripped] if stripped else []
        current.append(char)
        index += 1
    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts or [command.strip()]


def documented_command_target_missing(
    root: Path,
    command_base: Path,
    command: str,
    package_scripts: Dict[str, str],
    make_targets: List[str],
    just_targets: List[str],
) -> bool:
    if documented_package_target_missing(root, command_base, command, package_scripts, make_targets, just_targets):
        return True
    target = local_command_target(command)
    if target is None:
        return False
    direct_target = direct_local_command_target(command)
    if target.startswith("./"):
        path = resolve_repo_path(root, command_base, target[2:])
        if path is None:
            return True
        return not documented_local_command_target_exists(path, direct_target == target)
    if target.startswith(("script/", "scripts/", "bin/", "tools/")):
        path = resolve_repo_path(root, command_base, target)
        if path is None:
            return True
        return not documented_local_command_target_exists(path, direct_target == target)
    return False


def documented_local_command_target_exists(path: Path, requires_executable: bool) -> bool:
    if not path.exists() or not is_command_file(path):
        return False
    if requires_executable and not os.access(path, os.X_OK):
        return False
    return True


def documented_package_target_missing(
    root: Path,
    command_base: Path,
    command: str,
    package_scripts: Dict[str, str],
    make_targets: List[str],
    just_targets: List[str],
) -> bool:
    command = command_without_leading_env_assignments(command)
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return False
    tokens = normalize_pip_command_tokens(tokens)
    tool = tokens[0]
    if tool in {"npm", "pnpm", "yarn", "bun"}:
        return package_manager_target_missing(root, command_base, tokens, package_scripts)
    if tool in {"pip", "pip3"}:
        return pip_install_target_missing(root, command_base, tokens)
    if tool == "make":
        return make_command_target_missing(root, command_base, tokens[1:], make_targets)
    if tool == "just":
        target = first_non_option(tokens[1:])
        if target is None:
            return not any((command_base / name).is_file() for name in ("justfile", "Justfile", ".justfile"))
        available_targets = just_targets if command_base == root else read_just_targets(command_base)
        return target not in available_targets
    return False


def pip_install_target_missing(root: Path, command_base: Path, tokens: List[str]) -> bool:
    if len(tokens) < 2 or tokens[1] != "install":
        return False
    args = tokens[2:]
    index = 0
    while index < len(args):
        arg = args[index]
        requirement: Optional[str] = None
        if arg in {"-r", "--requirement"}:
            if index + 1 >= len(args):
                return True
            requirement = args[index + 1]
            index += 2
        elif arg.startswith("--requirement="):
            requirement = arg.split("=", 1)[1]
            index += 1
        else:
            index += 1
        if requirement is None:
            continue
        path = resolve_repo_path(root, command_base, requirement)
        if path is None or not path.is_file():
            return True
    return False


def package_manager_target_missing(
    root: Path,
    command_base: Path,
    tokens: List[str],
    root_package_scripts: Dict[str, str],
) -> bool:
    parsed = parse_package_manager_command(root, command_base, tokens)
    if parsed is None:
        return package_manager_parse_failure_target_missing(root, command_base, tokens)
    if parsed.package_dirs is None:
        return True
    if package_manager_builtin_target_missing(root, command_base, tokens):
        return True
    if package_manager_install_manifest_missing(tokens, parsed):
        return True
    if parsed.script is None:
        return False
    found_script = False
    for package_dir in parsed.package_dirs:
        scripts = root_package_scripts if package_dir == root else read_package_scripts(package_dir / "package.json")
        if parsed.script in scripts:
            found_script = True
        elif not parsed.if_present and not parsed.allow_missing_scripts:
            return True
    return not found_script


def package_manager_builtin_target_missing(root: Path, command_base: Path, tokens: List[str]) -> bool:
    if tokens[0] != "npm":
        return False
    lockfile_root = npm_ci_lockfile_root(root, command_base, tokens)
    return lockfile_root is not None and not npm_lockfile_exists(lockfile_root)


def package_manager_install_manifest_missing(tokens: List[str], parsed: PackageManagerCommand) -> bool:
    command = package_manager_builtin_command(tokens)
    if command != "install":
        return False
    if tokens[0] == "npm" and package_manager_install_has_package_spec(tokens):
        return False
    return any(not (package_dir / "package.json").is_file() for package_dir in parsed.package_dirs or [])


def package_manager_install_has_package_spec(tokens: List[str]) -> bool:
    command_args = package_manager_builtin_command_args(tokens)
    if not command_args or normalize_package_manager_command(tokens[0], command_args[0]) != "install":
        return False
    args = command_args[1:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            return False
        if is_package_manager_no_value_option(arg, tokens[0]):
            index += 1
            continue
        directory_option = package_manager_directory_option_value(tokens[0], args, index)
        if directory_option is not None:
            _, index = directory_option
            continue
        workspace_option = package_manager_workspace_option_value(tokens[0], args, index)
        if workspace_option is not None:
            _, index = workspace_option
            continue
        workspace_toggle = package_manager_all_workspaces_option_value(tokens[0], args, index)
        if workspace_toggle is not None:
            _, index = workspace_toggle
            continue
        include_root = package_manager_include_workspace_root_option(tokens[0], args, index)
        if include_root is not None:
            _, index = include_root
            continue
        install_option = package_manager_install_option_value(args, index)
        if install_option is not None:
            index = install_option
            continue
        if arg.startswith("-"):
            return False
        return True
    return False


def package_manager_install_option_value(args: List[str], index: int) -> Optional[int]:
    arg = args[index]
    if arg in PACKAGE_MANAGER_INSTALL_NO_VALUE_OPTIONS or arg.startswith("--no-"):
        return index + 1
    if any(arg.startswith(f"{option}=") for option in PACKAGE_MANAGER_INSTALL_NO_VALUE_OPTIONS):
        return index + 1
    if arg in PACKAGE_MANAGER_INSTALL_VALUE_OPTIONS:
        return index + 2 if index + 1 < len(args) else len(args)
    if any(arg.startswith(f"{option}=") for option in PACKAGE_MANAGER_INSTALL_VALUE_OPTIONS):
        return index + 1
    return None


def package_manager_builtin_command(tokens: List[str]) -> Optional[str]:
    command_args = package_manager_builtin_command_args(tokens)
    if not command_args:
        return None
    return normalize_package_manager_command(tokens[0], command_args[0])


def package_manager_builtin_command_args(tokens: List[str]) -> List[str]:
    if not tokens:
        return []
    tool = tokens[0]
    args = tokens[1:]
    index = 0
    while index < len(args):
        directory_option = package_manager_directory_option_value(tool, args, index)
        if directory_option is not None:
            _, index = directory_option
            continue
        workspace_option = package_manager_workspace_option_value(tool, args, index)
        if workspace_option is not None:
            _, index = workspace_option
            continue
        workspace_toggle = package_manager_all_workspaces_option_value(tool, args, index)
        if workspace_toggle is not None:
            _, index = workspace_toggle
            continue
        include_root = package_manager_include_workspace_root_option(tool, args, index)
        if include_root is not None:
            _, index = include_root
            continue
        arg = args[index]
        if is_package_manager_no_value_option(arg, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, args, index)
        if value_option is not None:
            index = value_option
            continue
        if arg.startswith("-"):
            return []
        return args[index:]
    return []


def npm_lockfile_exists(package_dir: Path) -> bool:
    return (package_dir / "package-lock.json").is_file() or (package_dir / "npm-shrinkwrap.json").is_file()


def npm_ci_lockfile_root(root: Path, command_base: Path, tokens: List[str]) -> Optional[Path]:
    directory = command_base
    args = tokens[1:]
    index = 0
    while index < len(args):
        directory_option = package_manager_directory_option_value("npm", args, index)
        if directory_option is not None:
            value, index = directory_option
            resolved = resolve_repo_path(root, command_base, value)
            if resolved is None:
                return None
            directory = resolved
            continue
        if package_manager_workspace_option_value("npm", args, index) is not None:
            _, index = package_manager_workspace_option_value("npm", args, index)
            continue
        if package_manager_all_workspaces_option_value("npm", args, index) is not None:
            _, index = package_manager_all_workspaces_option_value("npm", args, index)
            continue
        if package_manager_include_workspace_root_option("npm", args, index) is not None:
            _, index = package_manager_include_workspace_root_option("npm", args, index)
            continue
        arg = args[index]
        if is_package_manager_no_value_option(arg, "npm"):
            index += 1
            continue
        value_option = package_manager_value_option_value("npm", args, index)
        if value_option is not None:
            index = value_option
            continue
        if arg.startswith("-"):
            return None
        if normalize_package_manager_command("npm", arg) != "ci":
            return None
        return package_manager_command_directory(root, directory, "npm", args[index:])
    return None


def parse_package_manager_command(
    root: Path,
    command_base: Path,
    tokens: List[str],
) -> Optional[PackageManagerCommand]:
    if not tokens:
        return None
    tool = tokens[0]
    directory = command_base
    workspace_selection = WorkspaceSelection([])
    args = tokens[1:]
    if_present = package_manager_args_if_present(args)
    index = 0
    while index < len(args):
        workspace_option = package_manager_workspace_option_value(tool, args, index)
        if workspace_option is not None:
            value, next_index = workspace_option
            workspace_selection.names.append(value)
            index = next_index
            continue
        workspace_toggle = package_manager_all_workspaces_option_value(tool, args, index)
        if workspace_toggle is not None:
            enabled, next_index = workspace_toggle
            workspace_selection.all_workspaces = workspace_selection.all_workspaces or enabled
            index = next_index
            continue
        include_root = package_manager_include_workspace_root_option(tool, args, index)
        if include_root is not None:
            enabled, next_index = include_root
            workspace_selection.include_root = workspace_selection.include_root or enabled
            index = next_index
            continue
        directory_option = package_manager_directory_option_value(tool, args, index)
        if directory_option is not None:
            value, next_index = directory_option
            resolved = resolve_repo_path(root, command_base, value)
            if resolved is None:
                return None
            directory = resolved
            index = next_index
            continue
        arg = args[index]
        if is_package_manager_no_value_option(arg, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, args, index)
        if value_option is not None:
            index = value_option
            continue
        if arg.startswith("-"):
            return None
        command_args = args[index:]
        workspace_selection.extend(package_manager_workspace_selection(tool, command_args))
        command_directory = package_manager_command_directory(root, directory, tool, command_args)
        if command_directory is None:
            return None
        directory = command_directory
        script = package_manager_script_from_args(tool, command_args)
        allow_missing_scripts = tool == "pnpm" and workspace_selection.all_workspaces
        if script == UNSUPPORTED_DIRECT_SCRIPT and tool == "npm":
            return PackageManagerCommand(None, script)
        if workspace_selection.enabled():
            package_dirs = resolve_package_workspaces(root, directory, tool, workspace_selection)
            return PackageManagerCommand(package_dirs, script, if_present, allow_missing_scripts)
        return PackageManagerCommand([directory], script, if_present, allow_missing_scripts)
    if workspace_selection.enabled():
        package_dirs = resolve_package_workspaces(root, directory, tool, workspace_selection)
        return PackageManagerCommand(package_dirs, None, if_present)
    return PackageManagerCommand([directory], None, if_present)


def package_manager_workspace_selection(tool: str, args: List[str]) -> WorkspaceSelection:
    if not args:
        return WorkspaceSelection([])
    command = normalize_package_manager_command(tool, args[0])
    if tool == "yarn" and command == "workspace":
        return yarn_workspace_command_selection(args)
    if command in {"run", "run-script"}:
        return package_manager_run_workspace_selection(tool, args[1:])
    if command in PACKAGE_MANAGER_DIRECT_SCRIPT_ALIASES.get(tool, set()):
        return package_manager_post_command_workspace_selection(tool, args[1:])
    if command in PACKAGE_MANAGER_BUILTIN_COMMANDS.get(tool, set()):
        return package_manager_post_command_workspace_selection(tool, args[1:])
    return WorkspaceSelection([])


def package_manager_run_workspace_selection(tool: str, tokens: List[str]) -> WorkspaceSelection:
    selection = WorkspaceSelection([])
    index = 0
    saw_script = False
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            break
        directory_option = package_manager_directory_option_value(tool, tokens, index)
        if directory_option is not None:
            _, index = directory_option
            continue
        workspace_option = package_manager_workspace_option_value(tool, tokens, index)
        if workspace_option is not None:
            value, index = workspace_option
            selection.names.append(value)
            continue
        workspace_toggle = package_manager_all_workspaces_option_value(tool, tokens, index)
        if workspace_toggle is not None:
            enabled, index = workspace_toggle
            selection.all_workspaces = selection.all_workspaces or enabled
            continue
        include_root = package_manager_include_workspace_root_option(tool, tokens, index)
        if include_root is not None:
            enabled, index = include_root
            selection.include_root = selection.include_root or enabled
            continue
        if is_package_manager_no_value_option(token, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, tokens, index)
        if value_option is not None:
            index = value_option
            continue
        if token.startswith("-") or saw_script:
            break
        saw_script = True
        index += 1
    return selection


def package_manager_post_command_workspace_selection(tool: str, tokens: List[str]) -> WorkspaceSelection:
    selection = WorkspaceSelection([])
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            break
        directory_option = package_manager_directory_option_value(tool, tokens, index)
        if directory_option is not None:
            _, index = directory_option
            continue
        workspace_option = package_manager_workspace_option_value(tool, tokens, index)
        if workspace_option is not None:
            value, index = workspace_option
            selection.names.append(value)
            continue
        workspace_toggle = package_manager_all_workspaces_option_value(tool, tokens, index)
        if workspace_toggle is not None:
            enabled, index = workspace_toggle
            selection.all_workspaces = selection.all_workspaces or enabled
            continue
        include_root = package_manager_include_workspace_root_option(tool, tokens, index)
        if include_root is not None:
            enabled, index = include_root
            selection.include_root = selection.include_root or enabled
            continue
        if is_package_manager_no_value_option(token, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, tokens, index)
        if value_option is not None:
            index = value_option
            continue
        break
    return selection


def package_manager_command_directory(root: Path, directory: Path, tool: str, args: List[str]) -> Optional[Path]:
    if not args:
        return directory
    command = normalize_package_manager_command(tool, args[0])
    if tool == "yarn" and command == "workspace":
        return directory
    if command in {"run", "run-script"}:
        return package_manager_run_command_directory(root, directory, tool, args[1:])
    if (
        command in PACKAGE_MANAGER_DIRECT_SCRIPT_ALIASES.get(tool, set())
        or command in PACKAGE_MANAGER_BUILTIN_COMMANDS.get(tool, set())
    ):
        return package_manager_post_command_directory(root, directory, tool, args[1:])
    if command in PACKAGE_MANAGER_DIRECT_SCRIPTS:
        return directory
    return directory


def package_manager_run_command_directory(root: Path, directory: Path, tool: str, tokens: List[str]) -> Optional[Path]:
    index = 0
    saw_script = False
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            break
        directory_option = package_manager_directory_option_value(tool, tokens, index)
        if directory_option is not None:
            value, index = directory_option
            resolved = resolve_repo_path(root, directory, value)
            if resolved is None:
                return None
            directory = resolved
            continue
        if package_manager_workspace_option_value(tool, tokens, index) is not None:
            _, index = package_manager_workspace_option_value(tool, tokens, index)
            continue
        if package_manager_all_workspaces_option_value(tool, tokens, index) is not None:
            _, index = package_manager_all_workspaces_option_value(tool, tokens, index)
            continue
        if package_manager_include_workspace_root_option(tool, tokens, index) is not None:
            _, index = package_manager_include_workspace_root_option(tool, tokens, index)
            continue
        if is_package_manager_no_value_option(token, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, tokens, index)
        if value_option is not None:
            index = value_option
            continue
        if token.startswith("-") or saw_script:
            break
        saw_script = True
        index += 1
    return directory


def package_manager_post_command_directory(root: Path, directory: Path, tool: str, tokens: List[str]) -> Optional[Path]:
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            break
        directory_option = package_manager_directory_option_value(tool, tokens, index)
        if directory_option is not None:
            value, index = directory_option
            resolved = resolve_repo_path(root, directory, value)
            if resolved is None:
                return None
            directory = resolved
            continue
        if package_manager_workspace_option_value(tool, tokens, index) is not None:
            _, index = package_manager_workspace_option_value(tool, tokens, index)
            continue
        if package_manager_all_workspaces_option_value(tool, tokens, index) is not None:
            _, index = package_manager_all_workspaces_option_value(tool, tokens, index)
            continue
        if package_manager_include_workspace_root_option(tool, tokens, index) is not None:
            _, index = package_manager_include_workspace_root_option(tool, tokens, index)
            continue
        if is_package_manager_no_value_option(token, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, tokens, index)
        if value_option is not None:
            index = value_option
            continue
        break
    return directory


def first_package_manager_run_arg(tool: str, tokens: List[str]) -> Optional[str]:
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            return None
        directory_option = package_manager_directory_option_value(tool, tokens, index)
        if directory_option is not None:
            _, index = directory_option
            continue
        workspace_option = package_manager_workspace_option_value(tool, tokens, index)
        if workspace_option is not None:
            _, index = workspace_option
            continue
        workspace_toggle = package_manager_all_workspaces_option_value(tool, tokens, index)
        if workspace_toggle is not None:
            _, index = workspace_toggle
            continue
        include_root = package_manager_include_workspace_root_option(tool, tokens, index)
        if include_root is not None:
            _, index = include_root
            continue
        if is_package_manager_no_value_option(token, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, tokens, index)
        if value_option is not None:
            index = value_option
            continue
        if token.startswith("-"):
            return None
        return token
    return None


def package_manager_run_without_script(command: str) -> bool:
    command = command_without_leading_env_assignments(command)
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens or tokens[0] not in {"npm", "pnpm", "yarn", "bun"}:
        return False
    tool = tokens[0]
    args = tokens[1:]
    index = 0
    while index < len(args):
        workspace_option = package_manager_workspace_option_value(tool, args, index)
        if workspace_option is not None:
            _, index = workspace_option
            continue
        workspace_toggle = package_manager_all_workspaces_option_value(tool, args, index)
        if workspace_toggle is not None:
            _, index = workspace_toggle
            continue
        include_root = package_manager_include_workspace_root_option(tool, args, index)
        if include_root is not None:
            _, index = include_root
            continue
        directory_option = package_manager_directory_option_value(tool, args, index)
        if directory_option is not None:
            _, index = directory_option
            continue
        token = args[index]
        if is_package_manager_no_value_option(token, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, args, index)
        if value_option is not None:
            index = value_option
            continue
        if token.startswith("-"):
            return False
        command = normalize_package_manager_command(tool, token)
        return command in {"run", "run-script"} and first_package_manager_run_arg(tool, args[index + 1:]) is None
    return False


def package_manager_workspace_option_value(
    tool: str,
    args: List[str],
    index: int,
) -> Optional[Tuple[str, int]]:
    arg = args[index]
    options = PACKAGE_MANAGER_WORKSPACE_OPTIONS.get(tool, set())
    if arg in options:
        if index + 1 >= len(args):
            return None
        return args[index + 1], index + 2
    for option in options:
        if arg.startswith(f"{option}="):
            return arg.split("=", 1)[1], index + 1
    return None


def package_manager_value_option_value(
    tool: str,
    args: List[str],
    index: int,
) -> Optional[int]:
    arg = args[index]
    options = PACKAGE_MANAGER_VALUE_OPTIONS
    if arg in options:
        return index + 2 if index + 1 < len(args) else len(args)
    if any(arg.startswith(f"{option}=") for option in options):
        return index + 1
    return None


def package_manager_all_workspaces_option_value(
    tool: str,
    args: List[str],
    index: int,
) -> Optional[Tuple[bool, int]]:
    arg = args[index]
    options = PACKAGE_MANAGER_ALL_WORKSPACES_OPTIONS.get(tool, set())
    if arg in options:
        return True, index + 1
    for option in options:
        if arg.startswith(f"{option}="):
            return parse_truthy_option_value(arg.split("=", 1)[1]), index + 1
    return None


def package_manager_include_workspace_root_option(
    tool: str,
    args: List[str],
    index: int,
) -> Optional[Tuple[bool, int]]:
    arg = args[index]
    options = PACKAGE_MANAGER_INCLUDE_WORKSPACE_ROOT_OPTIONS.get(tool, set())
    if arg in options:
        return True, index + 1
    for option in options:
        if arg.startswith(f"{option}="):
            return parse_truthy_option_value(arg.split("=", 1)[1]), index + 1
    return None


def parse_truthy_option_value(value: str) -> bool:
    return value.lower() not in {"0", "false", "no", "off"}


def package_manager_args_if_present(args: List[str]) -> bool:
    enabled = False
    for arg in args:
        if arg == "--":
            break
        if arg == "--if-present":
            enabled = True
        elif arg.startswith("--if-present="):
            enabled = parse_truthy_option_value(arg.split("=", 1)[1])
    return enabled


def resolve_package_workspaces(
    root: Path,
    package_root: Path,
    tool: str,
    selection: WorkspaceSelection,
) -> Optional[List[Path]]:
    declared = declared_package_workspaces(root, package_root, tool)
    selected: List[Path] = []
    if selection.all_workspaces and not selection.names:
        selected.extend(declared)
    for workspace in selection.names:
        resolved = resolve_declared_package_workspaces(package_root, declared, workspace, tool)
        if resolved is None:
            return None
        selected.extend(resolved)
    if selection.include_root:
        selected.append(package_root)
    selected = unique_paths(selected)
    return selected or None


def declared_package_workspaces(root: Path, package_root: Path, tool: str) -> List[Path]:
    if tool == "pnpm":
        workspace_file = package_root / "pnpm-workspace.yaml"
        patterns = read_pnpm_workspace_patterns(workspace_file)
        if not patterns and not workspace_file.is_file():
            return discover_pnpm_recursive_packages(root, package_root)
    else:
        patterns = read_package_workspace_patterns(package_root / "package.json")
    workspaces: List[Path] = []
    for pattern in patterns:
        exclude = pattern.startswith("!")
        if exclude:
            pattern = pattern[1:]
        pattern = pattern.strip()
        if not pattern:
            continue
        candidates = matching_workspace_dirs(root, package_root, pattern)
        if exclude:
            excluded = {candidate.resolve() for candidate in candidates}
            workspaces = [workspace for workspace in workspaces if workspace.resolve() not in excluded]
            continue
        workspaces.extend(candidates)
    return unique_paths(workspaces)


def discover_pnpm_recursive_packages(root: Path, package_root: Path) -> List[Path]:
    package_dirs: List[Path] = []
    for package_json in iter_files(package_root, "package.json"):
        package_dir = package_json.parent
        try:
            package_dir.resolve().relative_to(root.resolve())
        except ValueError:
            continue
        package_dirs.append(package_dir)
    return unique_paths(package_dirs)


def matching_workspace_dirs(root: Path, package_root: Path, pattern: str) -> List[Path]:
    matches: List[Path] = []
    for expanded_pattern in expand_brace_glob(pattern):
        for candidate in sorted(package_root.glob(expanded_pattern)):
            if not candidate.is_dir() or not (candidate / "package.json").is_file():
                continue
            try:
                candidate.resolve().relative_to(root.resolve())
            except ValueError:
                continue
            matches.append(candidate)
    return matches


def expand_brace_glob(pattern: str) -> List[str]:
    match = re.search(r"\{([^{}]+)\}", pattern)
    if not match:
        return [pattern]
    expanded: List[str] = []
    before = pattern[: match.start()]
    after = pattern[match.end() :]
    for option in match.group(1).split(","):
        expanded.extend(expand_brace_glob(f"{before}{option}{after}"))
    return expanded


def read_package_workspace_patterns(path: Path) -> List[str]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    workspaces = data.get("workspaces")
    if isinstance(workspaces, list):
        return [item for item in workspaces if isinstance(item, str)]
    if isinstance(workspaces, dict):
        packages = workspaces.get("packages", [])
        if isinstance(packages, list):
            return [item for item in packages if isinstance(item, str)]
    return []


def read_pnpm_workspace_patterns(path: Path) -> List[str]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    patterns: List[str] = []
    in_packages = False
    packages_indent = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if not in_packages:
            if stripped.startswith("packages:"):
                package_value = strip_yaml_inline_comment(stripped.split(":", 1)[1].strip())
                inline_patterns = parse_yaml_inline_string_list(package_value)
                if inline_patterns:
                    patterns.extend(inline_patterns)
                    continue
                if package_value:
                    continue
                in_packages = True
                packages_indent = indent
            continue
        if indent <= packages_indent and not stripped.startswith("-"):
            break
        if not stripped.startswith("-"):
            continue
        pattern = stripped[1:].strip()
        pattern = strip_yaml_inline_comment(pattern)
        pattern = pattern.strip("\"'")
        if pattern:
            patterns.append(pattern)
    return patterns


def strip_yaml_inline_comment(value: str) -> str:
    if value.startswith("#"):
        return ""
    if " #" in value:
        return value.split(" #", 1)[0].strip()
    return value


def parse_yaml_inline_string_list(value: str) -> List[str]:
    if not value.startswith("[") or not value.endswith("]"):
        return []
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        parsed = None
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, str)]
    inner = value[1:-1].strip()
    if not inner:
        return []
    items = []
    for item in inner.split(","):
        item = strip_yaml_inline_comment(item.strip()).strip("\"'")
        if item:
            items.append(item)
    return items


def resolve_declared_package_workspaces(
    package_root: Path,
    declared: List[Path],
    workspace: str,
    tool: str,
) -> Optional[List[Path]]:
    normalized = workspace.strip().rstrip("/")
    relation_selector = parse_pnpm_relation_selector(normalized) if tool == "pnpm" else None
    selector_base = relation_selector.base if relation_selector is not None else normalize_pnpm_selector_base(normalized)
    exact_selector = selector_base or normalized
    if tool == "pnpm":
        package_name_matches = resolve_pnpm_package_name_workspaces(declared, exact_selector)
        if package_name_matches is not None:
            if relation_selector is not None:
                return resolve_pnpm_relation_workspaces_for_bases(
                    declared,
                    package_name_matches,
                    relation_selector,
                ) or None
            if has_pnpm_relation_adornment(normalized):
                return None
            return unique_paths(package_name_matches) or None
    normalized_without_dot = exact_selector[2:] if exact_selector.startswith("./") else exact_selector
    for workspace_dir in declared:
        rel = str(workspace_dir.relative_to(package_root)).replace(os.sep, "/")
        if normalized_without_dot == rel or exact_selector == f"./{rel}":
            if relation_selector is not None:
                return resolve_pnpm_relation_workspaces_for_bases(
                    declared,
                    [workspace_dir],
                    relation_selector,
                ) or None
            return [workspace_dir]
        if read_package_name(workspace_dir / "package.json") == exact_selector.strip():
            if relation_selector is not None:
                return resolve_pnpm_relation_workspaces(declared, workspace_dir, relation_selector)
            if tool == "pnpm" and has_pnpm_relation_adornment(normalized):
                return None
            return [workspace_dir]
    filter_selector = normalize_pnpm_filter_selector(exact_selector)
    if filter_selector is None:
        return None
    matches = []
    for workspace_dir in declared:
        rel = str(workspace_dir.relative_to(package_root)).replace(os.sep, "/")
        if pnpm_filter_selector_matches_workspace(filter_selector, rel):
            matches.append(workspace_dir)
    if relation_selector is not None and matches:
        return resolve_pnpm_relation_workspaces_for_bases(
            declared,
            unique_paths(matches),
            relation_selector,
        ) or None
    return unique_paths(matches) or None


def resolve_pnpm_package_name_workspaces(
    declared: List[Path],
    selector: str,
) -> Optional[List[Path]]:
    normalized = selector.strip().rstrip("/")
    if not normalized:
        return None
    names = [
        (workspace_dir, name)
        for workspace_dir in declared
        if (name := read_package_name(workspace_dir / "package.json"))
    ]
    exact_matches = [workspace_dir for workspace_dir, name in names if name == normalized]
    if exact_matches:
        return exact_matches
    if pnpm_selector_allows_unscoped_fallback(normalized):
        unscoped_matches = [
            workspace_dir
            for workspace_dir, name in names
            if pnpm_package_unscoped_name(name) == normalized
        ]
        if unscoped_matches:
            return unscoped_matches if len(unscoped_matches) == 1 else []
    if any(char in normalized for char in "*?["):
        glob_matches = [
            workspace_dir
            for workspace_dir, name in names
            if fnmatch.fnmatch(name, normalized)
        ]
        if glob_matches:
            return glob_matches
    return None


def pnpm_selector_allows_unscoped_fallback(selector: str) -> bool:
    return (
        not selector.startswith(("@", ".", "/", "~"))
        and "/" not in selector
        and not any(char in selector for char in "*?[")
    )


def pnpm_package_unscoped_name(name: str) -> str:
    if name.startswith("@") and "/" in name:
        return name.rsplit("/", 1)[1]
    return name


def parse_pnpm_relation_selector(selector: str) -> Optional[PnpmRelationSelector]:
    stripped = selector.strip().rstrip("/")
    if not stripped:
        return None
    leading = pnpm_leading_relation(stripped)
    trailing = pnpm_trailing_relation(stripped)
    if leading is not None and trailing is not None:
        return None
    if leading is not None:
        base, include_base = leading
        return PnpmRelationSelector(base.rstrip("/"), "dependents", include_base)
    if trailing is not None:
        base, include_base = trailing
        return PnpmRelationSelector(base.rstrip("/"), "dependencies", include_base)
    return None


def pnpm_leading_relation(selector: str) -> Optional[Tuple[str, bool]]:
    for prefix, include_base in (("...^", False), ("...", True)):
        if selector.startswith(prefix) and len(selector) > len(prefix):
            return selector[len(prefix):], include_base
    return None


def pnpm_trailing_relation(selector: str) -> Optional[Tuple[str, bool]]:
    for suffix, include_base in (("^...", False), ("...", True)):
        if selector.endswith(suffix) and len(selector) > len(suffix):
            return selector[: -len(suffix)], include_base
    return None


def has_pnpm_relation_adornment(selector: str) -> bool:
    stripped = selector.strip().rstrip("/")
    return pnpm_leading_relation(stripped) is not None or pnpm_trailing_relation(stripped) is not None


def resolve_pnpm_relation_workspaces(
    declared: List[Path],
    base_workspace: Path,
    relation_selector: PnpmRelationSelector,
) -> List[Path]:
    graph = pnpm_workspace_dependency_graph(declared)
    if relation_selector.direction == "dependents":
        graph = reverse_workspace_dependency_graph(graph)
    related = transitive_related_workspaces(graph, base_workspace)
    selected = ([base_workspace] if relation_selector.include_base else []) + related
    return unique_paths(selected)


def resolve_pnpm_relation_workspaces_for_bases(
    declared: List[Path],
    base_workspaces: List[Path],
    relation_selector: PnpmRelationSelector,
) -> List[Path]:
    selected: List[Path] = []
    for base_workspace in base_workspaces:
        selected.extend(resolve_pnpm_relation_workspaces(declared, base_workspace, relation_selector))
    if not relation_selector.include_base:
        base_resolved = {workspace.resolve() for workspace in base_workspaces}
        selected = [workspace for workspace in selected if workspace.resolve() not in base_resolved]
    return unique_paths(selected)


def pnpm_workspace_dependency_graph(declared: List[Path]) -> Dict[Path, List[Path]]:
    package_names = workspace_package_name_map(declared)
    graph: Dict[Path, List[Path]] = {workspace_dir: [] for workspace_dir in declared}
    for workspace_dir in declared:
        for dependency_name in read_package_dependency_names(workspace_dir / "package.json"):
            dependency_dir = package_names.get(dependency_name)
            if dependency_dir is not None and dependency_dir not in graph[workspace_dir]:
                graph[workspace_dir].append(dependency_dir)
    return graph


def workspace_package_name_map(declared: List[Path]) -> Dict[str, Path]:
    names: Dict[str, Path] = {}
    for workspace_dir in declared:
        name = read_package_name(workspace_dir / "package.json")
        if name:
            names[name] = workspace_dir
    return names


def read_package_dependency_names(path: Path) -> List[str]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    names: List[str] = []
    for field in PACKAGE_DEPENDENCY_FIELDS:
        dependencies = data.get(field)
        if not isinstance(dependencies, dict):
            continue
        for name, spec in dependencies.items():
            if not isinstance(name, str):
                continue
            names.append(pnpm_workspace_alias_dependency_name(spec) or name)
    return names


def pnpm_workspace_alias_dependency_name(spec: Any) -> Optional[str]:
    if not isinstance(spec, str) or not spec.startswith("workspace:"):
        return None
    target = spec[len("workspace:"):].strip()
    if not target or target[0] in "*^~<>=0123456789":
        return None
    if target.startswith(("./", "../")):
        return None
    if target.startswith("@"):
        version_separator = target.rfind("@")
        return target[:version_separator] if version_separator > 0 else target
    name, _, _ = target.partition("@")
    return name or None


def reverse_workspace_dependency_graph(graph: Dict[Path, List[Path]]) -> Dict[Path, List[Path]]:
    reverse: Dict[Path, List[Path]] = {workspace_dir: [] for workspace_dir in graph}
    for workspace_dir, dependencies in graph.items():
        for dependency_dir in dependencies:
            reverse.setdefault(dependency_dir, []).append(workspace_dir)
    return reverse


def transitive_related_workspaces(graph: Dict[Path, List[Path]], base_workspace: Path) -> List[Path]:
    related: List[Path] = []
    seen = {base_workspace.resolve()}
    queue = list(graph.get(base_workspace, []))
    while queue:
        workspace_dir = queue.pop(0)
        resolved = workspace_dir.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        related.append(workspace_dir)
        queue.extend(graph.get(workspace_dir, []))
    return related


def normalize_pnpm_selector_base(selector: str) -> Optional[str]:
    stripped = selector.strip().rstrip("/")
    if not stripped:
        return None
    relation_selector = parse_pnpm_relation_selector(stripped)
    if relation_selector is not None:
        return relation_selector.base
    for prefix in ("...^", "...", "^"):
        if stripped.startswith(prefix) and len(stripped) > len(prefix):
            stripped = stripped[len(prefix):]
            break
    for suffix in ("^...", "...", "^"):
        if stripped.endswith(suffix) and len(stripped) > len(suffix):
            stripped = stripped[: -len(suffix)]
            break
    stripped = stripped.rstrip("/")
    return stripped or None


def normalize_pnpm_filter_selector(selector: str) -> Optional[str]:
    stripped = normalize_pnpm_selector_base(selector)
    if not stripped:
        return None
    if stripped.startswith("./"):
        stripped = stripped[2:]
    if not stripped or not is_pnpm_path_or_glob_selector(stripped):
        return None
    return stripped


def is_pnpm_path_or_glob_selector(selector: str) -> bool:
    return selector.startswith(".") or "/" in selector or any(char in selector for char in "*?[")


def pnpm_filter_selector_matches_workspace(selector: str, rel: str) -> bool:
    return any(
        fnmatch.fnmatch(rel, expanded_selector)
        or fnmatch.fnmatch(f"./{rel}", expanded_selector)
        for expanded_selector in expand_brace_glob(selector)
    )


def unique_paths(paths: List[Path]) -> List[Path]:
    seen = set()
    unique: List[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def read_package_name(path: Path) -> Optional[str]:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    name = data.get("name")
    return name if isinstance(name, str) else None


def package_manager_directory_option_value(
    tool: str,
    args: List[str],
    index: int,
) -> Optional[Tuple[str, int]]:
    arg = args[index]
    options = PACKAGE_MANAGER_DIRECTORY_OPTIONS.get(tool, set())
    if arg in options:
        if index + 1 >= len(args):
            return None
        return args[index + 1], index + 2
    for option in options:
        if arg.startswith(f"{option}="):
            return arg.split("=", 1)[1], index + 1
    if tool == "pnpm" and arg.startswith("-C") and arg != "-C":
        return arg[2:], index + 1
    return None


def package_manager_option_name(arg: str) -> str:
    return arg.split("=", 1)[0]


def package_manager_script_from_args(tool: str, args: List[str]) -> Optional[str]:
    if not args:
        return None
    command = normalize_package_manager_command(tool, args[0])
    if tool == "yarn" and command == "workspace":
        if len(args) < 3:
            return None
        return package_manager_script_from_args(tool, args[2:])
    if command in {"run", "run-script"}:
        return first_package_manager_run_arg(tool, args[1:])
    if command in PACKAGE_MANAGER_DIRECT_SCRIPT_ALIASES.get(tool, set()):
        return command
    if command in PACKAGE_MANAGER_BUILTIN_COMMANDS.get(tool, set()):
        return None
    if tool == "npm" and command in NPM_UNSUPPORTED_DIRECT_SCRIPTS:
        return UNSUPPORTED_DIRECT_SCRIPT
    if command in PACKAGE_MANAGER_DIRECT_SCRIPTS:
        return UNSUPPORTED_DIRECT_SCRIPT
    return None


def yarn_workspace_command_selection(args: List[str]) -> WorkspaceSelection:
    if len(args) < 2:
        return WorkspaceSelection([])
    return WorkspaceSelection([args[1]])


def normalize_package_manager_command(tool: str, command: str) -> str:
    return PACKAGE_MANAGER_COMMAND_ALIASES.get(tool, {}).get(command, command)


def package_manager_no_value_options(tool: Optional[str] = None) -> set[str]:
    options = set(PACKAGE_MANAGER_NO_VALUE_OPTIONS)
    if tool is not None:
        options.update(PACKAGE_MANAGER_TOOL_NO_VALUE_OPTIONS.get(tool, set()))
    return options


def is_package_manager_no_value_option(arg: str, tool: Optional[str] = None) -> bool:
    options = package_manager_no_value_options(tool)
    return arg in options or (
        arg.startswith("--") and "=" in arg and package_manager_option_name(arg) in options
    )


def first_non_option(tokens: List[str]) -> Optional[str]:
    for token in tokens:
        if not token.startswith("-"):
            return token
    return None


def make_command_target_missing(
    root: Path,
    command_base: Path,
    args: List[str],
    root_make_targets: List[str],
) -> bool:
    parsed = parse_make_command(root, command_base, args)
    if parsed is None:
        return False
    makefile, targets = parsed
    return parsed_make_command_target_missing(root, makefile, targets, root_make_targets)


def parsed_make_command_target_missing(
    root: Path,
    makefile: Path,
    targets: List[str],
    root_make_targets: List[str],
) -> bool:
    if not targets:
        return not makefile.is_file()
    if not makefile.is_file():
        return True
    if makefile == default_makefile(root):
        make_targets = root_make_targets
    else:
        make_targets = read_make_targets(makefile)
    return any(target not in make_targets for target in targets)


def parse_make_command(root: Path, command_base: Path, args: List[str]) -> Optional[Tuple[Path, List[str]]]:
    directory = command_base
    makefile_arg: Optional[str] = None
    targets: List[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            targets.extend(token for token in args[index + 1 :] if "=" not in token)
            break
        if "=" in arg and not arg.startswith("-"):
            index += 1
            continue
        if arg in {"-C", "--directory"}:
            if index + 1 >= len(args):
                return None
            resolved = resolve_repo_path(root, directory, args[index + 1])
            if resolved is None:
                return None
            directory = resolved
            index += 2
            continue
        if arg.startswith("-C") and arg != "-C":
            resolved = resolve_repo_path(root, directory, arg[2:])
            if resolved is None:
                return None
            directory = resolved
            index += 1
            continue
        if arg.startswith("--directory="):
            resolved = resolve_repo_path(root, directory, arg.split("=", 1)[1])
            if resolved is None:
                return None
            directory = resolved
            index += 1
            continue
        if arg in {"-f", "--file", "--makefile"}:
            if index + 1 >= len(args):
                return None
            makefile_arg = args[index + 1]
            index += 2
            continue
        if arg.startswith("-f") and arg != "-f":
            makefile_arg = arg[2:]
            index += 1
            continue
        if arg.startswith(("--file=", "--makefile=")):
            makefile_arg = arg.split("=", 1)[1]
            index += 1
            continue
        if arg in {"-s", "--silent", "--quiet", "-k", "--keep-going", "-n", "--just-print", "--dry-run", "--recon"}:
            index += 1
            continue
        if arg in {"-j", "--jobs"}:
            if index + 1 < len(args) and args[index + 1].isdigit():
                index += 2
            else:
                index += 1
            continue
        if arg.startswith("-j") and arg[2:].isdigit():
            index += 1
            continue
        if arg.startswith("--jobs="):
            index += 1
            continue
        if arg.startswith("-"):
            return None
        targets.append(arg)
        index += 1

    if makefile_arg is None:
        makefile = default_makefile(directory)
    else:
        makefile = resolve_repo_path(root, directory, makefile_arg)
        if makefile is None:
            return None
    return makefile, targets


def is_codex_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").is_file()


def resolve_repo_path(root: Path, base: Path, value: str) -> Optional[Path]:
    candidate = Path(value)
    if candidate.is_absolute():
        return None
    resolved = (base / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def local_command_target(command: str) -> Optional[str]:
    command = command_without_leading_env_assignments(command)
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return None
    if is_repo_local_token(tokens[0]):
        return tokens[0]
    if tokens[0] not in INTERPRETER_COMMANDS:
        return None
    skip_next = False
    for token in tokens[1:]:
        if skip_next:
            skip_next = False
            continue
        if token in {"-m", "-c", "-e"}:
            skip_next = True
            continue
        if token.startswith("-"):
            continue
        if is_repo_local_token(token):
            return token
        return None
    return None


def direct_local_command_target(command: str) -> Optional[str]:
    command = command_without_leading_env_assignments(command)
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens or not is_repo_local_token(tokens[0]):
        return None
    return tokens[0]


def is_repo_local_token(token: str) -> bool:
    return token.startswith(("./", "script/", "scripts/", "bin/", "tools/"))


def classify_documented_command(line: str, command: str) -> List[str]:
    text = line.replace(f"`{command}`", " ").lower()
    matches = []
    for responsibility, keywords in DOC_RESPONSIBILITY_KEYWORDS.items():
        if any(keyword_matches_text(keyword, text) for keyword in keywords):
            matches.append(responsibility)
    if documented_pip_install_command(command) and "setup" not in matches:
        matches.append("setup")
    return matches


def documented_command_segment_context(context: str, command: str, is_split_chain: bool) -> str:
    if not is_split_chain:
        return context
    responsibilities = [
        responsibility
        for responsibility in workflow_command_responsibilities(command)
        if responsibility in DOC_RESPONSIBILITY_KEYWORDS
    ]
    if not responsibilities:
        return context
    return " ".join(DOC_RESPONSIBILITY_KEYWORDS[responsibility][0] for responsibility in responsibilities)


def documented_pip_install_command(command: str) -> bool:
    try:
        tokens = shlex.split(command_without_leading_env_assignments(command))
    except ValueError:
        tokens = command.split()
    tokens = normalize_pip_command_tokens(tokens)
    return len(tokens) >= 2 and tokens[0] in {"pip", "pip3"} and tokens[1] == "install"


def normalize_pip_command_tokens(tokens: List[str]) -> List[str]:
    if len(tokens) >= 4 and tokens[0] in {"python", "python3"} and tokens[1] == "-m" and tokens[2] == "pip":
        return [tokens[2], *tokens[3:]]
    if len(tokens) >= 3 and tokens[0] == "uv" and tokens[1] == "pip":
        return [tokens[1], *tokens[2:]]
    return tokens


def keyword_matches_text(keyword: str, text: str) -> bool:
    if " " in keyword:
        return keyword in text
    return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", text) is not None


def classify_responsibility_status(found: List[str], documented: List[str], needed: bool) -> str:
    if found:
        return "present"
    if documented:
        return "documented"
    if not needed:
        return "not_applicable"
    return "missing"


def infer_responsibility_needs(
    root: Path,
    package_scripts: Dict[str, str],
    make_targets: List[str],
    just_targets: List[str],
) -> Dict[str, bool]:
    has_dependencies = has_dependency_surface(root)
    has_code = has_code_surface(root)
    has_tests = has_test_surface(root)
    has_packaging = has_codex_packaging_surface(root)
    has_server = has_server_surface(root, package_scripts, make_targets, just_targets)
    has_console = has_named_surface(package_scripts, make_targets, just_targets, {"console", "repl", "shell"})

    return {
        "bootstrap": has_dependencies,
        "setup": has_dependencies,
        "update": has_dependencies,
        "server": has_server,
        "test": has_code or has_tests or has_packaging,
        "cibuild": has_code or has_tests or has_packaging,
        "console": has_console,
    }


def has_dependency_surface(root: Path) -> bool:
    return any(path.name in DEPENDENCY_MANIFESTS for path in iter_files(root))


def has_code_surface(root: Path) -> bool:
    return any(path.suffix in CODE_EXTENSIONS for path in iter_files(root))


def has_test_surface(root: Path) -> bool:
    return any(iter_files(root, "test_*.py")) or any(iter_files(root, "*_test.py"))


def has_codex_packaging_surface(root: Path) -> bool:
    skills_dir = root / "skills"
    mirror_dir = root / "plugins" / "codex-skills" / "skills"
    return any(
        directory.is_dir() and any(is_codex_skill_dir(path) for path in directory.iterdir())
        for directory in (skills_dir, mirror_dir)
    )


def has_server_surface(
    root: Path,
    package_scripts: Dict[str, str],
    make_targets: List[str],
    just_targets: List[str],
) -> bool:
    if any((root / marker).exists() for marker in SERVER_MARKERS):
        return True
    return has_named_surface(package_scripts, make_targets, just_targets, {"server", "serve", "start", "dev"})


def has_named_surface(
    package_scripts: Dict[str, str],
    make_targets: List[str],
    just_targets: List[str],
    names: set[str],
) -> bool:
    package_names = set(package_scripts)
    make_names = set(make_targets)
    just_names = set(just_targets)
    return bool((package_names | make_names | just_names) & names)


def not_applicable_reason(responsibility: str) -> str:
    reasons = {
        "bootstrap": "no dependency setup surface detected",
        "setup": "no dependency setup surface detected",
        "update": "no dependency update surface detected",
        "server": "no app or service runtime surface detected",
        "test": "no executable or packaged surface detected",
        "cibuild": "no executable, packaged, or validation surface detected",
        "console": "no console or REPL surface detected",
    }
    return reasons[responsibility]


def normalize_doc_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def is_public_doc_path(rel: str) -> bool:
    if rel.startswith("docs/"):
        return True
    return "/" not in rel and rel.upper() in {
        "README.MD",
        "CONTRIBUTING.MD",
        "SECURITY.MD",
        "CHANGELOG.MD",
        "CODE_OF_CONDUCT.MD",
    }


def has_unresolved_marker(line: str) -> bool:
    if re.search(r"^\s*(TODO|FIXME|XXX|TBD)\s*[:\-]", line):
        return True
    upper = line.upper()
    return any(
        phrase in upper
        for phrase in (
            "PRIVATE NOTE",
            "INTERNAL NOTE",
            "CLAIMS TO VERIFY",
        )
    )


def find_broken_markdown_links(root: Path, source: Path, text: str) -> List[str]:
    broken: List[str] = []
    link_pattern = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
    for match in link_pattern.finditer(text):
        raw_target = match.group(1).strip()
        if not raw_target or raw_target.startswith(("#", "http://", "https://", "mailto:", "tel:")):
            continue
        target = raw_target.split()[0].strip("<>")
        target = target.split("#", 1)[0]
        if not target:
            continue
        if target.startswith("/"):
            target_path = (root / target.lstrip("/")).resolve()
        else:
            target_path = (source.parent / target).resolve()
        try:
            target_path.relative_to(root.resolve())
        except ValueError:
            continue
        if not target_path.exists():
            broken.append(f"{source.relative_to(root)} -> {raw_target}")
    return broken


def directory_fingerprint(path: Path) -> Dict[str, str]:
    fingerprint: Dict[str, str] = {}
    for file_path in sorted(iter_files(path)):
        rel = str(file_path.relative_to(path))
        if rel.endswith(".pyc") or rel == ".DS_Store":
            continue
        fingerprint[rel] = safe_read_text(file_path, limit=1_000_000)
    return fingerprint


def is_generated_path(path: str, root: Optional[Path] = None) -> bool:
    normalized = path.replace(os.sep, "/")
    if any(fnmatch.fnmatch(normalized, pattern) for pattern in GENERATED_PATTERNS):
        return True
    if root is None:
        return False
    return is_nested_generated_path(normalized, root)


def is_nested_generated_path(path: str, root: Path) -> bool:
    parts = path.split("/")
    for index, part in enumerate(parts[:-1]):
        if part not in NESTED_GENERATED_DIRS or index == 0:
            continue
        package_root = root.joinpath(*parts[:index])
        if has_direct_dependency_manifest(package_root):
            return True
    return False


def has_direct_dependency_manifest(path: Path) -> bool:
    return any((path / name).is_file() for name in DEPENDENCY_MANIFESTS)


def largest_tracked_files(root: Path, tracked_paths: List[str], limit: int) -> List[Dict[str, Any]]:
    sizes: List[Tuple[int, str]] = []
    for rel in tracked_paths:
        path = root / rel
        try:
            size = path.stat().st_size
        except OSError:
            continue
        sizes.append((size, rel))
    return [
        {"path": rel, "bytes": size, "size": format_bytes(size)}
        for size, rel in sorted(sizes, reverse=True)[:limit]
    ]


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def workflow_command_evidence(root: Path) -> Dict[str, List[str]]:
    evidence: Dict[str, List[str]] = defaultdict(list)
    for workflow in sorted((root / ".github" / "workflows").glob("*.y*ml")):
        rel_workflow = relative_path(root, workflow)
        try:
            text = workflow.read_text(errors="replace")
        except OSError:
            continue
        for directory, command in workflow_step_run_commands(text):
            for scope_path in workflow_command_scope_paths(root, directory or ".", command):
                evidence[scope_path].append(f"{rel_workflow}:{command}")
    return dict(evidence)


def workflow_command_scope_paths(root: Path, directory: str, command: str) -> List[str]:
    chain_parts = split_simple_shell_chain(command.strip())
    if len(chain_parts) > 1:
        scope_paths: List[str] = []
        _, command_records = workflow_shell_command_records(directory, command)
        for command_directory, command_part in command_records:
            scope_paths.extend(workflow_command_scope_paths(root, command_directory, command_part))
        return sorted(set(scope_paths))
    command = command_without_leading_env_assignments(command)
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    directory = directory or "."
    if not tokens:
        return [directory]
    if tokens[0] in SHELL_PREDICATE_COMMANDS:
        return []
    if tokens[0] == "go":
        scope_paths = go_test_scope_paths(root, directory, tokens)
        if scope_paths:
            return scope_paths
        return [] if go_test_has_explicit_package_path_arg(tokens) else [directory]
    if tokens[0] in DIRECT_TEST_PATH_TOOLS:
        scope_paths = direct_test_tool_scope_paths(root, directory, tokens)
        if scope_paths:
            return scope_paths
        return [] if direct_test_tool_has_explicit_path_arg(tokens[0], tokens) else [directory]
    if tokens[0] == "make":
        scope_paths = make_command_scope_paths(root, directory, tokens)
        if scope_paths is None:
            return []
        return scope_paths or [directory]
    if tokens[0] not in {"npm", "pnpm", "yarn", "bun"}:
        return [directory]
    command_base = workflow_command_base(root, directory)
    parsed = parse_package_manager_command(root, command_base, tokens)
    if parsed is None or parsed.package_dirs is None:
        return [] if package_manager_command_has_explicit_scope(tokens) else [directory]
    package_dirs = parsed.package_dirs
    if parsed.script is not None:
        package_dirs = package_dirs_declaring_script(package_dirs, parsed.script)
    scope_paths = package_dirs_to_scope_paths(root, package_dirs)
    if parsed.script is not None:
        return scope_paths
    return scope_paths or [directory]


def workflow_command_base(root: Path, directory: str) -> Path:
    return root if directory in {"", "."} else (root / directory).resolve()


def go_test_scope_paths(root: Path, directory: str, tokens: List[str]) -> List[str]:
    if len(tokens) < 2 or tokens[1] != "test":
        return []
    command_base = workflow_command_base(root, directory)
    package_dirs: List[Path] = []
    args = tokens[2:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in {"--", "-args"}:
            break
        if go_test_option_with_inline_value(arg):
            index += 1
            continue
        if arg in GO_TEST_VALUE_OPTIONS:
            index += 2 if index + 1 < len(args) else 1
            continue
        if arg.startswith("-"):
            index += 1
            continue
        package_dir = go_test_package_path(root, command_base, arg)
        if package_dir is not None:
            package_dirs.append(package_dir)
        index += 1
    return package_dirs_to_scope_paths(root, unique_paths(package_dirs))


def go_test_option_with_inline_value(arg: str) -> bool:
    if not arg.startswith("-") or "=" not in arg:
        return False
    return arg.split("=", 1)[0] in GO_TEST_VALUE_OPTIONS


def go_test_package_path(root: Path, command_base: Path, arg: str) -> Optional[Path]:
    package_arg = arg.strip()
    if package_arg.endswith("/..."):
        package_arg = package_arg[:-4] or "."
    if not go_test_package_arg_looks_like_path(package_arg):
        return None
    resolved = resolve_repo_path(root, command_base, package_arg)
    if resolved is None or not resolved.is_dir():
        return None
    return nearest_inventory_boundary(root, resolved)


def go_test_package_arg_looks_like_path(arg: str) -> bool:
    return arg in {".", ".."} or arg.startswith(("./", "../")) or "/" in arg


def go_test_has_explicit_package_path_arg(tokens: List[str]) -> bool:
    if len(tokens) < 2 or tokens[1] != "test":
        return False
    args = tokens[2:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in {"--", "-args"}:
            break
        if go_test_option_with_inline_value(arg):
            index += 1
            continue
        if arg in GO_TEST_VALUE_OPTIONS:
            index += 2 if index + 1 < len(args) else 1
            continue
        if arg.startswith("-"):
            index += 1
            continue
        if go_test_package_arg_looks_like_path(arg.strip().removesuffix("/...")):
            return True
        index += 1
    return False


def direct_test_tool_scope_paths(root: Path, directory: str, tokens: List[str]) -> List[str]:
    command_base = workflow_command_base(root, directory)
    package_dirs: List[Path] = []
    args = tokens[1:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            index += 1
            continue
        if direct_test_tool_option_with_inline_value(tokens[0], arg):
            index += 1
            continue
        if arg in DIRECT_TEST_VALUE_OPTIONS.get(tokens[0], set()):
            index += 2 if index + 1 < len(args) else 1
            continue
        if arg.startswith("-"):
            index += 1
            continue
        package_dir = direct_test_tool_package_path(root, command_base, arg)
        if package_dir is not None:
            package_dirs.append(package_dir)
        index += 1
    return package_dirs_to_scope_paths(root, unique_paths(package_dirs))


def direct_test_tool_has_explicit_path_arg(tool: str, tokens: List[str]) -> bool:
    args = tokens[1:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            index += 1
            continue
        if direct_test_tool_option_with_inline_value(tool, arg):
            index += 1
            continue
        if arg in DIRECT_TEST_VALUE_OPTIONS.get(tool, set()):
            index += 2 if index + 1 < len(args) else 1
            continue
        if arg.startswith("-"):
            index += 1
            continue
        return True
    return False


def direct_test_tool_option_with_inline_value(tool: str, arg: str) -> bool:
    if not arg.startswith("-") or "=" not in arg:
        return False
    return arg.split("=", 1)[0] in DIRECT_TEST_VALUE_OPTIONS.get(tool, set())


def direct_test_tool_package_path(root: Path, command_base: Path, arg: str) -> Optional[Path]:
    path_arg = arg.split("::", 1)[0]
    if not path_arg:
        return None
    resolved = resolve_repo_path(root, command_base, path_arg)
    if resolved is None or not resolved.exists():
        return None
    return nearest_inventory_boundary(root, resolved)


def make_command_scope_paths(root: Path, directory: str, tokens: List[str]) -> Optional[List[str]]:
    command_base = workflow_command_base(root, directory)
    parsed = parse_make_command(root, command_base, tokens[1:])
    if parsed is None:
        return []
    makefile, targets = parsed
    if parsed_make_command_target_missing(root, makefile, targets, read_make_targets(default_makefile(root))):
        return [] if makefile.parent.resolve() == root.resolve() and not makefile.is_file() else None
    boundary = nearest_inventory_boundary(root, makefile.parent)
    if boundary is None:
        return []
    return package_dirs_to_scope_paths(root, [boundary])


def package_manager_command_has_explicit_scope(tokens: List[str]) -> bool:
    if not tokens:
        return False
    tool = tokens[0]
    args = tokens[1:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--":
            break
        if package_manager_arg_is_scope_option(tool, arg):
            return True
        if is_package_manager_no_value_option(arg, tool):
            index += 1
            continue
        value_option = package_manager_value_option_value(tool, args, index)
        if value_option is not None:
            index = value_option
            continue
        if arg.startswith("-"):
            return package_manager_args_contain_scope_option(tool, args, index + 1)
        return tool == "yarn" and normalize_package_manager_command(tool, arg) == "workspace"
    return False


def package_manager_parse_failure_is_invalid_scoped_command(tokens: List[str]) -> bool:
    if not package_manager_command_has_explicit_scope(tokens):
        return False
    tool = tokens[0]
    invalid_options = PACKAGE_MANAGER_INVALID_SCOPED_OPTIONS.get(tool, set())
    for arg in tokens[1:]:
        if arg == "--":
            return False
        if arg in invalid_options or any(arg.startswith(f"{option}=") for option in invalid_options):
            return True
    return False


def package_manager_parse_failure_target_missing(root: Path, command_base: Path, tokens: List[str]) -> bool:
    return package_manager_parse_failure_is_invalid_scoped_command(
        tokens
    ) or package_manager_parse_failure_has_unresolved_directory(root, command_base, tokens)


def package_manager_parse_failure_has_unresolved_directory(root: Path, command_base: Path, tokens: List[str]) -> bool:
    if not tokens:
        return False
    tool = tokens[0]
    args = tokens[1:]
    index = 0
    while index < len(args):
        if args[index] == "--":
            return False
        directory_option = package_manager_directory_option_value(tool, args, index)
        if directory_option is not None:
            value, index = directory_option
            if resolve_repo_path(root, command_base, value) is None:
                return True
            continue
        if args[index] in PACKAGE_MANAGER_DIRECTORY_OPTIONS.get(tool, set()):
            return True
        index += 1
    return False


def package_manager_args_contain_scope_option(tool: str, args: List[str], start: int) -> bool:
    for arg in args[start:]:
        if arg == "--":
            return False
        if package_manager_arg_is_scope_option(tool, arg):
            return True
    return False


def package_manager_arg_is_scope_option(tool: str, arg: str) -> bool:
    options = (
        PACKAGE_MANAGER_DIRECTORY_OPTIONS.get(tool, set())
        | PACKAGE_MANAGER_WORKSPACE_OPTIONS.get(tool, set())
        | PACKAGE_MANAGER_ALL_WORKSPACES_OPTIONS.get(tool, set())
    )
    if arg in options:
        return True
    if any(arg.startswith(f"{option}=") for option in options):
        return True
    return tool == "pnpm" and arg.startswith("-C") and arg != "-C"


def nearest_inventory_boundary(root: Path, path: Path) -> Optional[Path]:
    current = path if path.is_dir() else path.parent
    root = root.resolve()
    while True:
        if any((current / name).exists() for name in BOUNDARY_MANIFESTS):
            return current
        if current == root:
            return None
        try:
            current.relative_to(root)
        except ValueError:
            return None
        current = current.parent


def package_dirs_to_scope_paths(root: Path, package_dirs: List[Path]) -> List[str]:
    scope_paths: List[str] = []
    for package_dir in package_dirs:
        try:
            rel = relative_path(root, package_dir)
        except ValueError:
            continue
        if rel not in scope_paths:
            scope_paths.append(rel)
    return scope_paths


def package_dirs_declaring_script(package_dirs: List[Path], script: str) -> List[Path]:
    return [
        package_dir
        for package_dir in package_dirs
        if script in read_package_scripts(package_dir / "package.json")
    ]


def workflow_step_run_commands(text: str) -> List[Tuple[str, str]]:
    lines = text.splitlines()
    commands: List[Tuple[str, str]] = []
    workflow_default_directory = "."
    jobs_indent: Optional[int] = None
    job_entry_indent: Optional[int] = None
    current_job_indent: Optional[int] = None
    current_job_default_directory = "."
    current_steps_indent: Optional[int] = None
    current_step_entry_indent: Optional[int] = None
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if jobs_indent is not None and stripped and indent <= jobs_indent and not stripped.startswith("#") and not stripped.startswith("jobs:"):
            jobs_indent = None
            job_entry_indent = None
            current_job_indent = None
            current_job_default_directory = workflow_default_directory
            current_steps_indent = None
            current_step_entry_indent = None
        if current_steps_indent is not None and stripped and indent <= current_steps_indent and not stripped.startswith("#") and not stripped.startswith("steps:"):
            current_steps_indent = None
            current_step_entry_indent = None
        if indent == 0 and stripped.startswith("defaults:"):
            default_directory = parse_defaults_run_directory(lines, index, indent)
            if default_directory is not None:
                workflow_default_directory = default_directory
                if current_job_indent is None:
                    current_job_default_directory = default_directory
        elif jobs_indent is not None and current_job_indent is not None and indent > current_job_indent and stripped.startswith("defaults:"):
            default_directory = parse_defaults_run_directory(lines, index, indent)
            if default_directory is not None:
                current_job_default_directory = default_directory
        if indent == 0 and stripped.startswith("jobs:"):
            jobs_indent = indent
            job_entry_indent = None
            current_job_indent = None
            current_job_default_directory = workflow_default_directory
            current_steps_indent = None
            current_step_entry_indent = None
            index += 1
            continue
        if jobs_indent is not None and stripped.endswith(":") and not stripped.startswith("- ") and indent > jobs_indent:
            if job_entry_indent is None:
                job_entry_indent = indent
            if indent == job_entry_indent:
                current_job_indent = indent
                current_job_default_directory = workflow_default_directory
                current_steps_indent = None
                current_step_entry_indent = None
        if current_job_indent is not None and stripped.startswith("steps:") and indent > current_job_indent:
            current_steps_indent = indent
            current_step_entry_indent = None
            index += 1
            continue
        if current_steps_indent is None or not stripped.startswith("- ") or indent <= current_steps_indent:
            index += 1
            continue
        if current_step_entry_indent is None:
            current_step_entry_indent = indent
        if indent != current_step_entry_indent:
            index += 1
            continue
        step_end = index + 1
        while step_end < len(lines):
            next_line = lines[step_end]
            next_stripped = next_line.lstrip()
            next_indent = len(next_line) - len(next_stripped)
            if next_stripped.startswith("- ") and next_indent == indent:
                break
            if next_stripped and next_indent <= current_steps_indent and not next_stripped.startswith("#"):
                break
            step_end += 1
        relative_lines = [line[indent + 2:]]
        for offset in range(index + 1, step_end):
            raw = lines[offset]
            relative_lines.append(raw[indent + 2:] if len(raw) >= indent + 2 else "")
        default_directory = current_job_default_directory if current_job_indent is not None else workflow_default_directory
        commands.extend(parse_workflow_step(relative_lines, default_directory))
        index = step_end
    return commands


def parse_defaults_run_directory(lines: List[str], start_index: int, defaults_indent: int) -> Optional[str]:
    run_indent: Optional[int] = None
    index = start_index + 1
    while index < len(lines):
        line = lines[index]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped and indent <= defaults_indent and not stripped.startswith("#"):
            break
        if run_indent is not None and stripped and indent <= run_indent and not stripped.startswith("#"):
            run_indent = None
        if run_indent is None and stripped.startswith("run:") and indent > defaults_indent:
            run_indent = indent
            index += 1
            continue
        if run_indent is not None and stripped.startswith("working-directory:") and indent > run_indent:
            return normalize_workflow_directory(workflow_scalar_value(stripped.split(":", 1)[1]))
        index += 1
    return None


def parse_workflow_step(lines: List[str], default_directory: str = ".") -> List[Tuple[str, str]]:
    directory = workflow_step_directory(lines, default_directory)
    commands: List[Tuple[str, str]] = []
    step_key_indent = workflow_step_key_indent(lines)
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if leading_spaces(line) != step_key_indent:
            index += 1
            continue
        if stripped.startswith("working-directory:"):
            index += 1
            continue
        if stripped.startswith("run:"):
            value = line.split(":", 1)[1].lstrip()
            block_style = workflow_block_scalar_style(value)
            if block_style is not None:
                block_lines: List[str] = []
                index += 1
                while index < len(lines):
                    block_line = lines[index]
                    if block_line.strip() and leading_spaces(block_line) <= step_key_indent:
                        break
                    block_lines.append(block_line)
                    index += 1
                if block_style == "literal":
                    commands.extend(workflow_literal_block_command_records(directory, block_lines))
                else:
                    block_commands = workflow_block_commands(block_lines, block_style)
                    for command in block_commands:
                        _, records = workflow_shell_command_records(directory, command)
                        commands.extend(records)
                continue
            command = workflow_scalar_value(value)
            if command:
                _, records = workflow_shell_command_records(directory, command)
                commands.extend(records)
        index += 1
    return commands


def workflow_step_directory(lines: List[str], default_directory: str = ".") -> str:
    directory = normalize_workflow_directory(default_directory)
    step_key_indent = workflow_step_key_indent(lines)
    for line in lines:
        stripped = line.strip()
        if leading_spaces(line) != step_key_indent:
            continue
        if stripped.startswith("working-directory:"):
            directory = normalize_workflow_directory(workflow_scalar_value(stripped.split(":", 1)[1]))
    return directory


def workflow_step_key_indent(lines: List[str]) -> int:
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return leading_spaces(line)
    return 0


def workflow_block_scalar_style(value: str) -> Optional[str]:
    header = value.strip()
    if header in {"|", "|-", "|+"}:
        return "literal"
    if header in {">", ">-", ">+"}:
        return "folded"
    return None


def workflow_block_commands(lines: List[str], block_style: str) -> List[str]:
    non_empty = [line for line in lines if line.strip()]
    if not non_empty:
        return []
    base_indent = min(leading_spaces(line) for line in non_empty)
    if block_style == "folded":
        commands: List[str] = []
        paragraph: List[Tuple[int, str]] = []
        for line in lines:
            if not line.strip():
                if paragraph:
                    commands.extend(folded_workflow_paragraph_commands(paragraph, base_indent))
                    paragraph = []
                continue
            indent = leading_spaces(line)
            command = line[base_indent:].strip()
            if not command or command.startswith("#"):
                continue
            paragraph.append((indent, command))
        if paragraph:
            commands.extend(folded_workflow_paragraph_commands(paragraph, base_indent))
        return commands
    commands = []
    for line in lines:
        if not line.strip():
            continue
        command = line[base_indent:].strip()
        if command and not command.startswith("#"):
            commands.append(command)
    return commands


def workflow_literal_block_command_records(
    directory: str,
    lines: List[str],
) -> List[Tuple[str, str]]:
    non_empty = [line for line in lines if line.strip()]
    if not non_empty:
        return []
    base_indent = min(leading_spaces(line) for line in non_empty)
    current_directory: Optional[str] = normalize_workflow_directory(directory)
    records: List[Tuple[str, str]] = []
    for line in lines:
        if not line.strip():
            continue
        indent = leading_spaces(line)
        command = line[base_indent:].strip()
        if not command or command.startswith("#"):
            continue
        next_directory, command_records = workflow_shell_command_records(current_directory, command)
        records.extend(command_records)
        if indent == base_indent:
            current_directory = next_directory
    return records


def workflow_shell_command_records(
    directory: Optional[str],
    command: str,
) -> Tuple[Optional[str], List[Tuple[str, str]]]:
    if directory is None:
        return None, []
    current_directory: Optional[str] = normalize_workflow_directory(directory)
    records: List[Tuple[str, str]] = []
    for part in split_simple_shell_chain(command):
        if current_directory is None:
            break
        changed_directory = workflow_simple_cd_directory(current_directory, part)
        if changed_directory is not None:
            current_directory = changed_directory
            continue
        if simple_cd_command_target(part) is not None:
            current_directory = None
            break
        records.append((current_directory, part))
    return current_directory, records


def workflow_simple_cd_directory(current_directory: str, command: str) -> Optional[str]:
    target = simple_cd_command_target(command)
    if target is None:
        return None
    if not target or target == "-" or target.startswith(("/", "~", "$")) or any(char in target for char in "*?["):
        return None
    base = "" if current_directory in {"", "."} else current_directory
    normalized = normalize_workflow_directory(posixpath.join(base, target))
    if normalized == ".." or normalized.startswith("../"):
        return None
    return normalized


def folded_workflow_paragraph_commands(
    paragraph: List[Tuple[int, str]],
    base_indent: int,
) -> List[str]:
    if any(indent > base_indent for indent, _ in paragraph):
        return [command for _, command in paragraph]
    return [" ".join(command for _, command in paragraph)]


def workflow_scalar_value(value: str) -> str:
    return strip_unquoted_yaml_comment(value).strip().strip("\"'")


def strip_unquoted_yaml_comment(value: str) -> str:
    quote: Optional[str] = None
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if quote == '"' and char == "\\":
            escaped = True
            continue
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            continue
        if char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index]
    return value


def normalize_workflow_directory(value: str) -> str:
    normalized = posixpath.normpath(value.strip() or ".")
    return "." if normalized in {"", "."} else normalized


def leading_spaces(text: str) -> int:
    return len(text) - len(text.lstrip(" "))


def classify_workflow_name(name: str) -> List[str]:
    words = set(re.split(r"[^a-z0-9]+", name.lower()))
    words.discard("")
    matches = set(classify_command_name(name))
    direct_matches = {
        "pytest": "test",
        "tox": "test",
        "ruff": "lint",
        "mypy": "typecheck",
        "pyright": "typecheck",
        "tsc": "typecheck",
    }
    if name.lower() in direct_matches:
        matches.add(direct_matches[name.lower()])
    if words & {"build", "package"}:
        matches.add("build")
    if words & {"lint", "fmt", "format"}:
        matches.add("lint")
    if words & {"typecheck", "types", "mypy", "pyright", "tsc"}:
        matches.add("typecheck")
    if words & {"docs", "doc", "documentation"}:
        matches.add("docs")
    return sorted(matches)


def workflow_command_responsibilities(command: str) -> List[str]:
    chain_parts = split_simple_shell_chain(command.strip())
    if len(chain_parts) > 1:
        matches = set()
        for part in chain_parts:
            matches.update(workflow_command_responsibilities(part))
        return sorted(matches)
    command = command_without_leading_env_assignments(command)
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return []
    tokens = normalize_pip_command_tokens(tokens)
    tool = tokens[0]
    if tool in SHELL_PREDICATE_COMMANDS:
        return []
    if tool in {"npm", "pnpm", "yarn", "bun"}:
        command_args = package_manager_builtin_command_args(tokens)
        script = package_manager_script_from_args(tool, command_args)
        if script:
            return classify_workflow_name(script)
        builtin_command = package_manager_builtin_command(tokens)
        if builtin_command:
            return classify_workflow_name(builtin_command)
    if tool in {"make", "just"}:
        if tool == "make":
            matches = set()
            for target in make_command_targets_for_responsibility(tokens[1:]):
                matches.update(classify_workflow_name(target))
            if matches:
                return sorted(matches)
        target = first_non_option(tokens[1:])
        if target is not None:
            return classify_workflow_name(target)
    if tool in {"go", "cargo"} and len(tokens) > 1:
        return classify_workflow_name(tokens[1])
    if tool in {"pytest", "tox", "mypy", "pyright", "ruff"}:
        return classify_workflow_name(tool)
    if tool in {"python", "python3"} and len(tokens) > 2 and tokens[1] == "-m":
        return classify_workflow_name(tokens[2])
    return classify_workflow_name(tool)


def make_command_targets_for_responsibility(args: List[str]) -> List[str]:
    parsed = parse_make_command(Path("/"), Path("/"), args)
    if parsed is None:
        return []
    _, targets = parsed
    return targets


def workflow_command_matches_boundary(command: str, boundary: Optional[Dict[str, Any]]) -> bool:
    if boundary is None or boundary["kind"] != "docker-service":
        return True
    return is_docker_service_command(command, boundary["path"])


def is_docker_service_command(command: str, boundary_path: str) -> bool:
    command = command_without_leading_env_assignments(command)
    search_text = command.lower()
    docker_markers = ("docker", "dockerfile", "compose", "podman", "buildah", "container")
    if any(marker in search_text for marker in docker_markers):
        return True
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return False
    tool = tokens[0].lower()
    docker_tools = {"buildah", "docker", "docker-compose", "nerdctl", "podman"}
    if tool in docker_tools:
        return True
    boundary_tokens = {boundary_path.lower(), posixpath.basename(boundary_path).lower(), "dockerfile"}
    return any(token.lower() in boundary_tokens for token in tokens[1:])


def repo_owned_candidate_matches_boundary(
    candidate: str,
    boundary: Optional[Dict[str, Any]],
    script_name: str = "",
) -> bool:
    if boundary is None or boundary["kind"] != "docker-service":
        return True
    search_text = " ".join(part for part in (candidate, script_name) if part).lower()
    docker_markers = ("docker", "dockerfile", "compose", "podman", "buildah", "container")
    return any(marker in search_text for marker in docker_markers)


def workflow_evidence_for_responsibility(
    path: str,
    responsibility: str,
    workflow_commands: Dict[str, List[str]],
    boundary: Optional[Dict[str, Any]] = None,
) -> List[str]:
    evidence = []
    for item in workflow_commands.get(path, []):
        _, _, command = item.partition(":")
        if not workflow_command_matches_boundary(command, boundary):
            continue
        if responsibility in workflow_command_responsibilities(command):
            evidence.append(item)
    return evidence


def lifecycle_repo_owned_evidence(
    root: Path,
    path: str,
    responsibility: str,
    scripts_check: Dict[str, Any],
    documented_command_directories: DocumentedCommandDirectories,
    boundary: Optional[Dict[str, Any]] = None,
) -> List[str]:
    evidence: List[str] = []
    responsibility_info = scripts_check.get("responsibilities", {}).get(responsibility)
    if responsibility_info:
        documented_candidates = set(scripts_check.get("documented_commands", {}).get(responsibility, []))
        evidence.extend(
            candidate
            for candidate in responsibility_info.get("candidates", [])
            if lifecycle_candidate_matches_path(
                root,
                candidate,
                path,
                responsibility,
                documented_candidates,
                documented_command_directories,
            )
            and repo_owned_candidate_matches_boundary(candidate, boundary)
        )
    for script, sources in scripts_check.get("package_script_sources", {}).items():
        if responsibility not in classify_workflow_name(script):
            continue
        evidence.extend(
            source
            for source in sources
            if lifecycle_candidate_scope_path(source) == path
            and repo_owned_candidate_matches_boundary(source, boundary, script)
        )
    return sorted(set(evidence))


def lifecycle_documented_evidence(
    root: Path,
    path: str,
    responsibility: str,
    scripts_check: Dict[str, Any],
    documented_command_directories: DocumentedCommandDirectories,
    boundary: Optional[Dict[str, Any]] = None,
) -> List[str]:
    documented_candidates = set(scripts_check.get("documented_commands", {}).get(responsibility, []))
    return sorted(
        candidate
        for candidate in documented_candidates
        if lifecycle_candidate_matches_path(
            root,
            candidate,
            path,
            responsibility,
            documented_candidates,
            documented_command_directories,
        )
        and repo_owned_candidate_matches_boundary(candidate, boundary)
    )


def lifecycle_candidate_matches_path(
    root: Path,
    candidate: str,
    path: str,
    responsibility: str,
    documented_candidates: set[str],
    documented_command_directories: DocumentedCommandDirectories,
) -> bool:
    if lifecycle_candidate_scope_path(candidate) == path:
        if path == "." and documented_candidate_has_explicit_package_manager_scope(candidate):
            return path in documented_candidate_scope_paths(
                root,
                candidate,
                responsibility,
                documented_command_directories,
                include_root=True,
            )
        return True
    if candidate not in documented_candidates:
        return False
    return path in documented_candidate_scope_paths(
        root,
        candidate,
        responsibility,
        documented_command_directories,
    )


def documented_candidate_scope_paths(
    root: Path,
    candidate: str,
    responsibility: str,
    documented_command_directories: DocumentedCommandDirectories,
    include_root: bool = False,
) -> List[str]:
    _, _, command = candidate.partition(":")
    if not command:
        return []
    scope_paths: List[str] = []
    for directory in documented_command_directories.get(candidate, {}).get(responsibility, ["."]):
        for scope_path in workflow_command_scope_paths(root, directory, command):
            if (include_root or scope_path != ".") and scope_path not in scope_paths:
                scope_paths.append(scope_path)
    return scope_paths


def documented_candidate_has_explicit_package_manager_scope(candidate: str) -> bool:
    _, _, command = candidate.partition(":")
    command = command_without_leading_env_assignments(command)
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    return bool(
        tokens
        and tokens[0] in {"npm", "pnpm", "yarn", "bun"}
        and package_manager_command_has_explicit_scope(tokens)
    )


def lifecycle_candidate_scope_path(candidate: str) -> str:
    source_path, _, _ = candidate.partition(":")
    name = posixpath.basename(source_path)
    if name in {
        "package.json",
        "GNUmakefile",
        "makefile",
        "Makefile",
        ".justfile",
        "justfile",
        "Justfile",
    }:
        parent = posixpath.dirname(source_path)
        return "." if parent in {"", "."} else parent
    return "."


def lifecycle_cell(
    root: Path,
    path: str,
    responsibility: str,
    scripts_check: Dict[str, Any],
    workflow_commands: Dict[str, List[str]],
    documented_command_directories: DocumentedCommandDirectories,
    boundary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    evidence = lifecycle_repo_owned_evidence(
        root, path, responsibility, scripts_check, documented_command_directories, boundary
    )
    documented_evidence = lifecycle_documented_evidence(
        root, path, responsibility, scripts_check, documented_command_directories, boundary
    )
    status = "missing"
    responsibility_info = scripts_check.get("responsibilities", {}).get(responsibility)
    if responsibility_info and path == ".":
        root_status = responsibility_info.get("status", "missing")
        if root_status == "not_applicable":
            status = root_status
        elif root_status in {"present", "documented"} and evidence:
            status = root_status
    elif evidence:
        status = "documented" if set(evidence) <= set(documented_evidence) else "present"
    evidence.extend(workflow_evidence_for_responsibility(path, responsibility, workflow_commands, boundary))
    if status == "not_applicable" and evidence:
        status = "present"
    if status == "missing" and evidence:
        status = "present"
    return {"status": status, "evidence": sorted(set(evidence))}


def lifecycle_scope_path(boundary: Dict[str, Any]) -> str:
    if boundary["kind"] != "docker-service":
        return boundary["path"]
    parent = posixpath.dirname(boundary["path"])
    return "." if parent in {"", "."} else parent


def lifecycle_server_cell(
    root: Path,
    boundary: Dict[str, Any],
    scripts_check: Dict[str, Any],
    workflow_commands: Dict[str, List[str]],
    documented_command_directories: DocumentedCommandDirectories,
) -> Dict[str, Any]:
    if boundary["kind"] in {"docs-site", "codex-skill"}:
        return {"status": "not_applicable", "evidence": []}
    cell = lifecycle_cell(
        root,
        lifecycle_scope_path(boundary),
        "server",
        scripts_check,
        workflow_commands,
        documented_command_directories,
        boundary,
    )
    if boundary["kind"] in {"go-package", "python-package", "rust-crate", "swift-package"}:
        if cell["status"] == "missing" and not cell["evidence"]:
            return {"status": "not_applicable", "evidence": []}
    return cell


def ci_coverage_cell(
    path: str,
    workflow_commands: Dict[str, List[str]],
    boundary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    evidence = [
        item
        for item in workflow_commands.get(path, [])
        if workflow_command_matches_boundary(item.partition(":")[2], boundary)
    ]
    return {
        "status": "present" if evidence else "missing",
        "evidence": sorted(set(evidence)),
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    checks = report["checks"]
    lines.extend(render_verdict(report))
    lines.extend(render_findings(report["findings"]))
    lines.extend(render_repository_shape(checks["repository_shape"]))
    lines.extend(render_repository_inventory(checks["repository_inventory"]))
    lines.extend(render_lifecycle_gate_matrix(checks["lifecycle_gate_matrix"]))
    lines.extend(render_documentation(checks["documentation"]))
    lines.extend(render_scripts(checks["scripts"]))
    lines.extend(render_validation(checks["validation"]))
    lines.extend(render_packaging(checks["packaging"]))
    lines.extend(render_hygiene(checks["hygiene"]))
    lines.extend(render_commands(report["commands_run"]))
    lines.extend(render_not_checked(report["not_checked"]))
    return "\n".join(lines) + "\n"


def render_verdict(report: Dict[str, Any]) -> List[str]:
    verdict = report["verdict"]
    return [
        "## Verdict",
        f"- Repository: `{report['repo']}`",
        f"- Ready to proceed: {verdict['ready_to_proceed']}",
        f"- Blocking issues: {verdict['blocking_issues']}",
        f"- Recommended first fix: {verdict['recommended_first_fix']}",
        "",
    ]


def render_findings(findings: List[Dict[str, Any]]) -> List[str]:
    lines = ["## Findings"]
    if findings:
        for finding in findings:
            lines.append(f"- {finding['severity']}: {finding['title']}")
            lines.append(f"  - Scope: {finding['path']} ({finding['scope_type']})")
            lines.append(f"  - Evidence state: {finding['evidence_state']}")
            for evidence in finding["evidence"]:
                lines.append(f"  - Evidence: {evidence}")
            lines.append(f"  - Impact: {finding['impact']}")
            lines.append(f"  - Fix shape: {finding['fix_shape']}")
    else:
        lines.append("- None")
    lines.append("")
    return lines


def render_repository_shape(shape: Dict[str, Any]) -> List[str]:
    return [
        "## Repository Shape",
        f"- README: {format_present(shape['readmes'])}",
        f"- Instructions: {format_present(shape['instructions'])}",
        f"- Docs directory: {yes_no(shape['has_docs_dir'])}",
        "- Scripts directories: "
        f"scripts={yes_no(shape['has_scripts_dir'])}, script={yes_no(shape['has_script_dir'])}",
        f"- CI workflows: {yes_no(shape['has_ci_workflows'])}",
        f"- Manifests: {format_present(shape['manifests'])}",
        "",
    ]


def render_repository_inventory(inventory: Dict[str, Any]) -> List[str]:
    lines = [
        "## Repository Inventory",
        f"- Classification: {inventory['classification']}",
        f"- Purpose: {inventory['purpose']}",
        f"- Ecosystems: {format_present(inventory['ecosystems'])}",
        f"- Suggested overlays: {format_present(inventory['suggested_overlays'])}",
        "- Boundaries:",
    ]
    for boundary in inventory["boundaries"]:
        evidence = ", ".join(boundary["evidence"])
        lines.append(
            f"  - {boundary['path']}: {boundary['kind']} ({boundary['ecosystem']}, {boundary['scope_type']}) - {evidence}"
        )
    lines.append("")
    return lines


def render_lifecycle_gate_matrix(matrix: Dict[str, Any]) -> List[str]:
    lines = ["## Lifecycle Gate Matrix"]
    for row in matrix["rows"]:
        lines.append(f"- {row['path']} ({row['kind']}, {row['scope_type']})")
        for key in [
            "setup",
            "focused_test",
            "full_validation",
            "lint_format",
            "typecheck_static",
            "build_package",
            "server",
            "docs_release",
            "ci_coverage",
        ]:
            cell = row[key]
            evidence = f" - {', '.join(cell['evidence'])}" if cell["evidence"] else ""
            lines.append(f"  - {key}: {cell['status']}{evidence}")
    lines.append("")
    return lines


def render_documentation(documentation: Dict[str, Any]) -> List[str]:
    return [
        "## Documentation",
        f"- Markdown files: {len(documentation['markdown_files'])}",
        f"- Broken local links: {len(documentation['broken_local_links'])}",
        f"- Duplicate-looking doc groups: {len(documentation['duplicate_doc_groups'])}",
        f"- Unresolved markers: {len(documentation['unresolved_markers'])}",
        "",
    ]


def render_scripts(scripts: Dict[str, Any]) -> List[str]:
    lines = ["## Scripts"]
    for name, item in scripts["responsibilities"].items():
        if item["candidates"]:
            candidates = ", ".join(item["candidates"])
        elif item["status"] == "not_applicable":
            candidates = item["reason"]
        else:
            candidates = "missing"
        lines.append(f"- {name}: {item['status']} - {candidates}")
    lines.append("")
    return lines


def render_validation(validation: Dict[str, Any]) -> List[str]:
    return [
        "## Validation",
        f"- Focused tests: {yes_no(validation['has_focused_tests'])}",
        f"- Full gate: {yes_no(validation['has_full_gate'])}",
        f"- Python tests: {format_present(validation['python_tests'])}",
        f"- Shell scripts: {format_present(validation['shell_scripts'])}",
        f"- CI workflows: {format_present(validation['ci_workflows'])}",
        "",
    ]


def render_packaging(packaging: Dict[str, Any]) -> List[str]:
    return [
        "## Packaging",
        f"- Skills directory: {yes_no(packaging['has_skills_dir'])}",
        f"- Plugin mirror: {yes_no(packaging['has_plugin_skill_mirror'])}",
        f"- Missing skill mirrors: {format_present(packaging['missing_skill_mirrors'])}",
        f"- Drifted skill mirrors: {format_present(packaging['drifted_skill_mirrors'])}",
        "",
    ]


def render_hygiene(hygiene: Dict[str, Any]) -> List[str]:
    return [
        "## Hygiene",
        f"- Branch: {hygiene['branch'] or 'unknown'}",
        f"- Dirty entries: {len(hygiene['dirty_entries'])}",
        f"- Tracked generated files: {format_present(hygiene['tracked_generated'])}",
        f"- Ignored entries sampled: {hygiene['ignored_entries_count']}",
        f"- Largest tracked files: {format_large_files(hygiene['largest_tracked_files'])}",
        "",
    ]


def render_commands(commands: List[Dict[str, str]]) -> List[str]:
    lines = ["## Commands Run"]
    for item in commands:
        lines.append(f"- `{item['command']}` - {item['result']}")
    lines.append("")
    return lines


def render_not_checked(items: List[Dict[str, str]]) -> List[str]:
    lines = ["## Not Checked"]
    for item in items:
        lines.append(f"- {item['area']}: {item['reason']}")
    return lines


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def format_present(items: List[str]) -> str:
    return ", ".join(items) if items else "missing"


def format_large_files(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "none"
    return ", ".join(f"{item['path']} ({item['size']})" for item in items[:5])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a read-only repository health audit.")
    parser.add_argument("--repo", default=".", help="Repository path to audit. Defaults to the current directory.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format. Defaults to markdown.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = Audit(Path(args.repo)).run()
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
