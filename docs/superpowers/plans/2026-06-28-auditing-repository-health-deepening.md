# Auditing Repository Health Deepening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen `auditing-repository-health` so audits classify repository topology, detect package/service/docs boundaries, apply ecosystem-specific setup guidance, and produce scoped multi-repo findings instead of shallow root-only checklist output.

**Architecture:** Keep the existing read-only auditor as the executable baseline, but add a lightweight topology inventory, lifecycle gate matrix, and CI command mapping so agents must see actual repository structure before writing recommendations. Keep judgement-heavy ecosystem rules in progressively loaded references, routed by an index from detected manifests. Preserve source/plugin mirror parity and prove the skill behavior with pressure fixtures before and after the skill edit.

**Tech Stack:** Markdown skills and references, Python 3 standard library auditor and unittest tests, Bash validation scripts, Codex skill packaging under `skills/` and `plugins/codex-skills/skills/`.

## Global Constraints

- Follow `AGENTS.md`: direct, terse, verify live state, minimal correct change.
- Do not push to `main` or the default branch.
- Commit at each milestone or major code edit.
- Use `apply_patch` for manual edits.
- Preserve source/plugin mirror parity for `auditing-repository-health`.
- Keep the auditor read-only: no dependency installs, no network calls, no writes outside explicit test fixtures.
- Run the bundled auditor first in the skill workflow, then classify the repository before recommending fixes.
- Use responsibility names such as `bootstrap`, `setup`, `test`, and `cibuild` as vocabulary, not mandatory filenames.
- Do not prescribe generic boilerplate, Scripts-to-Rule-Them-All filenames, or a new repo tree before mapping repo purpose, ecosystems, package boundaries, native commands, and CI coverage.
- Missing best-practice files are usually P2/P3 unless repo purpose, public exposure, security sensitivity, regulated use, or critical production status makes them blocking.
- Run `$autoreview` before closeout only if the implementation changes substantive executable behavior.

---

## File Structure

- Modify `skills/auditing-repository-health/scripts/audit_repository_health.py`: add topology inventory, lifecycle gate matrix, CI command mapping, and markdown rendering for the new sections.
- Modify `skills/auditing-repository-health/tests/test_audit_repository_health.py`: add fixture-backed tests for inventory, lifecycle gates, docs-only false positives, and scoped package findings.
- Create `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/`: synthetic pressure fixture used by tests and skill forward-testing.
- Create `skills/auditing-repository-health/tests/fixtures/docs-only-site/`: fixture proving docs-only repos do not need server/runtime gates.
- Create `skills/auditing-repository-health/tests/fixtures/codex-skill-mirror/`: fixture proving skill/plugin mirror audit expectations.
- Create `skills/auditing-repository-health/references/repo-foundation-rubric.md`: repo-wide audit stance, severity, mono/polyrepo rules, and evidence-before-prescription rules.
- Create `skills/auditing-repository-health/references/report-contract.md`: exact report sections and finding fields agents must preserve.
- Create `skills/auditing-repository-health/references/ecosystem-index.md`: manifest-to-overlay routing table.
- Create `skills/auditing-repository-health/references/ecosystems/*.md`: focused ecosystem overlays.
- Modify `skills/auditing-repository-health/SKILL.md`: route agents through the auditor, classification, report contract, and relevant ecosystem overlays.
- Create `scripts/check_skill_mirror.py`: deterministic mirror parity helper usable by tests and humans.
- Mirror all changed `skills/auditing-repository-health/**` files into `plugins/codex-skills/skills/auditing-repository-health/**`.

---

### Task 1: Add Pressure Fixtures And Baseline Criteria

**Files:**
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/README.md`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/package.json`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/pnpm-workspace.yaml`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/packages/api/go.mod`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/packages/api/api.go`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/packages/worker/pyproject.toml`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/packages/worker/src/worker/__init__.py`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/docs/package.json`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/Dockerfile`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/.github/workflows/ci.yml`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/EXPECTED_AUDIT_CRITERIA.md`
- Create: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/BASELINE_NOTES.md`

**Interfaces:**
- Consumes: current `audit_repository_health.py --repo <fixture> --format json`.
- Produces: stable fixture paths that later tests use by `Path(__file__).parent / "fixtures" / "polyglot-monorepo"`.

- [ ] **Step 1: Create the polyglot pressure fixture**

Create the fixture with these exact file contents:

```markdown
# Polyglot Fixture

Synthetic fixture for repository-health audit pressure tests.

This repository intentionally mixes:
- a Node workspace root
- a Go API package
- a Python worker package
- a docs site
- a Docker service surface

The correct audit must classify package boundaries before recommending scripts.
```

`package.json`:

```json
{
  "name": "polyglot-fixture",
  "private": true,
  "packageManager": "pnpm@10.0.0",
  "scripts": {
    "test": "pnpm -r test --if-present",
    "ci": "pnpm test && pnpm --filter ./docs run build"
  },
  "workspaces": [
    "packages/*",
    "docs"
  ]
}
```

`pnpm-workspace.yaml`:

```yaml
packages:
  - "packages/*"
  - "docs"
```

`packages/api/go.mod`:

```go
module example.com/polyglot-fixture/api

go 1.23
```

`packages/api/api.go`:

```go
package api

func Health() string {
	return "ok"
}
```

`packages/worker/pyproject.toml`:

