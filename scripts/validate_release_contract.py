#!/usr/bin/env python3
"""Validate Codex plugin and skills.sh release contracts."""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


PLUGIN_MANIFEST = Path("plugins/codex-skills/.codex-plugin/plugin.json")
CURSOR_PLUGIN_MANIFEST = Path("plugins/cursor-skills/.cursor-plugin/plugin.json")
CURSOR_MARKETPLACE_MANIFEST = Path(".cursor-plugin/marketplace.json")
MARKETPLACE_MANIFEST = Path(".agents/plugins/marketplace.json")
SKILLS_SH_MANIFEST = Path("skills.sh.json")
PLUGIN_ROOT = Path("plugins/codex-skills")
MIRROR_ROOT = PLUGIN_ROOT / "skills"
CURSOR_PLUGIN_ROOT = Path("plugins/cursor-skills")
CURSOR_MIRROR_ROOT = CURSOR_PLUGIN_ROOT / "skills"
SOURCE_ROOT = Path("skills")
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NUMBER_WORDS = {
    0: "zero",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
    20: "twenty",
}


def parse_semver(value: str) -> tuple[int, int, int]:
    match = SEMVER_PATTERN.fullmatch(value)
    if not match:
        raise ValueError(f"invalid SemVer: {value}")
    return tuple(int(component) for component in match.groups())


