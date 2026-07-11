# Simplify Knowledge Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the repository context skill safer and simpler without expanding its three-file output.

**Architecture:** Keep `AGENTS.md`, `.repo/context.md`, and `.repo/graph.json` as the complete target surface. Shorten the skill by routing detailed starter content through templates, merge the router into existing instructions, and make graph nodes and edges optional behind routes-first navigation.

**Tech Stack:** Markdown, JSON, YAML, Python 3 validation, shell smoke tests.

## Global Constraints

- Ship the skill as lowercase `knowledge-setup` in both source and plugin mirror surfaces.
- Preserve verified existing `AGENTS.md` instructions instead of replacing them.
- Keep commands and routes primary; add nodes and edges only when they improve navigation.
- Do not add dependencies, generators, databases, services, or committed validation tooling.
- Do not rewrite the historical implementation plan; it remains evidence of the original delivery.

---

### Task 1: Rename and simplify the skill

**Files:**
- Rename: `skills/Knowledge-setup/` to `skills/knowledge-setup/`
- Modify: `skills/knowledge-setup/SKILL.md`
- Modify: `skills/knowledge-setup/agents/openai.yaml`
- Modify: `skills/knowledge-setup/templates/AGENTS.md`
- Modify: `skills/knowledge-setup/templates/context.md`
- Modify: `skills/knowledge-setup/templates/graph.json`

**Interfaces:**
- Consumes: the existing three-file repository context contract.
- Produces: the `$knowledge-setup` trigger and routes-first graph guidance.

- [ ] **Step 1: Record the failing baseline**

Run five fresh pressure samples against the current skill.

Expected: samples choose full `AGENTS.md` replacement and treat nodes as required whenever routes use `start_nodes`.

- [ ] **Step 2: Rename the source directory and trigger**

Rename the skill directory and update frontmatter, the manual trigger, agent metadata, and template trigger references to `knowledge-setup`.

- [ ] **Step 3: Write the minimal guidance**

Keep the workflow in `SKILL.md`; refer to the three templates for reusable content. State the positive contracts explicitly:

```text
Existing AGENTS.md = verified instructions retained + context-layer router reconciled in place.
Small graph = verified commands + inspect_first routes + empty nodes/edges when deeper semantics add no value.
```

- [ ] **Step 4: Verify focused structure**

Run:

```bash
python3 -m json.tool skills/knowledge-setup/templates/graph.json >/dev/null
plugin-eval analyze skills/knowledge-setup --format markdown
```

Expected: valid JSON, lowercase-name check passes, trigger description check passes, and invocation cost is lower than the baseline.

- [ ] **Step 5: Commit**

```bash
git add skills/Knowledge-setup skills/knowledge-setup docs/superpowers/specs/2026-07-05-knowledge-setup-design.md docs/superpowers/plans/2026-07-09-simplify-knowledge-setup.md
git commit -m "refactor(knowledge-setup): simplify context routing"
```

### Task 2: Synchronize, test, and review the shipped mirror

**Files:**
- Rename: `plugins/codex-skills/skills/Knowledge-setup/` to `plugins/codex-skills/skills/knowledge-setup/`
- Modify: `scripts/test_install.sh`

**Interfaces:**
- Consumes: the completed source skill from Task 1.
- Produces: an identical marketplace mirror and installer proof for the lowercase skill.

- [ ] **Step 1: Mirror the source skill**

Copy the completed source skill directory exactly into the plugin skill surface under the lowercase name.

- [ ] **Step 2: Add installer assertions**

Extend the install smoke test with exact assertions for:

```text
skills/knowledge-setup/SKILL.md
skills/knowledge-setup/agents/openai.yaml
skills/knowledge-setup/templates/AGENTS.md
skills/knowledge-setup/templates/context.md
skills/knowledge-setup/templates/graph.json
```

- [ ] **Step 3: Run GREEN pressure samples**

Run five fresh samples against the revised skill.

Expected: all preserve verified existing instructions and allow routes without populated nodes or edges for the small-repo scenario.

- [ ] **Step 4: Run repository validation**

Run:

```bash
python3 scripts/check_skill_mirror.py knowledge-setup
bash scripts/test_install.sh
python3 -m json.tool skills.sh.json >/dev/null
git diff --check
```

Expected: every command exits zero.

- [ ] **Step 5: Review and commit**

Run the required skill review workflow, fix accepted in-scope findings, then commit the synchronized milestone.

```bash
git add plugins/codex-skills/skills/Knowledge-setup plugins/codex-skills/skills/knowledge-setup scripts/test_install.sh
git commit -m "test(knowledge-setup): cover lowercase skill install"
```