```toml
[project]
name = "polyglot-worker"
version = "0.1.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`packages/worker/src/worker/__init__.py`:

```python
def health() -> str:
    return "ok"
```

`docs/package.json`:

```json
{
  "name": "polyglot-docs",
  "private": true,
  "scripts": {
    "build": "echo build docs"
  }
}
```

`Dockerfile`:

```dockerfile
FROM alpine:3.20
CMD ["echo", "polyglot fixture"]
```

`.github/workflows/ci.yml`:

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm test
      - run: go test ./...
        working-directory: packages/api
```

- [ ] **Step 2: Add explicit expected criteria**

Create `EXPECTED_AUDIT_CRITERIA.md`:

```markdown
# Expected Audit Criteria

The updated skill must produce an audit that:

- classifies this fixture as a polyglot monorepo
- detects the Node workspace root
- detects the Go API package at `packages/api`
- detects the Python worker package at `packages/worker`
- detects the docs package at `docs`
- detects the Docker service surface at repository root
- separates root/shared lifecycle gates from package-specific gates
- maps the root `pnpm test` and CI workflow as shared validation evidence
- maps `go test ./...` from the workflow to `packages/api`
- reports that `packages/worker` has no package-level test command or CI coverage
- does not force `script/test`, `script/cibuild`, or other exact Scripts-to-Rule-Them-All filenames
- does not treat a missing root `scripts/validate.sh` as proof that no validation gate exists
```

- [ ] **Step 3: Record the baseline failure from the current skill**

Run this before modifying `SKILL.md` or the auditor:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py \
  --repo skills/auditing-repository-health/tests/fixtures/polyglot-monorepo \
  --format json > /tmp/polyglot-baseline.json
```

Expected: command succeeds, but the JSON has no `repository_inventory`, no `lifecycle_gate_matrix`, and no package boundary list.

Create `BASELINE_NOTES.md`:

````markdown
# Baseline Notes

Baseline command:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py --repo skills/auditing-repository-health/tests/fixtures/polyglot-monorepo --format json
```

Observed baseline failure:

- The report does not emit a repository topology inventory.
- The report does not list package, service, or docs boundaries.
- The report cannot distinguish root/shared validation from package-specific validation.
- The report cannot show that `packages/worker` lacks package-level test coverage while root and Go API validation exist.
- The report is therefore vulnerable to shallow root-only recommendations.
````

- [ ] **Step 4: Commit the fixtures**

```bash
git add skills/auditing-repository-health/tests/fixtures/polyglot-monorepo
git commit -m "test(auditing-repository-health): add polyglot audit pressure fixture"
```

---

### Task 2: Add Topology Inventory And Lifecycle Gate Matrix

**Files:**
- Modify: `skills/auditing-repository-health/scripts/audit_repository_health.py`
- Modify: `skills/auditing-repository-health/tests/test_audit_repository_health.py`

**Interfaces:**
- Produces: `report["checks"]["repository_inventory"]`.
- Produces: `report["checks"]["lifecycle_gate_matrix"]`.
- Produces: markdown sections `## Repository Inventory` and `## Lifecycle Gate Matrix`.
- Later tasks rely on inventory fields:
  - `classification: str`
  - `ecosystems: list[str]`
  - `boundaries: list[dict[str, Any]]`
  - `suggested_overlays: list[str]`

- [ ] **Step 1: Write failing inventory tests**

Append these tests to `AuditRepositoryHealthTests`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py \
  AuditRepositoryHealthTests.test_polyglot_monorepo_inventory_detects_boundaries \
  AuditRepositoryHealthTests.test_polyglot_lifecycle_gate_matrix_scopes_gates \
  AuditRepositoryHealthTests.test_markdown_report_includes_inventory_sections
```

Expected: FAIL with `KeyError: 'repository_inventory'` or missing markdown sections.

- [ ] **Step 3: Add inventory data definitions**

In `audit_repository_health.py`, add these constants near the existing manifest constants:

```python
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
```

- [ ] **Step 4: Add `check_repository_inventory`**

Add this method to `Audit` and call it from `run()` after `repository_shape`:

```python
    def check_repository_inventory(self, root: Path) -> Dict[str, Any]:
        boundaries: List[Dict[str, Any]] = []
        ecosystems: set[str] = set()

        for path in iter_files(root):
            rel = relative_path(root, path)
            kind_and_ecosystem = BOUNDARY_MANIFESTS.get(path.name)
            if kind_and_ecosystem is None and path.name in DOCS_SITE_FILES:
                kind_and_ecosystem = ("docs-site", "docs")
            if kind_and_ecosystem is None:
                continue

            kind, ecosystem = kind_and_ecosystem
            boundary_path = path.parent if kind != "docker-service" else path
            boundary_rel = relative_path(root, boundary_path)
            evidence_rel = rel
            boundary = {
                "path": boundary_rel,
                "kind": kind,
                "ecosystem": ecosystem,
                "evidence": [evidence_rel],
            }
            boundaries.append(boundary)
            ecosystems.add(ecosystem)

        boundaries = merge_boundaries(boundaries)
        classification = classify_repository_inventory(boundaries)
        overlays = sorted(
            ECOSYSTEM_OVERLAYS[ecosystem]
            for ecosystem in ecosystems
            if ecosystem in ECOSYSTEM_OVERLAYS
        )

        return {
            "classification": classification,
            "ecosystems": sorted(ecosystems),
            "boundaries": boundaries,
            "suggested_overlays": overlays,
        }
