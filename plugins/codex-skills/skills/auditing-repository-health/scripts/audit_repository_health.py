#!/usr/bin/env python3
"""Read-only repository health audit."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import subprocess
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


@dataclass
class Finding:
    severity: str
    title: str
    evidence: List[str]
    impact: str
    fix_shape: str


class Audit:
    def __init__(self, repo: Path) -> None:
        self.requested_repo = repo.resolve()
        self.commands_run: List[Dict[str, str]] = []
        self.not_checked: List[Dict[str, str]] = []
        self.findings: List[Finding] = []

    def run(self) -> Dict[str, Any]:
        root = self.find_repo_root()
        checks: Dict[str, Any] = {}
        checks["repository_shape"] = self.check_repository_shape(root)
        checks["documentation"] = self.check_documentation(root)
        checks["scripts"] = self.check_scripts(root)
        checks["validation"] = self.check_validation(root, checks["scripts"])
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
            return Path(result.stdout.strip()).resolve()
        self.add_not_checked("git metadata", "path is not inside a Git worktree")
        return self.requested_repo

    def add_finding(
        self,
        severity: str,
        title: str,
        evidence: Iterable[str],
        impact: str,
        fix_shape: str,
    ) -> None:
        evidence_list = [item for item in evidence if item]
        for finding in self.findings:
            if finding.title == title:
                finding.evidence.extend(item for item in evidence_list if item not in finding.evidence)
                return
        self.findings.append(Finding(severity, title, evidence_list, impact, fix_shape))

    def add_not_checked(self, area: str, reason: str) -> None:
        item = {"area": area, "reason": reason}
        if item not in self.not_checked:
            self.not_checked.append(item)

    def git(self, args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        command = ["git", *args]
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
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
            "has_ci_workflows": workflows_dir.is_dir() and any(workflows_dir.iterdir()),
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
        make_targets = read_make_targets(root / "Makefile")
        responsibilities: Dict[str, Dict[str, Any]] = {}

        for responsibility, candidates in RESPONSIBILITY_PATHS.items():
            found = [path for path in candidates if (root / path).exists()]
            found.extend(
                f"package.json:{script}"
                for script in sorted(package_scripts)
                if script in PACKAGE_SCRIPT_MAP[responsibility]
            )
            found.extend(
                f"Makefile:{target}"
                for target in sorted(make_targets)
                if target in PACKAGE_SCRIPT_MAP[responsibility] or target == responsibility
            )
            responsibilities[responsibility] = {
                "status": "present" if found else "missing",
                "candidates": sorted(found),
            }

        if responsibilities["setup"]["status"] == "missing" and responsibilities["bootstrap"]["status"] == "missing":
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
            "make_targets": sorted(make_targets),
        }

    def check_validation(self, root: Path, scripts_check: Dict[str, Any]) -> Dict[str, Any]:
        workflows_dir = root / ".github" / "workflows"
        python_tests = sorted(str(path.relative_to(root)) for path in iter_files(root, "test_*.py"))
        shell_scripts = []
        if (root / "scripts").is_dir():
            shell_scripts = sorted(str(path.relative_to(root)) for path in (root / "scripts").glob("*.sh"))
        workflows = []
        if workflows_dir.is_dir():
            workflows = sorted(str(path.relative_to(root)) for path in workflows_dir.glob("*") if path.is_file())
        validation_candidates = scripts_check["responsibilities"]["cibuild"]["candidates"]

        if not validation_candidates and not workflows:
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
            "has_full_gate": bool(validation_candidates or workflows),
        }

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
        if not skills_dir.is_dir():
            return result

        source_skills = sorted(path.name for path in skills_dir.iterdir() if path.is_dir())
        mirror_skills = []
        if mirror_dir.is_dir():
            mirror_skills = sorted(path.name for path in mirror_dir.iterdir() if path.is_dir())
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
        status_result = self.git(["status", "--short", "--branch", "--untracked-files=all"], root)
        count_result = self.git(["count-objects", "-vH"], root)
        tracked_result = self.git(["ls-files", "-z"], root)
        ignored_result = self.git(["status", "--ignored", "--short"], root)

        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None
        status_lines = status_result.stdout.splitlines() if status_result.returncode == 0 else []
        tracked_paths = tracked_result.stdout.split("\0") if tracked_result.returncode == 0 else []
        tracked_paths = [path for path in tracked_paths if path]
        dirty_lines = [line for line in status_lines if not line.startswith("##")]
        tracked_generated = sorted(path for path in tracked_paths if is_generated_path(path))
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


def iter_files(root: Path, pattern: str = "*") -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        current_path = Path(current)
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                yield current_path / name


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


def read_make_targets(path: Path) -> List[str]:
    if not path.is_file():
        return []
    targets: List[str] = []
    pattern = re.compile(r"^([A-Za-z0-9_.-]+):")
    for line in safe_read_text(path).splitlines():
        match = pattern.match(line)
        if match and not match.group(1).startswith("."):
            targets.append(match.group(1))
    return targets


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


def is_generated_path(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in GENERATED_PATTERNS)


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


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    checks = report["checks"]
    lines.extend(render_verdict(report))
    lines.extend(render_findings(report["findings"]))
    lines.extend(render_repository_shape(checks["repository_shape"]))
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
        candidates = ", ".join(item["candidates"]) if item["candidates"] else "missing"
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