def parse_skill_frontmatter(text: str, expected_name: str) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    if len(lines) < 4 or lines[0] != "---":
        return ["SKILL.md must start with YAML frontmatter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return ["SKILL.md frontmatter is not closed"]

    allowed_fields = {"name", "description", "license", "allowed-tools", "metadata"}
    try:
        fields = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as error:
        return [f"SKILL.md frontmatter is invalid YAML: {error}"]
    if not isinstance(fields, dict):
        return ["SKILL.md frontmatter must be a YAML mapping"]

    for field in fields:
        if not isinstance(field, str):
            errors.append("frontmatter field names must be strings")
        elif field not in allowed_fields:
            errors.append(f"unexpected frontmatter field: {field}")

    actual_name = fields.get("name")
    if not isinstance(actual_name, str):
        errors.append("frontmatter name must be a string")
    elif actual_name != expected_name:
        errors.append(
            f"frontmatter name must be {expected_name}, got {actual_name}"
        )
    if isinstance(actual_name, str) and len(actual_name) > 64:
        errors.append("frontmatter name must be at most 64 characters")
    description = fields.get("description")
    if not isinstance(description, str):
        errors.append("frontmatter description must be a string")
    elif not description.strip():
        errors.append("frontmatter description is required")
    elif len(description) > 1024:
        errors.append("frontmatter description must be at most 1024 characters")
    elif "<" in description or ">" in description:
        errors.append("frontmatter description cannot contain angle brackets")
    return errors


def validate_skills_sh(
    public_skills: set[str], data: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    listed: list[str] = []
    groupings = data.get("groupings")
    if not isinstance(groupings, list) or not groupings:
        return ["skills.sh groupings must be a non-empty list"]

    for index, grouping in enumerate(groupings):
        if not isinstance(grouping, dict):
            errors.append(f"skills.sh grouping {index} must be an object")
            continue
        if not str(grouping.get("title", "")).strip():
            errors.append(f"skills.sh grouping {index} is missing a title")
        if not str(grouping.get("description", "")).strip():
            errors.append(f"skills.sh grouping {index} is missing a description")
        skills = grouping.get("skills")
        if not isinstance(skills, list) or not skills:
            errors.append(f"skills.sh grouping {index} has no skills")
            continue
        listed.extend(str(skill) for skill in skills)

    counts = Counter(listed)
    for skill, count in sorted(counts.items()):
        if count > 1:
            errors.append(f"skills.sh duplicate skill: {skill}")
    for skill in sorted(set(listed) - public_skills):
        errors.append(f"skills.sh stale skill: {skill}")
    for skill in sorted(public_skills - set(listed)):
        errors.append(f"skills.sh missing skill: {skill}")
    return errors


def shipped_plugin_change(changed_paths: set[str]) -> bool:
    release_prefixes = (
        "skills/",
        "plugins/codex-skills/skills/",
        "plugins/codex-skills/assets/",
        "plugins/codex-skills/.codex-plugin/",
    )
    release_files = {
        "plugins/codex-skills/.app.json",
        "plugins/codex-skills/.mcp.json",
    }
    return bool(changed_paths & release_files) or any(
        path.startswith(release_prefixes) for path in changed_paths
    )


def cursor_plugin_change(changed_paths: set[str]) -> bool:
    prefixes = ("skills/", "plugins/cursor-skills/", ".cursor-plugin/")
    return any(path.startswith(prefixes) for path in changed_paths)


def validate_version_change(
    base_version: str, current_version: str, changed: set[str]
) -> list[str]:
    if not shipped_plugin_change(changed):
        return []
    try:
        if parse_semver(current_version) > parse_semver(base_version):
            return []
    except ValueError as error:
        return [str(error)]
    return [
        "shipped plugin content changed but plugin version did not increase: "
        f"{base_version} -> {current_version}"
    ]


def validate_plugin_manifest(repo: Path, data: dict[str, Any]) -> tuple[list[str], str]:
    errors: list[str] = []
    allowed_fields = {
        "id", "name", "version", "description", "skills", "apps", "mcpServers",
        "interface", "author", "homepage", "repository", "license", "keywords",
    }
    for field in sorted(set(data) - allowed_fields):
        errors.append(f"plugin manifest has unsupported field: {field}")

    for field in ("name", "version", "description"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"plugin manifest {field} must be a non-empty string")
    if data.get("name") != PLUGIN_ROOT.name:
        errors.append(f"plugin manifest name must be {PLUGIN_ROOT.name}")

    version = str(data.get("version", ""))
    try:
        parse_semver(version)
    except ValueError as error:
        errors.append(str(error))
    if data.get("skills") != "./skills/":
        errors.append("plugin manifest skills must be ./skills/")

    author = data.get("author")
    if not isinstance(author, dict) or not str(author.get("name", "")).strip():
        errors.append("plugin manifest author.name is required")

    interface = data.get("interface")
    if not isinstance(interface, dict):
        errors.append("plugin manifest interface must be an object")
        return errors, version
    for field in (
        "displayName", "shortDescription", "longDescription", "developerName", "category"
    ):
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            errors.append(f"plugin manifest interface.{field} is required")
    if "defaultPrompt" not in interface and "default_prompt" not in interface:
        errors.append("plugin manifest interface.defaultPrompt is required")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities or not all(
        isinstance(item, str) and item.strip() for item in capabilities
    ):
        errors.append("plugin manifest interface.capabilities must contain strings")

    logo = interface.get("logo")
    if not isinstance(logo, str) or not (repo / PLUGIN_ROOT / logo).is_file():
        errors.append(f"plugin manifest logo does not exist: {logo}")

    def contains_todo(value: Any) -> bool:
        if isinstance(value, str):
            return "[TODO:" in value
        if isinstance(value, list):
            return any(contains_todo(item) for item in value)
        if isinstance(value, dict):
            return any(contains_todo(item) for item in value.values())
        return False

    if contains_todo(data):
        errors.append("plugin manifest contains a [TODO: ...] placeholder")
    return errors, version


def validate_cursor_plugin_manifest(data: dict[str, Any]) -> tuple[list[str], str]:
    errors: list[str] = []
    allowed_fields = {
        "name",
        "displayName",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
    }
    for field in sorted(set(data) - allowed_fields):
        errors.append(f"Cursor plugin manifest has unsupported field: {field}")

    if data.get("name") != CURSOR_PLUGIN_ROOT.name:
        errors.append(f"Cursor plugin manifest name must be {CURSOR_PLUGIN_ROOT.name}")
    for field in ("displayName", "version", "description"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"Cursor plugin manifest {field} must be a non-empty string")

    version = str(data.get("version", ""))
    try:
        parse_semver(version)
    except ValueError as error:
        errors.append(str(error))

    author = data.get("author")
    if not isinstance(author, dict) or not str(author.get("name", "")).strip():
        errors.append("Cursor plugin manifest author.name is required")
    for field in ("homepage", "repository", "license"):
        if field in data and not isinstance(data[field], str):
            errors.append(f"Cursor plugin manifest {field} must be a string")
    if "keywords" in data and (
        not isinstance(data["keywords"], list)
        or not all(
            isinstance(keyword, str) and keyword.strip()
            for keyword in data["keywords"]
        )
    ):
        errors.append("Cursor plugin manifest keywords must contain strings")
    return errors, version


def validate_cursor_marketplace(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    owner = data.get("owner")
    metadata = data.get("metadata")
    plugins = data.get("plugins")
    if data.get("name") != "codex-skills":
        errors.append("Cursor marketplace name must be codex-skills")
    if not isinstance(owner, dict) or not str(owner.get("name", "")).strip():
        errors.append("Cursor marketplace owner.name is required")
    if not isinstance(metadata, dict):
        return [*errors, "Cursor marketplace metadata is required"]
    if metadata.get("pluginRoot") != "plugins":
        errors.append("Cursor marketplace metadata.pluginRoot must be plugins")
    if not isinstance(metadata.get("version"), str) or not metadata["version"].strip():
        errors.append("Cursor marketplace metadata.version is required")
    else:
        try:
            parse_semver(metadata["version"])
        except ValueError as error:
            errors.append(str(error))
    if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
        errors.append("Cursor marketplace metadata.description is required")
    if not isinstance(plugins, list) or len(plugins) != 1:
        return [*errors, "Cursor marketplace must contain exactly one plugin"]
    plugin = plugins[0]
    if not isinstance(plugin, dict):
        return [*errors, "Cursor marketplace plugin entry must be an object"]
    if plugin.get("name") != CURSOR_PLUGIN_ROOT.name:
        errors.append(f"Cursor marketplace plugin name must be {CURSOR_PLUGIN_ROOT.name}")
    if plugin.get("source") != CURSOR_PLUGIN_ROOT.name:
        errors.append(f"Cursor marketplace plugin source must be {CURSOR_PLUGIN_ROOT.name}")
    if not isinstance(plugin.get("description"), str) or not plugin["description"].strip():
        errors.append("Cursor marketplace plugin description is required")
    return errors


def load_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"{path}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{path}: root must be an object"]
    return value, []


def skill_names(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def relative_files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
        and ".DS_Store" not in path.parts
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    }


def validate_skill_mirror(
    source_root: Path, mirror_root: Path, public_skills: set[str], label: str
) -> list[str]:
    errors: list[str] = []
    mirrored_skills = skill_names(mirror_root)
    if public_skills != mirrored_skills:
        for skill in sorted(public_skills - mirrored_skills):
            errors.append(f"{label} mirror missing skill: {skill}")
        for skill in sorted(mirrored_skills - public_skills):
            errors.append(f"{label} mirror has stale skill: {skill}")

    for skill in sorted(public_skills & mirrored_skills):
        source = source_root / skill
        mirror = mirror_root / skill
        source_files = relative_files(source)
        mirror_files = relative_files(mirror)
        for path in sorted(source_files - mirror_files):
            errors.append(f"{label} {skill}: mirror missing {path}")
        for path in sorted(mirror_files - source_files):
            errors.append(f"{label} {skill}: mirror has stale {path}")
        for path in sorted(source_files & mirror_files):
            if not filecmp.cmp(source / path, mirror / path, shallow=False):
                errors.append(f"{label} {skill}: mirror differs at {path}")
    return errors


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(marker))
    return text[start : end if end >= 0 else len(text)]


def validate_catalogue(repo: Path) -> tuple[list[str], str]:
    errors: list[str] = []
    source_root = repo / SOURCE_ROOT
    mirror_root = repo / MIRROR_ROOT
    public_skills = skill_names(source_root)

    if not public_skills:
        errors.append("no public skills discovered under skills/")
    errors.extend(validate_skill_mirror(source_root, mirror_root, public_skills, "Codex"))
    errors.extend(
        validate_skill_mirror(
            source_root, repo / CURSOR_MIRROR_ROOT, public_skills, "Cursor"
        )
    )

    for skill in sorted(public_skills):
        if not SKILL_NAME_PATTERN.fullmatch(skill):
            errors.append(f"invalid skill directory name: {skill}")
        source = source_root / skill
        for detail in parse_skill_frontmatter(
            (source / "SKILL.md").read_text(encoding="utf-8"), skill
        ):
            errors.append(f"skills/{skill}/SKILL.md: {detail}")
        if not (source / "agents/openai.yaml").is_file():
            errors.append(f"skills/{skill}: missing agents/openai.yaml")

    skills_data, json_errors = load_json(repo / SKILLS_SH_MANIFEST)
    errors.extend(json_errors)
    if not json_errors:
        errors.extend(validate_skills_sh(public_skills, skills_data))

    plugin_data, json_errors = load_json(repo / PLUGIN_MANIFEST)
    errors.extend(json_errors)
    plugin_version = ""
    if not json_errors:
        plugin_errors, plugin_version = validate_plugin_manifest(repo, plugin_data)
        errors.extend(plugin_errors)

    cursor_plugin_data, cursor_json_errors = load_json(repo / CURSOR_PLUGIN_MANIFEST)
    errors.extend(cursor_json_errors)
    if not cursor_json_errors:
        cursor_plugin_errors, _ = validate_cursor_plugin_manifest(cursor_plugin_data)
        errors.extend(cursor_plugin_errors)

    cursor_marketplace_data, cursor_marketplace_json_errors = load_json(
        repo / CURSOR_MARKETPLACE_MANIFEST
    )
    errors.extend(cursor_marketplace_json_errors)
    if not cursor_marketplace_json_errors:
        errors.extend(validate_cursor_marketplace(cursor_marketplace_data))
        if (
            not cursor_json_errors
            and cursor_plugin_data.get("version")
            != cursor_marketplace_data.get("metadata", {}).get("version")
        ):
            errors.append("Cursor plugin and marketplace versions must match")

    marketplace, json_errors = load_json(repo / MARKETPLACE_MANIFEST)
    errors.extend(json_errors)
    if not json_errors:
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1:
            errors.append("marketplace must contain exactly one plugin")
        else:
            entry = plugins[0]
            source = entry.get("source", {})
            policy = entry.get("policy", {})
            if source.get("path") != "./plugins/codex-skills":
                errors.append("marketplace source.path must be ./plugins/codex-skills")
            if policy.get("installation") != "AVAILABLE":
                errors.append("marketplace installation policy must be AVAILABLE")
            if policy.get("authentication") != "ON_INSTALL":
                errors.append("marketplace authentication policy must be ON_INSTALL")
            if not entry.get("category"):
                errors.append("marketplace plugin category is required")

    readme = (repo / "README.md").read_text(encoding="utf-8")
    readme_skills = re.findall(
        r"\[`([a-z0-9-]+)`\]\(docs/([a-z0-9-]+)\.md\)",
        section(readme, "✨ Skills"),
    )
    readme_names = [name for name, doc_name in readme_skills if name == doc_name]
    if Counter(readme_names) != Counter(public_skills):
        errors.append("README Skills table must list every public skill exactly once")
    expected_count = NUMBER_WORDS.get(len(public_skills), str(len(public_skills)))
    if not re.search(
        rf"^> {re.escape(expected_count)} Codex skills\b", readme, re.MULTILINE | re.I
    ):
        errors.append(f"README skill count must be {expected_count}")

    installation = (repo / "docs/installation.md").read_text(encoding="utf-8")
    exposed = section(installation, "Install Through skills.sh")
    for skill in sorted(public_skills):
        if not (repo / f"docs/{skill}.md").is_file():
            errors.append(f"missing docs/{skill}.md")
        if f"--skill {skill}" not in exposed:
            errors.append(f"installation guide missing skills.sh command for {skill}")

    return errors, plugin_version


def git_output(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def git_paths(repo: Path, *args: str) -> set[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    return {
        os.fsdecode(path)
        for path in result.stdout.split(b"\0")
        if path
    }


def changed_paths(repo: Path, base_ref: str) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    changed: set[str] = set()
    try:
        changed.update(
            git_paths(repo, "diff", "--name-only", "-z", f"{base_ref}...HEAD")
        )
        for args in (
            ("diff", "--name-only", "-z"),
            ("diff", "--cached", "--name-only", "-z"),
        ):
            changed.update(git_paths(repo, *args))
        changed.update(
            git_paths(repo, "ls-files", "--others", "--exclude-standard", "-z")
        )
    except subprocess.CalledProcessError as error:
        errors.append(
            f"cannot resolve base ref {base_ref}: {os.fsdecode(error.stderr).strip()}"
        )
    return changed, errors


def version_at_ref(repo: Path, base_ref: str) -> tuple[str, list[str]]:
    try:
        raw = git_output(repo, "show", f"{base_ref}:{PLUGIN_MANIFEST}")
        data = json.loads(raw)
        return str(data.get("version", "")), []
    except (subprocess.CalledProcessError, json.JSONDecodeError) as error:
        return "", [f"cannot read plugin version at {base_ref}: {error}"]


def cursor_version_at_ref(repo: Path, base_ref: str) -> tuple[str, list[str]]:
    try:
        raw = git_output(repo, "show", f"{base_ref}:{CURSOR_PLUGIN_MANIFEST}")
        data = json.loads(raw)
        return str(data.get("version", "")), []
    except subprocess.CalledProcessError:
        return "", []
    except json.JSONDecodeError as error:
        return "", [f"cannot parse Cursor plugin version at {base_ref}: {error}"]


def validate_version_bump(
    repo: Path, base_ref: str, current_version: str
) -> list[str]:
    changed, errors = changed_paths(repo, base_ref)
    if errors or not shipped_plugin_change(changed):
        return errors
    base_version, version_errors = version_at_ref(repo, base_ref)
    errors.extend(version_errors)
    if version_errors:
        return errors
    errors.extend(validate_version_change(base_version, current_version, changed))
    return errors


def validate_cursor_version_bump(
    repo: Path, base_ref: str, current_version: str
) -> list[str]:
    changed, errors = changed_paths(repo, base_ref)
    if errors or not cursor_plugin_change(changed):
        return errors
    base_version, version_errors = cursor_version_at_ref(repo, base_ref)
    errors.extend(version_errors)
    if version_errors or not base_version:
        return errors
    try:
        if parse_semver(current_version) > parse_semver(base_version):
            return errors
    except ValueError as error:
        return [*errors, str(error)]
    errors.append(
        "Cursor plugin content changed but plugin version did not increase: "
        f"{base_version} -> {current_version}"
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-ref",
        help="Git base commit/ref used to enforce a plugin SemVer increase",
    )
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]

    errors, plugin_version = validate_catalogue(repo)
    if args.base_ref and args.base_ref.strip("0"):
        errors.extend(validate_version_bump(repo, args.base_ref, plugin_version))
        cursor_data, cursor_json_errors = load_json(repo / CURSOR_PLUGIN_MANIFEST)
        if not cursor_json_errors:
            errors.extend(
                validate_cursor_version_bump(
                    repo, args.base_ref, str(cursor_data.get("version", ""))
                )
            )

    if errors:
        for error in errors:
            print(f"release contract: {error}", file=sys.stderr)
        return 1

    print("Release contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
