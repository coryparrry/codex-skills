### Task 3: Verify Skill Installation And Template Validity

**Files:**
- Check: `~/.codex/skills/Knowledge-setup/SKILL.md`
- Check: `~/.codex/skills/Knowledge-setup/templates/AGENTS.md`
- Check: `~/.codex/skills/Knowledge-setup/templates/context.md`
- Check: `~/.codex/skills/Knowledge-setup/templates/graph.json`

**Interfaces:**
- Consumes: skill and templates from Tasks 1 and 2.
- Produces: a locally installed skill ready to invoke.

- [ ] **Step 1: Check files exist**

```bash
test -s "$HOME/.codex/skills/Knowledge-setup/SKILL.md"
test -s "$HOME/.codex/skills/Knowledge-setup/templates/AGENTS.md"
test -s "$HOME/.codex/skills/Knowledge-setup/templates/context.md"
test -s "$HOME/.codex/skills/Knowledge-setup/templates/graph.json"
```

Expected: All four files exist and are non-empty.

- [ ] **Step 2: Check skill frontmatter**

```bash
sed -n '1,12p' "$HOME/.codex/skills/Knowledge-setup/SKILL.md"
```

Expected: The first lines include `name: Knowledge-setup` and a concise `description`.

- [ ] **Step 3: Check template JSON**

```bash
python3 -m json.tool "$HOME/.codex/skills/Knowledge-setup/templates/graph.json" >/dev/null
```

Expected: The graph template parses as JSON.

- [ ] **Step 4: Check no actual home path leaked into skill content**

```bash
python3 - <<'PY'
from pathlib import Path

skill_dir = Path.home() / ".codex" / "skills" / "Knowledge-setup"
home = str(Path.home())
leaks = []

for path in skill_dir.rglob("*"):
    if path.is_file():
        text = path.read_text(errors="ignore")
        if home in text:
            leaks.append(path)

if leaks:
    for path in leaks:
        print(f"Home path leaked into skill content: {path}")
    raise SystemExit(1)
PY
```

Expected: The user's actual home path does not appear in the skill or templates.