```

Add helper functions near existing standalone helpers:

```python
def merge_boundaries(boundaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_key: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for boundary in boundaries:
        key = (boundary["path"], boundary["kind"], boundary["ecosystem"])
        existing = by_key.setdefault(
            key,
            {
                "path": boundary["path"],
                "kind": boundary["kind"],
                "ecosystem": boundary["ecosystem"],
                "evidence": [],
            },
        )
        existing["evidence"].extend(boundary["evidence"])
    merged = []
    for item in by_key.values():
        item["evidence"] = sorted(set(item["evidence"]))
        merged.append(item)
    return sorted(merged, key=lambda item: (item["path"], item["kind"]))


def classify_repository_inventory(boundaries: List[Dict[str, Any]]) -> str:
    package_boundaries = [
        boundary
        for boundary in boundaries
        if boundary["path"] not in {".", "Dockerfile"}
    ]
    ecosystems = {boundary["ecosystem"] for boundary in boundaries}
    if len(package_boundaries) >= 2 or len(ecosystems) >= 3:
        return "monorepo"
    if any(boundary["kind"] == "codex-skill" for boundary in boundaries):
        return "skill-repository"
    return "single-repository"
```

- [ ] **Step 5: Add lifecycle gate matrix**

Add this method to `Audit` and call it from `run()` after `scripts` and `validation` are available:

```python
    def check_lifecycle_gate_matrix(
        self,
        root: Path,
        inventory: Dict[str, Any],
        scripts_check: Dict[str, Any],
        validation_check: Dict[str, Any],
    ) -> Dict[str, Any]:
        rows = []
        workflow_commands = workflow_command_evidence(root)
        for boundary in inventory["boundaries"]:
            path = boundary["path"]
            rows.append(
                {
                    "path": path,
                    "kind": boundary["kind"],
                    "ecosystem": boundary["ecosystem"],
                    "setup": lifecycle_cell(path, "setup", scripts_check, workflow_commands),
                    "focused_test": lifecycle_cell(path, "test", scripts_check, workflow_commands),
                    "full_validation": lifecycle_cell(path, "cibuild", scripts_check, workflow_commands),
                    "lint_format": lifecycle_cell(path, "lint", scripts_check, workflow_commands),
                    "typecheck_static": lifecycle_cell(path, "typecheck", scripts_check, workflow_commands),
                    "build_package": lifecycle_cell(path, "build", scripts_check, workflow_commands),
                    "server": lifecycle_server_cell(boundary, scripts_check, workflow_commands),
                    "docs_release": lifecycle_cell(path, "docs", scripts_check, workflow_commands),
                    "ci_coverage": ci_coverage_cell(path, workflow_commands),
                }
            )
        return {"rows": rows}
```

Add helpers:

```python
def workflow_command_evidence(root: Path) -> Dict[str, List[str]]:
    evidence: Dict[str, List[str]] = defaultdict(list)
    for workflow in sorted((root / ".github" / "workflows").glob("*.y*ml")):
        rel_workflow = relative_path(root, workflow)
        try:
            text = workflow.read_text(errors="replace")
        except OSError:
            continue
        working_directory = "."
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("working-directory:"):
                working_directory = stripped.split(":", 1)[1].strip().strip("\"'")
                continue
            if not stripped.startswith("run:"):
                continue
            command = stripped.split(":", 1)[1].strip().strip("\"'")
            key = working_directory or "."
            evidence[key].append(f"{rel_workflow}:{command}")
    return dict(evidence)


def lifecycle_cell(
    path: str,
    responsibility: str,
    scripts_check: Dict[str, Any],
    workflow_commands: Dict[str, List[str]],
) -> Dict[str, Any]:
    evidence: List[str] = []
    responsibility_info = scripts_check.get("responsibilities", {}).get(responsibility)
    if responsibility_info and path == ".":
        evidence.extend(responsibility_info.get("candidates", []))
    evidence.extend(workflow_commands.get(path, []))
    status = "present" if evidence else "missing"
    return {"status": status, "evidence": sorted(set(evidence))}


def lifecycle_server_cell(
    boundary: Dict[str, Any],
    scripts_check: Dict[str, Any],
    workflow_commands: Dict[str, List[str]],
) -> Dict[str, Any]:
    if boundary["kind"] in {"docs-site", "codex-skill", "go-package", "python-package", "rust-crate", "swift-package"}:
        return {"status": "not_applicable", "evidence": []}
    return lifecycle_cell(boundary["path"], "server", scripts_check, workflow_commands)


def ci_coverage_cell(path: str, workflow_commands: Dict[str, List[str]]) -> Dict[str, Any]:
    evidence = workflow_commands.get(path, [])
    return {
        "status": "present" if evidence else "missing",
        "evidence": sorted(set(evidence)),
    }
```

- [ ] **Step 6: Render new sections**

Update `render_markdown()` to include the new sections after `Repository Shape`:

```python
    lines.extend(render_repository_inventory(checks["repository_inventory"]))
    lines.extend(render_lifecycle_gate_matrix(checks["lifecycle_gate_matrix"]))
```

Add render helpers:

```python
def render_repository_inventory(inventory: Dict[str, Any]) -> List[str]:
    lines = [
        "## Repository Inventory",
        f"- Classification: {inventory['classification']}",
        f"- Ecosystems: {format_present(inventory['ecosystems'])}",
        f"- Suggested overlays: {format_present(inventory['suggested_overlays'])}",
        "- Boundaries:",
    ]
    for boundary in inventory["boundaries"]:
        evidence = ", ".join(boundary["evidence"])
        lines.append(
            f"  - {boundary['path']}: {boundary['kind']} ({boundary['ecosystem']}) - {evidence}"
        )
    lines.append("")
    return lines


def render_lifecycle_gate_matrix(matrix: Dict[str, Any]) -> List[str]:
    lines = ["## Lifecycle Gate Matrix"]
    for row in matrix["rows"]:
        lines.append(f"- {row['path']} ({row['kind']})")
        for key in ["setup", "focused_test", "full_validation", "lint_format", "typecheck_static", "build_package", "server", "docs_release", "ci_coverage"]:
            cell = row[key]
            evidence = f" - {', '.join(cell['evidence'])}" if cell["evidence"] else ""
            lines.append(f"  - {key}: {cell['status']}{evidence}")
    lines.append("")
    return lines
```

- [ ] **Step 7: Run focused tests**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py \
  AuditRepositoryHealthTests.test_polyglot_monorepo_inventory_detects_boundaries \
  AuditRepositoryHealthTests.test_polyglot_lifecycle_gate_matrix_scopes_gates \
  AuditRepositoryHealthTests.test_markdown_report_includes_inventory_sections
```

Expected: PASS.

- [ ] **Step 8: Run full source tests**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py
```

Expected: all tests pass.

- [ ] **Step 9: Commit**

```bash
git add skills/auditing-repository-health/scripts/audit_repository_health.py \
  skills/auditing-repository-health/tests/test_audit_repository_health.py
git commit -m "feat(auditing-repository-health): inventory repo topology"
```

---

### Task 3: Add Report Contract And Ecosystem References

**Files:**
- Create: `skills/auditing-repository-health/references/report-contract.md`
- Create: `skills/auditing-repository-health/references/repo-foundation-rubric.md`
- Create: `skills/auditing-repository-health/references/ecosystem-index.md`
- Create: `skills/auditing-repository-health/references/ecosystems/python.md`
- Create: `skills/auditing-repository-health/references/ecosystems/node-typescript.md`
- Create: `skills/auditing-repository-health/references/ecosystems/go.md`
- Create: `skills/auditing-repository-health/references/ecosystems/rust.md`
- Create: `skills/auditing-repository-health/references/ecosystems/swift-apple.md`
- Create: `skills/auditing-repository-health/references/ecosystems/jvm-gradle-maven.md`
- Create: `skills/auditing-repository-health/references/ecosystems/ruby.md`
- Create: `skills/auditing-repository-health/references/ecosystems/docs-static-sites.md`
- Create: `skills/auditing-repository-health/references/ecosystems/docker-services.md`
- Create: `skills/auditing-repository-health/references/ecosystems/codex-skill-plugin.md`
- Create: `skills/auditing-repository-health/references/ecosystems/infra-iac.md`
- Modify: `skills/auditing-repository-health/tests/test_audit_repository_health.py`

**Interfaces:**
- Produces references routed by `repository_inventory["suggested_overlays"]`.
- Produces report contract consumed by `SKILL.md`.

- [ ] **Step 1: Write failing reference tests**

Append:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py \
  AuditRepositoryHealthTests.test_skill_reference_docs_define_report_contract_and_overlays \
  AuditRepositoryHealthTests.test_ecosystem_overlays_include_required_sections
```

Expected: FAIL because the reference files do not exist.

- [ ] **Step 3: Create `report-contract.md`**

Use this content:

````markdown
# Report Contract

Preserve all existing script report sections:

```md
## Verdict
## Findings
## Repository Shape
## Repository Inventory
## Lifecycle Gate Matrix
## Documentation
## Scripts
## Validation
## Packaging
## Hygiene
## Commands Run
## Not Checked
```

## Repository Classification

Required before recommending foundations.

Include:

- scope: `single-repository`, `monorepo`, `polyrepo-set`, `source-plugin-mirror`, or `generated-vendor-subtree`
- purpose: library, service, CLI, app, docs, infra, skill/plugin, or mixed
- detected ecosystems
- package, service, docs, and generated/vendor boundaries
- confidence level and missing evidence

## Topology Inventory

Required when more than one package, service, app, docs site, or mirror root exists.

List each boundary with:

- path
- kind
- ecosystem
- manifest evidence
- whether it is root/shared or package-specific

## Lifecycle Gate Matrix

Required for every audit.

Columns:

- scope/path
- setup/bootstrap
- focused test
- full validation/CI
- lint/format
- typecheck/static analysis
- build/package
- runtime/server/dev
- docs/release
- CI coverage

Use `present`, `documented`, `missing`, or `not_applicable`.

## Ecosystem Assessment

Required for every detected ecosystem.

For each ecosystem, summarize:

- expected native commands
- detected commands
- missing gates
- false positives avoided
- severity rationale

## Findings

Each finding must include:

- severity
- scope/path
- evidence
- impact
- repo-native recommendation
- whether the finding is root/shared or package-specific
- whether the issue is proven, inferred, or not checked

## Recommended Foundation

Only include after classification.

Do not prescribe a generic tree before mapping:

- repo purpose
- primary ecosystem or ecosystems
- package boundaries
- runtime model
- existing commands
- CI coverage
- release/deployment expectations
````

- [ ] **Step 4: Create `repo-foundation-rubric.md`**

Use this content:

```markdown
# Repository Foundation Rubric

Use this reference after running the auditor and reading the repository inventory.

## Scope Contract

Classify the audit target as:

- single repository
- monorepo
- polyrepo set
- source/plugin mirror repository
- generated/vendor subtree

Do not apply monorepo rules to polyrepo audits or polyrepo rules to one checkout.

## Evidence Before Prescription

Do not recommend a repository tree, scripts, CI layout, package structure, or boilerplate until these are known:

- repo purpose
- primary ecosystem or ecosystems
- package boundaries
- runtime model
- existing commands
- CI coverage
- release/deployment expectations

If package boundaries cannot be identified, say so explicitly and avoid package-specific recommendations.

## Responsibilities, Not Filenames

Use `bootstrap`, `setup`, `update`, `server`, `test`, `cibuild`, and `console` as responsibility names only. Healthy repositories may express them through `Makefile`, `justfile`, package scripts, Gradle tasks, Cargo commands, SwiftPM commands, `bin/`, `tools/`, CI workflows, or documented custom commands.

Do not require exact Scripts-to-Rule-Them-All filenames unless the repository already uses that convention or a wrapper is clearly justified.

## Root Health Does Not Prove Package Health

In monorepos and workspace repositories, audit:

- root/shared foundation
- each package, service, app, or docs root
- cross-package validation
- CI coverage for each package
- generated/vendor boundaries that should be excluded from findings

A missing root-level command is not a finding by itself in a monorepo. First check whether equivalent package-level or CI-level gates exist.

## Baseline Foundations

Check for:

- README or equivalent entrypoint documentation
- license when code is redistributable
- contribution guide for shared or public work
- security policy for public, installable, production, or security-sensitive work
- code ownership or review routing when ownership is non-obvious
- issue and PR templates when external contribution flow exists
- agent instructions when agents are expected to work in the repo
- dependency manifests and lockfiles where the ecosystem expects them
- setup, focused test, and full validation responsibilities
- CI workflows or documented release gates
- generated-file ignore policy
- release or deployment instructions when artifacts ship

## Missing Best-Practice Files Are Usually Not Blockers

README, CONTRIBUTING, CODEOWNERS, SECURITY.md, issue templates, and PR templates are usually P2/P3 unless the repository is public, installable, regulated, security-sensitive, or critical production infrastructure.

## Severity Guidance

- P0: data loss, destructive workflow, exposed secret, or guaranteed unsafe execution.
- P1: blocks onboarding, prevents all validation, or creates likely shipped breakage.
- P2: materially slows repeated work, hides package boundaries, or leaves validation incomplete.
- P3: useful hardening, polish, or optional community surface.
```

- [ ] **Step 5: Create `ecosystem-index.md`**

Use this content:

```markdown
# Ecosystem Index

Read only the overlays that match the auditor inventory.

| Detection artifact | Overlay |
|---|---|
| package.json -> references/ecosystems/node-typescript.md | Node, TypeScript, JavaScript, package manager scripts, workspaces |
| pnpm-workspace.yaml -> references/ecosystems/node-typescript.md | pnpm workspace roots |
| pyproject.toml -> references/ecosystems/python.md | Python package or app |
| setup.cfg -> references/ecosystems/python.md | Python package |
| setup.py -> references/ecosystems/python.md | Python package |
| requirements.txt -> references/ecosystems/python.md | Python app or script repo |
| go.mod -> references/ecosystems/go.md | Go module |
| Cargo.toml -> references/ecosystems/rust.md | Rust crate or workspace |
| Package.swift -> references/ecosystems/swift-apple.md | SwiftPM package |
| *.xcodeproj -> references/ecosystems/swift-apple.md | Apple app project |
| settings.gradle -> references/ecosystems/jvm-gradle-maven.md | Gradle build |
| build.gradle -> references/ecosystems/jvm-gradle-maven.md | Gradle build |
| pom.xml -> references/ecosystems/jvm-gradle-maven.md | Maven build |
| Gemfile -> references/ecosystems/ruby.md | Ruby app or gem |
| *.gemspec -> references/ecosystems/ruby.md | Ruby gem |
| Dockerfile -> references/ecosystems/docker-services.md | Container/service surface |
| docker-compose.yml -> references/ecosystems/docker-services.md | Local service stack |
| mkdocs.yml -> references/ecosystems/docs-static-sites.md | Docs site |
| docusaurus.config.js -> references/ecosystems/docs-static-sites.md | Docs site |
| SKILL.md -> references/ecosystems/codex-skill-plugin.md | Codex skill |
| agents/openai.yaml -> references/ecosystems/codex-skill-plugin.md | Codex skill metadata |
| main.tf -> references/ecosystems/infra-iac.md | Terraform infrastructure |
| Chart.yaml -> references/ecosystems/infra-iac.md | Helm chart |
```

- [ ] **Step 6: Create ecosystem overlays**

Each overlay must use this structure and concrete ecosystem content:

```markdown
# Python

## Detection Artifacts

- `pyproject.toml`
- `setup.cfg`
- `setup.py`
- `requirements.txt`
- `tox.ini`
- `noxfile.py`

## Common Repo Shapes

- installable library using `src/<package>` and `tests`
- application package with `requirements.txt` or `pyproject.toml`
- script repo with stdlib-only scripts and focused tests

## Required Lifecycle Gates

- setup: `python -m pip install -e .`, `pip install -r requirements.txt`, `uv sync`, or documented equivalent
- focused test: `pytest`, `python -m unittest`, or documented package-specific command
- full validation: test plus lint/typecheck/build commands when configured

## Native Commands

- `python -m pytest`
- `python -m unittest`
- `python -m py_compile`
- `tox`
- `nox`
- `ruff check`
- `mypy`
- `python -m build`

## CI Expectations

CI should run the same focused or full validation gates documented for local use. Matrix testing is expected when the package claims multiple Python versions.

## Lockfile/Toolchain Policy

Libraries may omit lockfiles for runtime dependencies. Applications should document or commit a lock/sync mechanism such as `uv.lock`, `requirements*.txt`, or a tool-specific lockfile.

## Package Boundary Rules

Do not assume the repo root is the Python package root when `pyproject.toml` appears under a nested directory.

## Common False Positives

- Do not require a server command for libraries or script-only packages.
- Do not require both `tox` and `pytest`.

## Severity Guidance

Missing package-specific tests in a Python package is usually P2. Missing setup instructions in an installable public library is P2 or P1 when it blocks onboarding.

## Good Finding Examples

- P2 scoped to `packages/worker`: `pyproject.toml` declares a Python package, but no local or CI test command references that path.

## Bad Finding Examples

- P2 at root: repo lacks `scripts/test.sh` even though `tox` exists and is documented.
```

Create the remaining overlays with the same headings and equivalent concrete bullets:

- `node-typescript.md`: `package.json`, `packageManager`, lockfiles, workspaces, `npm test`, `pnpm -r test`, `lint`, `typecheck`, `build`, `dev`, package filters, false positive for missing root script when workspace scripts exist.
- `go.md`: `go.mod`, `go.sum`, `cmd/`, `internal/`, `go test ./...`, `go vet`, `golangci-lint`, false positive for requiring setup when Go module has no external setup.
- `rust.md`: `Cargo.toml`, `Cargo.lock`, workspaces, `cargo test`, `cargo clippy`, `cargo fmt --check`, `cargo doc`, false positive for requiring `Cargo.lock` in every library context without checking repo policy.
- `swift-apple.md`: `Package.swift`, `Sources`, `Tests`, `swift build`, `swift test`, `.xcodeproj`, `xcodebuild`, Swift format/lint, platform SDK scripts, false positive for requiring `xcodebuild` for pure SwiftPM packages.
- `jvm-gradle-maven.md`: Gradle/Maven wrappers, `settings.gradle`, `build.gradle`, `pom.xml`, `./gradlew test`, `./gradlew check`, `mvn test`, `mvn verify`, false positive for ignoring wrapper scripts.
- `ruby.md`: `Gemfile`, `Gemfile.lock`, `*.gemspec`, `Rakefile`, `bundle exec rake`, `bundle exec rspec`, false positive for requiring npm-style scripts.
- `docs-static-sites.md`: docs config files, docs build/render/link check, publish command, false positive for requiring server/runtime command for static docs.
- `docker-services.md`: `Dockerfile`, compose files, env sample, healthcheck, migration command, local dev stack, integration test command, false positive for requiring compose when single Dockerfile is only release packaging.
- `codex-skill-plugin.md`: source skill, plugin mirror, `SKILL.md`, `agents/openai.yaml`, references, scripts, tests, `quick_validate`, plugin metadata, source/plugin relative path safety, no source-only reference paths, no mirror-only drift.
- `infra-iac.md`: Terraform, Pulumi, Helm, Kubernetes manifests, `terraform fmt -check`, `terraform validate`, chart linting, plan/apply safety, false positive for requiring app server commands.

- [ ] **Step 7: Run reference tests**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py \
  AuditRepositoryHealthTests.test_skill_reference_docs_define_report_contract_and_overlays \
  AuditRepositoryHealthTests.test_ecosystem_overlays_include_required_sections
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add skills/auditing-repository-health/references \
  skills/auditing-repository-health/tests/test_audit_repository_health.py
git commit -m "docs(auditing-repository-health): add repo foundation overlays"
```

---

### Task 4: Update SKILL.md Workflow And Report Contract Routing

**Files:**
- Modify: `skills/auditing-repository-health/SKILL.md`
- Modify: `skills/auditing-repository-health/tests/test_audit_repository_health.py`

**Interfaces:**
- Consumes: `references/report-contract.md`, `references/repo-foundation-rubric.md`, and `references/ecosystem-index.md`.
- Produces: skill workflow that requires classification before recommendations.

- [ ] **Step 1: Write failing SKILL.md tests**

Append:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py \
  AuditRepositoryHealthTests.test_skill_requires_classification_before_recommendations
```

Expected: FAIL because current `SKILL.md` lacks the new routing language.

- [ ] **Step 3: Replace SKILL.md body**

Keep the existing frontmatter name. Update the description to include multi-repo and ecosystem setup triggers without summarizing the workflow:

```yaml
description: Use when auditing repository health, onboarding to a repo, checking multi-repo or monorepo setup, validating language-specific scaffolding, scripts, CI, docs, packaging, mirrors, Git hygiene, generated files, or missing developer lifecycle gates.
```

Use this body structure:

````markdown
# Auditing Repository Health

## Overview

Run a read-only repository health audit before trusting a repo for repeated work. The script is the executable baseline; references provide judgement for repo topology and ecosystem setup.

## Required Workflow

1. Run the bundled auditor first.
2. Read the generated `Repository Inventory` and `Lifecycle Gate Matrix`.
3. Classify the repository before writing findings.
4. Read `references/report-contract.md`.
5. Read `references/repo-foundation-rubric.md` when recommending foundations.
6. Use `references/ecosystem-index.md` to choose only the relevant ecosystem overlays.
7. For monorepos and polyrepos, assess root/shared foundations separately from each package, service, app, docs root, or mirror root.
8. Preserve the existing report sections and add the inventory/classification sections when applicable.
9. Do not prescribe generic boilerplate, generic repo trees, or Scripts-to-Rule-Them-All filenames unless evidence shows that convention already fits the repo.
10. Every finding must name the affected path or scope and cite concrete evidence.

If you cannot identify package boundaries, say so explicitly and avoid package-specific recommendations.

## Run The Audit

From the repository being audited:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/auditing-repository-health/scripts/audit_repository_health.py" --repo "$PWD"
```

From this source checkout:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py --repo "$PWD"
```

For automation:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/auditing-repository-health/scripts/audit_repository_health.py" --repo "$PWD" --format json
```

## Report Contract

Preserve these sections when summarizing:

```md
## Verdict
## Findings
## Repository Shape
## Repository Inventory
## Lifecycle Gate Matrix
## Documentation
## Scripts
## Validation
## Packaging
## Hygiene
## Commands Run
## Not Checked
```

Read `references/report-contract.md` before producing a final audit.

## Reference Routing

- Unclear script responsibility: read `references/script-responsibilities.md`.
- Foundation recommendations: read `references/repo-foundation-rubric.md`.
- Ecosystem-specific setup: read `references/ecosystem-index.md`, then only the matching `references/ecosystems/*.md` overlays.

## Common Mistakes

| Mistake | Correct behavior |
|---|---|
| Listing ideal scripts without running the audit | Run the bundled auditor first, then interpret gaps. |
| Treating root health as package health | Use the inventory and lifecycle matrix to inspect each package/service/docs root. |
| Forcing script filenames | Audit responsibilities and accept repo-native commands. |
| Recommending boilerplate before classification | Classify purpose, ecosystem, package boundaries, and CI coverage first. |
| Dropping `Not Checked` | Preserve skipped areas so readiness is not overstated. |
````

- [ ] **Step 4: Run SKILL.md test**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py \
  AuditRepositoryHealthTests.test_skill_requires_classification_before_recommendations
```

Expected: PASS.

- [ ] **Step 5: Validate skill metadata**

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  skills/auditing-repository-health
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/auditing-repository-health/SKILL.md \
  skills/auditing-repository-health/tests/test_audit_repository_health.py
git commit -m "docs(auditing-repository-health): require repo classification"
```

---

### Task 5: Add Mirror Parity Helper And Sync Plugin Mirror

**Files:**
- Create: `scripts/check_skill_mirror.py`
- Modify: `skills/auditing-repository-health/tests/test_audit_repository_health.py`
- Create/modify mirrored files under `plugins/codex-skills/skills/auditing-repository-health/**`

**Interfaces:**
- Produces command: `python3 scripts/check_skill_mirror.py auditing-repository-health`.
- Later validation uses this command instead of relying only on manual `diff -qr`.

- [ ] **Step 1: Write failing mirror helper test**

Append:

```python
    def test_source_and_plugin_mirror_are_identical(self):
        repo = Path(__file__).resolve().parents[3]
        result = subprocess.run(
            ["python3", "scripts/check_skill_mirror.py", "auditing-repository-health"],
            cwd=repo,
            text=True,
            capture_output=True,
        )
        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("mirror ok: auditing-repository-health", result.stdout)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py \
  AuditRepositoryHealthTests.test_source_and_plugin_mirror_are_identical
```

Expected: FAIL because `scripts/check_skill_mirror.py` does not exist and mirror files are not synced.

- [ ] **Step 3: Create mirror helper**

Create `scripts/check_skill_mirror.py`:

```python
#!/usr/bin/env python3
"""Check source skill and plugin mirror parity."""

from __future__ import annotations

import filecmp
import sys
from pathlib import Path


IGNORED_NAMES = {"__pycache__", ".pytest_cache", ".DS_Store"}


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_NAMES for part in path.parts):
            continue
        if path.is_file():
            files.append(path.relative_to(root))
    return files


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_skill_mirror.py <skill-name>", file=sys.stderr)
        return 2

    skill_name = sys.argv[1]
    repo = Path.cwd()
    source = repo / "skills" / skill_name
    mirror = repo / "plugins" / "codex-skills" / "skills" / skill_name

    if not source.is_dir():
        print(f"missing source skill: {source}", file=sys.stderr)
        return 1
    if not mirror.is_dir():
        print(f"missing plugin mirror: {mirror}", file=sys.stderr)
        return 1

    source_files = set(iter_files(source))
    mirror_files = set(iter_files(mirror))
    failures: list[str] = []

    for path in sorted(source_files - mirror_files):
        failures.append(f"missing from mirror: {path}")
    for path in sorted(mirror_files - source_files):
        failures.append(f"extra in mirror: {path}")
    for path in sorted(source_files & mirror_files):
        if not filecmp.cmp(source / path, mirror / path, shallow=False):
            failures.append(f"content differs: {path}")

    if failures:
        print("\\n".join(failures))
        return 1

    print(f"mirror ok: {skill_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Sync source to mirror**

Copy the source skill into the plugin mirror:

```bash
rsync -a --delete \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  skills/auditing-repository-health/ \
  plugins/codex-skills/skills/auditing-repository-health/
```

- [ ] **Step 5: Run mirror helper**

```bash
python3 scripts/check_skill_mirror.py auditing-repository-health
```

Expected:

```text
mirror ok: auditing-repository-health
```

- [ ] **Step 6: Run source and mirror tests**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py
python3 plugins/codex-skills/skills/auditing-repository-health/tests/test_audit_repository_health.py
```

Expected: both pass.

- [ ] **Step 7: Commit**

```bash
git add scripts/check_skill_mirror.py \
  skills/auditing-repository-health \
  plugins/codex-skills/skills/auditing-repository-health
git commit -m "test(skills): enforce audit skill mirror parity"
```

---

### Task 6: Forward-Test The Updated Skill And Finalize Validation

**Files:**
- Modify: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/BASELINE_NOTES.md`
- Modify: `skills/auditing-repository-health/tests/fixtures/polyglot-monorepo/EXPECTED_AUDIT_CRITERIA.md`
- Modify mirror copies of those fixture files.

**Interfaces:**
- Consumes updated skill and auditor.
- Produces recorded forward-test evidence in fixture notes.

- [ ] **Step 1: Run the updated auditor against the pressure fixture**

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py \
  --repo skills/auditing-repository-health/tests/fixtures/polyglot-monorepo \
  --format json | python3 -m json.tool > /tmp/polyglot-updated.json
```

Expected: PASS and `/tmp/polyglot-updated.json` includes `repository_inventory` and `lifecycle_gate_matrix`.

- [ ] **Step 2: Verify expected criteria manually**

Check:

```bash
python3 - <<'PY'
import json
from pathlib import Path

report = json.loads(Path("/tmp/polyglot-updated.json").read_text())
inventory = report["checks"]["repository_inventory"]
matrix = {row["path"]: row for row in report["checks"]["lifecycle_gate_matrix"]["rows"]}

assert inventory["classification"] == "monorepo"
assert "node" in inventory["ecosystems"]
assert "go" in inventory["ecosystems"]
assert "python" in inventory["ecosystems"]
assert "docker" in inventory["ecosystems"]
assert matrix["packages/worker"]["focused_test"]["status"] == "missing"
assert matrix["packages/api"]["focused_test"]["status"] == "present"
print("polyglot fixture criteria ok")
PY
```

Expected:

```text
polyglot fixture criteria ok
```

- [ ] **Step 3: Update forward-test notes**

Append to `BASELINE_NOTES.md`:

````markdown
## Updated Forward Test

Updated command:

```bash
python3 skills/auditing-repository-health/scripts/audit_repository_health.py --repo skills/auditing-repository-health/tests/fixtures/polyglot-monorepo --format json
```

Observed updated behavior:

- The report emits `repository_inventory`.
- The report classifies the fixture as `monorepo`.
- The report emits package/service/docs boundaries.
- The lifecycle matrix separates root validation from package-specific validation.
- The lifecycle matrix marks `packages/api` test coverage present from CI evidence.
- The lifecycle matrix marks `packages/worker` focused tests missing.
````

- [ ] **Step 4: Sync mirror again**

```bash
rsync -a --delete \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  skills/auditing-repository-health/ \
  plugins/codex-skills/skills/auditing-repository-health/
```

- [ ] **Step 5: Run full validation**

```bash
python3 skills/auditing-repository-health/tests/test_audit_repository_health.py
python3 plugins/codex-skills/skills/auditing-repository-health/tests/test_audit_repository_health.py
python3 -m py_compile skills/auditing-repository-health/scripts/audit_repository_health.py
python3 -m py_compile plugins/codex-skills/skills/auditing-repository-health/scripts/audit_repository_health.py
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/auditing-repository-health
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/codex-skills/skills/auditing-repository-health
python3 scripts/check_skill_mirror.py auditing-repository-health
bash scripts/test_install.sh
git diff --check
git status --short
```

Expected: all commands pass. `git status --short` shows only intended source, mirror, fixture, helper, and plan files until committed.

- [ ] **Step 6: Run autoreview if executable behavior changed**

Because Task 2 changes `audit_repository_health.py`, run:

```bash
autoreview --mode local
```

Expected: no accepted in-scope findings remain. If it reports in-scope issues, fix narrowly, rerun relevant tests, and rerun autoreview. Stop after four autoreview loops.

- [ ] **Step 7: Commit final validation notes and mirror sync**

```bash
git add skills/auditing-repository-health \
  plugins/codex-skills/skills/auditing-repository-health \
  scripts/check_skill_mirror.py
git commit -m "test(auditing-repository-health): record polyglot forward test"
```

---

## Self-Review Checklist

- Spec coverage: the plan covers deeper repo setup research, multi-repo topology, ecosystem overlays, scripts/CI guidance, boilerplate judgement, skill TDD, source/plugin mirroring, and validation.
- Vague-text scan: do not leave unresolved markers or ambiguous edge-case language during implementation.
- Type consistency: use `repository_inventory`, `lifecycle_gate_matrix`, `classification`, `ecosystems`, `boundaries`, and `suggested_overlays` exactly as named here.
- Scope control: do not add destructive repo mutations, dependency installs, network calls, or unrelated cleanup.
- Forward-test integrity: record baseline behavior before changing the skill and updated behavior after changing it.
